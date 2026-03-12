#!/usr/bin/env python3
"""
LLM-based Research Paper Relevance Scorer

This script uses LLM to calculate relevance scores between papers and research profile.
It evaluates the relevance as a percentage (0-100%).
"""

import os
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from tqdm import tqdm

import requests
import dotenv
import argparse
from langchain_core.exceptions import OutputParserException
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from pydantic import BaseModel, Field

# Load environment variables
if os.path.exists('.env'):
    dotenv.load_dotenv()

# Use shared utilities - support both module import and direct script execution
try:
    from utils import load_research_profile
except ModuleNotFoundError:
    from ai.utils import load_research_profile


class RelevanceScore(BaseModel):
    """LLM output structure for relevance scoring"""
    relevance_score: int = Field(description="Relevance score from 0 to 100", ge=0, le=100)
    reason: str = Field(description="Brief reason for the score")


# Scoring prompt
SCORING_SYSTEM_PROMPT = """You are an expert research paper evaluator. Your task is to evaluate how relevant a research paper is to a given research profile.

CRITICAL: You must distinguish between APPLICATION DOMAIN and METHOD:
- Using the same method (e.g., diffusion models) in DIFFERENT application domains (image generation vs human motion generation) should be considered DIFFERENT
- Robot motion generation is NOT the same as human motion generation
- Medical image generation is NOT the same as human motion generation

Evaluation criteria (in order of importance):
1. APPLICATION DOMAIN MATCH: Does the paper's application domain match the research field? (Most Important)
2. Whether the paper addresses the pain points
3. Whether the paper uses the EXACT same methods in the SAME application domain
4. The overall fit for someone working in this research area

Provide a score from 0 to 100 where:
- 0-20: Completely irrelevant (different field and application entirely)
- 21-40: Uses similar methods but wrong application domain (e.g., diffusion for image generation when you need human motion generation)
- 41-60: Moderately relevant (same general area)
- 61-80: Highly relevant (same application domain and methods)
- 81-100: Extremely relevant (directly addresses research profile with exact domain match)"""

SCORING_HUMAN_PROMPT = """Research Profile:
- Field: {field}
- Pain Points: {pain_points}
- Methods: {methods}

Paper Information:
- Title: {title}
- TLDR: {tldr}
- Motivation: {motivation}
- Method: {method}
- Result: {result}

IMPORTANT: Consider if this paper is about {field} specifically. A paper about "diffusion for image generation" should get LOW score if you need "diffusion for human motion generation" because the application domain is DIFFERENT.

Evaluate the relevance and provide a score (0-100) with a brief reason."""


def calculate_relevance_with_llm(
    llm: ChatOpenAI,
    chain: ChatPromptTemplate,
    item: Dict,
    profile: Dict
) -> Dict:
    """Use LLM to calculate relevance score for a single paper"""
    try:
        # Prepare paper information
        title = item.get('title', '')
        ai = item.get('AI', {})
        tldr = ai.get('tldr', '')
        motivation = ai.get('motivation', '')
        method = ai.get('method', '')
        result = ai.get('result', '')

        # Prepare profile information
        field = profile.get('field', '')
        pain_points = profile.get('pain_points', [])
        methods = profile.get('methods', [])

        # Call LLM
        response = chain.invoke({
            "field": field,
            "pain_points": ", ".join(pain_points) if pain_points else "None",
            "methods": ", ".join(methods) if methods else "None",
            "title": title,
            "tldr": tldr,
            "motivation": motivation,
            "method": method,
            "result": result
        })

        # Extract score
        if hasattr(response, 'relevance_score'):
            score = response.relevance_score
        else:
            score = response.model_dump().get('relevance_score', 0)

        # Ensure score is in valid range
        score = max(0, min(100, score))

        # Add to item
        item['relevance_score'] = score

        # Add reason if available
        if hasattr(response, 'reason'):
            item['relevance_reason'] = response.reason
        elif hasattr(response, 'model_dump'):
            item['relevance_reason'] = response.model_dump().get('reason', '')

        return item

    except OutputParserException as e:
        print(f"Output parsing error for {item.get('id', 'unknown')}: {e}", file=sys.stderr)
        item['relevance_score'] = 0
        item['relevance_reason'] = 'Scoring failed'
        return item
    except Exception as e:
        print(f"Error scoring {item.get('id', 'unknown')}: {e}", file=sys.stderr)
        item['relevance_score'] = 0
        item['relevance_reason'] = 'Scoring failed'
        return item


