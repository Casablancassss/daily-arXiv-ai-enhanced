#!/usr/bin/env python3
"""
Research Profile Auto-Parser

This script parses user research descriptions into structured research profiles
using LLM. It supports both CLI and API usage.
"""

import os
import json
import sys
import argparse
from typing import Dict, Optional

import dotenv

# Use shared utilities - support both module import and direct script execution
try:
    from structure import ResearchProfile
except ModuleNotFoundError:
    from ai.structure import ResearchProfile

from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# Load environment variables
if os.path.exists('.env'):
    dotenv.load_dotenv()


# Prompt for parsing research profile
PROFILE_PARSE_SYSTEM_PROMPT = """你是一个专业的学术研究顾问。你的任务是从用户的研究描述中提取结构化的研究画像。

## 输出要求

请从以下维度分析用户的研究描述：

### 1. field (研究领域)
- 主要研究方向（用英文命名，如 Computer Vision, Machine Learning）
- 核心关键词

### 2. pain_points (研究痛点)
- 当前面临的技术挑战
- 想要解决的具体问题
- 现有方法的局限性

### 3. methods (研究方法)
- 使用的主要技术/模型
- 实验方法
- 相关的工具和框架

### 4. keywords (扩展关键词)
- 相关的技术术语
- 重要概念

请确保：
1. 使用英文描述研究领域和技术术语
2. pain_points 应该描述具体的技术问题，而非泛泛而谈
3. methods 应该包含具体的技术名称（如 diffusion models, LoRA, Transformer）
4. keywords 至少包含 3 个相关技术术语
"""

PROFILE_PARSE_HUMAN_PROMPT = """用户的研究描述：
{research_description}

请提取结构化的研究画像，返回 JSON 格式：
{{
  "field": "主要研究领域",
  "field_keywords": ["相关关键词"],
  "pain_points": ["痛点1", "痛点2"],
  "methods": ["方法1", "方法2"],
  "keywords": ["扩展关键词1", "扩展关键词2"]
}}
"""


def parse_research_profile(research_description: str, model_name: str = None) -> Optional[Dict]:
    """
    Parse research description into structured profile using LLM.

    Args:
        research_description: User's research description text
        model_name: Optional model name to use (defaults to MODEL_NAME env var)

    Returns:
        Dictionary containing structured research profile or None on failure
    """
    if not research_description or not research_description.strip():
        print("Error: Research description cannot be empty", file=sys.stderr)
        return None

    if model_name is None:
        model_name = os.environ.get("MODEL_NAME", 'deepseek-chat')

    llm = ChatOpenAI(model=model_name).with_structured_output(
        ResearchProfile,
        method="function_calling"
    )

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(PROFILE_PARSE_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(template=PROFILE_PARSE_HUMAN_PROMPT)
    ])

    chain = prompt_template | llm

    try:
        response = chain.invoke({
            "research_description": research_description
        })

        if hasattr(response, 'model_dump'):
            return response.model_dump()
        else:
            return dict(response)

    except Exception as e:
        print(f"Error parsing research profile: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Research Profile Auto-Parser - Parse research descriptions into structured profiles"
    )
    parser.add_argument(
        "--description", "-d",
        type=str,
        required=True,
        help="Research description text to parse"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Model name to use (defaults to MODEL_NAME env var)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        help="Pretty print JSON output"
    )

    args = parser.parse_args()

    # Parse research profile
    profile = parse_research_profile(args.description, args.model)

    if profile is None:
        print("Failed to parse research profile", file=sys.stderr)
        sys.exit(1)

    # Output result
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2 if args.pretty else None)
        print(f"Profile saved to: {args.output}", file=sys.stderr)
    else:
        if args.pretty:
            print(json.dumps(profile, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(profile, ensure_ascii=False))


if __name__ == "__main__":
    main()
