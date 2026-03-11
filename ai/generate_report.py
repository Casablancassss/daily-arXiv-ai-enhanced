#!/usr/bin/env python3
"""
Generate a daily paper recommendation report with top relevant papers.
Outputs to console or can be configured to send via Slack/Email.
"""

import os
import json
import sys
import argparse
from typing import List, Dict, Optional

import dotenv

# Load environment variables
if os.path.exists('.env'):
    dotenv.load_dotenv()


def load_papers(data_file: str, top_n: int = 5) -> List[Dict]:
    """Load papers and sort by relevance score"""
    papers = []

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        paper = json.loads(line)
                        score = paper.get('relevance_score')
                        # Handle None or non-numeric values
                        if score is not None and isinstance(score, (int, float)) and score > 0:
                            papers.append(paper)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Skipping malformed JSON at line {line_num}: {e}", file=sys.stderr)
                        continue
    except FileNotFoundError:
        print(f"Error: File not found: {data_file}", file=sys.stderr)
        return []
    except OSError as e:
        print(f"Error reading file {data_file}: {e}", file=sys.stderr)
        return []

    # Sort by relevance score (descending)
    papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    return papers[:top_n]


def normalize_score(score: float) -> int:
    """
    Normalize relevance score to 0-100 percentage.
    - 0-1 range: multiply by 100
    - 0-10 range: multiply by 10
    - 0-100 range: use as-is
    """
    if score <= 1:
        # Assume 0-1 range (including 1 -> 100%)
        normalized = score * 100
    elif score <= 10:
        # Assume 0-10 range
        normalized = score * 10
    else:
        # Assume 0-100 range (percentage)
        normalized = score

    # Clamp to 0-100
    return max(0, min(100, int(normalized)))


def format_paper(paper: Dict, index: int) -> str:
    """Format a single paper for the report"""
    score = paper.get('relevance_score', 0)
    # Normalize score to percentage
    score_display = f"{normalize_score(score)}%"

    title = paper.get('title', 'Untitled')
    authors = paper.get('authors', [])
    if isinstance(authors, list):
        authors = ', '.join(authors[:3])  # Limit to first 3 authors
    else:
        authors = str(authors)[:100]

    # Get AI summary - fall back to summary if tldr is empty/None
    ai = paper.get('AI', {})
    tldr = ai.get('tldr') or paper.get('summary', '')
    tldr = tldr[:300] if tldr else ''

    url = paper.get('abs', paper.get('url', ''))

    return f"""
## 📄 Paper {index} - Relevance: {score_display}
**Title:** {title}
**Authors:** {authors}
**arXiv:** {url}

**TL;DR:** {tldr}
"""


def generate_report(
    data_file: str,
    top_n: int = 5,
    research_profile: Optional[Dict] = None
) -> str:
    """Generate the daily report"""

    papers = load_papers(data_file, top_n)

    if not papers:
        return "No relevant papers found for your research profile."

    # Build header
    header = f"""# 📊 Daily arXiv Paper Recommendations

"""

    if research_profile:
        # Safely handle methods and pain_points
        methods = research_profile.get('methods', [])
        if not isinstance(methods, (list, tuple)):
            methods = [methods] if methods else []

        pain_points = research_profile.get('pain_points', [])
        if not isinstance(pain_points, (list, tuple)):
            pain_points = [pain_points] if pain_points else []

        header += f"""**Research Profile:**
- Field: {research_profile.get('field', 'N/A')}
- Methods: {', '.join(map(str, methods))}
- Pain Points: {', '.join(map(str, pain_points))}

"""

    header += f"""**Top {len(papers)} Most Relevant Papers:**

"""

    # Build paper sections
    papers_content = []
    for i, paper in enumerate(papers, 1):
        papers_content.append(format_paper(paper, i))

    return header + '\n'.join(papers_content)


def main():
    parser = argparse.ArgumentParser(description="Generate daily paper recommendation report")
    parser.add_argument("--data", type=str, required=True, help="JSONL data file")
    parser.add_argument("--top", type=int, default=5, help="Number of top papers to include")
    parser.add_argument("--output", type=str, default=None, help="Output file (default: print to stdout)")
    args = parser.parse_args()

    # Load research profile
    profile_str = os.environ.get('RESEARCH_PROFILE', '')
    research_profile = None
    if profile_str:
        try:
            research_profile = json.loads(profile_str)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to parse RESEARCH_PROFILE: {e}", file=sys.stderr)
            print(f"Raw profile: {profile_str[:100]}...", file=sys.stderr)
            print("Please check your RESEARCH_PROFILE JSON format", file=sys.stderr)

    # Fallback: read from individual environment variables
    if not research_profile:
        field = os.environ.get('RESEARCH_FIELD', '')
        pain_points = os.environ.get('RESEARCH_PAIN_POINTS', '')
        methods = os.environ.get('RESEARCH_METHODS', '')

        if field or pain_points or methods:
            research_profile = {}
            if field:
                research_profile['field'] = field
            if pain_points:
                research_profile['pain_points'] = [p.strip() for p in pain_points.split(',') if p.strip()]
            if methods:
                research_profile['methods'] = [m.strip() for m in methods.split(',') if m.strip()]

    # Generate report
    report = generate_report(
        args.data,
        args.top,
        research_profile
    )

    # Output
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        except OSError as e:
            print(f"Error writing to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(report)


if __name__ == "__main__":
    main()
