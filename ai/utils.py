#!/usr/bin/env python3
"""
Shared utility functions for the daily arXiv project.
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, List


def load_research_profile(profile_str: str = None) -> Optional[Dict]:
    """
    Load research profile from JSON string or individual environment variables.

    Priority:
    1. JSON string passed as argument
    2. RESEARCH_PROFILE environment variable (JSON string)
    3. Individual environment variables (RESEARCH_FIELD, RESEARCH_PAIN_POINTS, RESEARCH_METHODS)

    Args:
        profile_str: Optional JSON string of research profile

    Returns:
        Dictionary containing research profile or None if not found
    """
    # Try JSON string first
    if profile_str:
        try:
            return json.loads(profile_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse RESEARCH_PROFILE as JSON: {e}", file=sys.stderr)

    # Try environment variable
    profile_str = os.environ.get('RESEARCH_PROFILE', '')
    if profile_str:
        try:
            return json.loads(profile_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse RESEARCH_PROFILE as JSON: {e}", file=sys.stderr)

    # Fallback: read from individual environment variables
    field = os.environ.get('RESEARCH_FIELD', '')
    pain_points = os.environ.get('RESEARCH_PAIN_POINTS', '')
    methods = os.environ.get('RESEARCH_METHODS', '')

    if field or pain_points or methods:
        profile = {}
        if field:
            profile['field'] = field
        if pain_points:
            # Split by comma if multiple values
            profile['pain_points'] = [p.strip() for p in pain_points.split(',') if p.strip()]
        if methods:
            # Split by comma if multiple values
            profile['methods'] = [m.strip() for m in methods.split(',') if m.strip()]
        return profile if profile else None

    return None


def get_sensitive_check_url() -> str:
    """
    Get the sensitive content check URL from environment variable.
    Falls back to a default value if not set.

    Returns:
        URL string for sensitive content check API
    """
    return os.environ.get('SENSITIVE_CHECK_URL', 'https://spam.dw-dengwei.workers.dev')


def read_template_file(filename: str, default_dir: str = None) -> str:
    """
    Safely read a template file from the project directory.

    Args:
        filename: Name of the template file
        default_dir: Optional directory to search in (defaults to project root)

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file cannot be found
    """
    if default_dir is None:
        # Try multiple locations
        possible_paths = [
            Path(filename),
            Path(__file__).parent.parent / filename,
            Path.cwd() / filename,
        ]
    else:
        possible_paths = [Path(default_dir) / filename]

    for path in possible_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

    raise FileNotFoundError(f"Template file '{filename}' not found in any of: {[str(p) for p in possible_paths]}")
