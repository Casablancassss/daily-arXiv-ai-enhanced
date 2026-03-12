"""Tests for ai/structure.py"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import ValidationError
from ai.structure import Structure


class TestStructure:
    """Tests for Structure pydantic model"""

    def test_valid_structure(self):
        """Test valid data creates model correctly"""
        data = {
            'tldr': 'This is a TLDR',
            'motivation': 'This is motivation',
            'method': 'This is the method',
            'result': 'These are the results',
            'conclusion': 'This is the conclusion'
        }
        structure = Structure(**data)
        assert structure.tldr == 'This is a TLDR'
        assert structure.motivation == 'This is motivation'
        assert structure.method == 'This is the method'
        assert structure.result == 'These are the results'
        assert structure.conclusion == 'This is the conclusion'

    def test_missing_field(self):
        """Test missing field raises ValidationError"""
        data = {
            'tldr': 'TLDR',
            'motivation': 'Motivation',
            'method': 'Method',
            'result': 'Result'
            # Missing 'conclusion'
        }
        try:
            Structure(**data)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert len(e.errors()) == 1
            assert e.errors()[0]['loc'] == ('conclusion',)

    def test_empty_fields(self):
        """Test empty strings are valid"""
        data = {
            'tldr': '',
            'motivation': '',
            'method': '',
            'result': '',
            'conclusion': ''
        }
        structure = Structure(**data)
        assert structure.tldr == ''
        assert structure.motivation == ''

    def test_long_text(self):
        """Test long text is accepted"""
        long_text = 'A' * 10000
        data = {
            'tldr': long_text,
            'motivation': long_text,
            'method': long_text,
            'result': long_text,
            'conclusion': long_text
        }
        structure = Structure(**data)
        assert len(structure.tldr) == 10000

    def test_unicode_text(self):
        """Test unicode text is accepted"""
        data = {
            'tldr': '中文摘要',
            'motivation': '中文动机',
            'method': '中文方法',
            'result': '中文结果',
            'conclusion': '中文结论'
        }
        structure = Structure(**data)
        assert structure.tldr == '中文摘要'
        assert structure.motivation == '中文动机'
