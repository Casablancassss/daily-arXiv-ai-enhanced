import os
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import requests

import dotenv
import argparse
from tqdm import tqdm

import langchain_core.exceptions
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from structure import Structure

# Use shared utilities - support both module import and direct script execution
try:
    from utils import load_research_profile, get_sensitive_check_url, read_template_file
except ModuleNotFoundError:
    from ai.utils import load_research_profile, get_sensitive_check_url, read_template_file

if os.path.exists('.env'):
    dotenv.load_dotenv()

# Safely read template files
try:
    template = read_template_file("ai/template.txt")
    system = read_template_file("ai/system.txt")
except FileNotFoundError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

def calculate_relevance_score(item: Dict, profile: Dict) -> float:
    """
    根据研究画像计算论文的相关性分数

    评分规则：
    - field 匹配 (权重 1.0)：在标题、摘要、AI分析的tldr/motivation中匹配研究方向
    - pain_points 匹配 (权重 1.5)：匹配当前痛点
    - methods 匹配 (权重 2.0)：在AI分析的method/result中匹配关注方法
    """
    if not profile:
        return 0.0

    score = 0.0
    field = profile.get('field', '')
    pain_points = profile.get('pain_points', [])
    methods = profile.get('methods', [])

    # 获取论文的文本内容
    text_content = ' '.join([
        item.get('title', ''),
        item.get('summary', ''),
        item.get('AI', {}).get('tldr', ''),
        item.get('AI', {}).get('motivation', '')
    ]).lower()

    method_content = ' '.join([
        item.get('AI', {}).get('method', ''),
        item.get('AI', {}).get('result', '')
    ]).lower()

    # field 匹配 (权重 1.0)
    if field:
        field_lower = field.lower()
        if field_lower in text_content:
            score += 1.0

    # pain_points 匹配 (权重 1.5)
    for pp in pain_points:
        pp_lower = pp.lower()
        if pp_lower in text_content:
            score += 1.5

    # methods 匹配 (权重 2.0)
    for method in methods:
        method_lower = method.lower()
        if method_lower in method_content:
            score += 2.0

    return score

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="jsonline data file")
    parser.add_argument("--max_workers", type=int, default=1, help="Maximum number of parallel workers")
    return parser.parse_args()

def process_single_item(chain, item: Dict, language: str) -> Dict:
    def is_sensitive(content: str) -> bool:
        """
        调用敏感词检测接口检测内容是否包含敏感词。
        使用 SENSITIVE_CHECK_URL 环境变量配置接口地址。
        返回 True 表示触发敏感词，False 表示未触发。
        """
        try:
            resp = requests.post(
                get_sensitive_check_url(),
                json={"text": content},
                timeout=5
            )
            if resp.status_code == 200:
                result = resp.json()
                # 约定接口返回 {"sensitive": true/false, ...}
                return result.get("sensitive", True)
            else:
                # 如果接口异常，默认不触发敏感词
                print(f"Sensitive check failed with status {resp.status_code}", file=sys.stderr)
                return True
        except Exception as e:
            print(f"Sensitive check error: {e}", file=sys.stderr)
            return True

    # 检查 summary 字段
    if is_sensitive(item.get("summary", "")):
        return None

    """处理单个数据项"""
    # Default structure with meaningful fallback values
    default_ai_fields = {
        "tldr": "Summary generation failed",
        "motivation": "Motivation analysis unavailable",
        "method": "Method extraction failed",
        "result": "Result analysis unavailable",
        "conclusion": "Conclusion extraction failed"
    }
    
    try:
        response: Structure = chain.invoke({
            "language": language,
            "content": item['summary']
        })
        item['AI'] = response.model_dump()
    except langchain_core.exceptions.OutputParserException as e:
        # 尝试从错误信息中提取 JSON 字符串并修复
        error_msg = str(e)
        partial_data = {}
        
        if "Function Structure arguments:" in error_msg:
            try:
                # 提取 JSON 字符串
                json_str = error_msg.split("Function Structure arguments:", 1)[1].strip().split('are not valid JSON')[0].strip()
                # 预处理 LaTeX 数学符号 - 使用四个反斜杠来确保正确转义
                json_str = json_str.replace('\\', '\\\\')
                # 尝试解析修复后的 JSON
                partial_data = json.loads(json_str)
            except Exception as json_e:
                print(f"Failed to parse JSON for {item.get('id', 'unknown')}: {json_e}", file=sys.stderr)
        
        # Merge partial data with defaults to ensure all fields exist
        item['AI'] = {**default_ai_fields, **partial_data}
        print(f"Using partial AI data for {item.get('id', 'unknown')}: {list(partial_data.keys())}", file=sys.stderr)
    except Exception as e:
        # Catch any other exceptions and provide default values
        print(f"Unexpected error for {item.get('id', 'unknown')}: {e}", file=sys.stderr)
        item['AI'] = default_ai_fields
    
    # Final validation to ensure all required fields exist
    for field in default_ai_fields.keys():
        if field not in item['AI']:
            item['AI'][field] = default_ai_fields[field]

    # 检查 AI 生成的所有字段
    for v in item.get("AI", {}).values():
        if is_sensitive(str(v)):
            return None
    return item