def process_all_items(
    data: List[Dict],
    profile: Dict,
    model_name: str,
    max_workers: int
) -> List[Dict]:
    """Process all items with LLM-based scoring"""
    # Request delay in seconds, default 5.0
    try:
        request_delay = float(os.environ.get("REQUEST_DELAY", 5))
    except (ValueError, TypeError):
        request_delay = 5.0

    llm = ChatOpenAI(model=model_name).with_structured_output(
        RelevanceScore,
        method="function_calling"
    )
    print(f'Connecting to: {model_name}', file=sys.stderr)

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SCORING_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(template=SCORING_HUMAN_PROMPT)
    ])

    chain = prompt_template | llm

    # Process with thread pool
    processed_data = [None] * len(data)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {}

        for idx, item in enumerate(data):
            # Rate limit: sleep before submitting each request
            if request_delay > 0 and idx > 0:
                time.sleep(request_delay)
            future = executor.submit(calculate_relevance_with_llm, llm, chain, item, profile)
            future_to_idx[future] = idx

        for future in tqdm(
            as_completed(future_to_idx),
            total=len(data),
            desc="Scoring papers"
        ):
            idx = future_to_idx[future]
            try:
                result = future.result()
                processed_data[idx] = result
            except Exception as e:
                print(f"Exception at index {idx}: {e}", file=sys.stderr)
                # Create a copy to avoid mutating original data
                processed_data[idx] = dict(data[idx])
                processed_data[idx]['relevance_score'] = 0
                processed_data[idx]['relevance_reason'] = 'Scoring failed'

    return processed_data


def main():
    parser = argparse.ArgumentParser(description="LLM-based paper relevance scorer")
    parser.add_argument("--data", type=str, required=True, help="JSONL data file (AI enhanced)")
    parser.add_argument("--profile", type=str, default="", help="Research profile JSON string")
    parser.add_argument("--max_workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--output", type=str, default=None, help="Output file (default: <input>.scored)")
    args = parser.parse_args()

    model_name = os.environ.get("MODEL_NAME", 'deepseek-chat')

    # Load research profile
    profile_str = args.profile or os.environ.get('RESEARCH_PROFILE', '')
    profile = load_research_profile(profile_str)

    if not profile:
        print("No research profile provided. Use --profile or set RESEARCH_PROFILE environment variable.", file=sys.stderr)
        sys.exit(1)

    print(f"Research profile: {profile}", file=sys.stderr)

    # Determine output file
    output_file = args.output
    if not output_file:
        input_file = args.data
        # Insert '.scored' before the extension
        if input_file.endswith('.jsonl'):
            output_file = input_file.replace('.jsonl', '.scored.jsonl')
        else:
            output_file = input_file + '.scored.jsonl'

    # Read data
    data = []
    try:
        with open(args.data, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Skipping malformed JSON at line {line_num}: {e}", file=sys.stderr)
                        continue
    except FileNotFoundError:
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file {args.data}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(data)} papers from {args.data}", file=sys.stderr)

    # Process with LLM
    processed_data = process_all_items(
        data,
        profile,
        model_name,
        args.max_workers
    )

    # Save results
    with open(output_file, "w", encoding="utf-8") as f:
        for item in processed_data:
            if item is not None:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Print statistics
    scores = [item.get('relevance_score', 0) for item in processed_data if item]
    if scores:
        avg_score = sum(scores) / len(scores)
        high_relevance = sum(1 for s in scores if s >= 60)
        print(f"\nScoring complete!", file=sys.stderr)
        print(f"  Total papers: {len(scores)}", file=sys.stderr)
        print(f"  Average score: {avg_score:.1f}%", file=sys.stderr)
        print(f"  Highly relevant (>=60%): {high_relevance}", file=sys.stderr)
        print(f"  Output: {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