def process_all_items(data: List[Dict], model_name: str, language: str, max_workers: int) -> List[Dict]:
    """并行处理所有数据项"""
    llm = ChatOpenAI(model=model_name).with_structured_output(Structure, method="function_calling")
    print('Connect to:', model_name, file=sys.stderr)
    
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system),
        HumanMessagePromptTemplate.from_template(template=template)
    ])

    chain = prompt_template | llm
    
    # 使用线程池并行处理
    processed_data = [None] * len(data)  # 预分配结果列表
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_idx = {
            executor.submit(process_single_item, chain, item, language): idx
            for idx, item in enumerate(data)
        }
        
        # 使用tqdm显示进度
        for future in tqdm(
            as_completed(future_to_idx),
            total=len(data),
            desc="Processing items"
        ):
            idx = future_to_idx[future]
            try:
                result = future.result()
                processed_data[idx] = result
            except Exception as e:
                print(f"Item at index {idx} generated an exception: {e}", file=sys.stderr)
                # Add default AI fields to ensure consistency
                processed_data[idx] = data[idx]
                processed_data[idx]['AI'] = {
                    "tldr": "Processing failed",
                    "motivation": "Processing failed",
                    "method": "Processing failed",
                    "result": "Processing failed",
                    "conclusion": "Processing failed"
                }
    
    return processed_data

def main():
    args = parse_args()
    model_name = os.environ.get("MODEL_NAME", 'deepseek-chat')
    language = os.environ.get("LANGUAGE", 'Chinese')

    # 使用共享工具加载研究画像配置
    research_profile = load_research_profile()
    if research_profile:
        print(f'Research profile loaded: {research_profile}', file=sys.stderr)

    # 检查并删除目标文件
    target_file = args.data.replace('.jsonl', f'_AI_enhanced_{language}.jsonl')
    if os.path.exists(target_file):
        os.remove(target_file)
        print(f'Removed existing file: {target_file}', file=sys.stderr)

    # 读取数据
    data = []
    with open(args.data, "r") as f:
        for line in f:
            data.append(json.loads(line))

    # 去重 - 安全处理可能为 None 或缺少 id 字段的 item
    seen_ids = set()
    unique_data = []
    for item in data:
        if item is None:
            continue
        item_id = item.get('id')
        if item_id and item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_data.append(item)

    data = unique_data
    print('Open:', args.data, file=sys.stderr)
    
    # 并行处理所有数据
    processed_data = process_all_items(
        data,
        model_name,
        language,
        args.max_workers
    )
    
    # 计算相关性分数
    if research_profile:
        for item in processed_data:
            if item is not None:
                item['relevance_score'] = calculate_relevance_score(item, research_profile)
        print(f'Calculated relevance scores for {len(processed_data)} papers', file=sys.stderr)

    # 保存结果
    with open(target_file, "w", encoding="utf-8") as f:
        for item in processed_data:
            if item is not None:
                f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    main()
