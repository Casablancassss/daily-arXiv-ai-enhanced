"""Tests for ai/generate_report.py"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.generate_report import normalize_score, format_paper


class TestNormalizeScore:
    """Tests for normalize_score function"""

    def test_zero(self):
        """Test zero score"""
        assert normalize_score(0) == 0

    def test_one(self):
        """Test score 1 (0-1 range -> 100%)"""
        assert normalize_score(1) == 100

    def test_half(self):
        """Test 0.5 score (0-1 range -> 50%)"""
        assert normalize_score(0.5) == 50

    def test_decimal_small(self):
        """Test small decimal in 0-1 range"""
        assert normalize_score(0.25) == 25

    def test_ten(self):
        """Test score 10 (0-10 range -> 100%)"""
        assert normalize_score(10) == 100

    def test_five(self):
        """Test score 5 (0-10 range -> 50%)"""
        assert normalize_score(5) == 50

    def test_one_hundred(self):
        """Test score 100 (0-100 range -> 100%)"""
        assert normalize_score(100) == 100

    def test_fifty(self):
        """Test score 50 (0-100 range -> 50%)"""
        assert normalize_score(50) == 50

    def test_negative(self):
        """Test negative score should clamp to 0"""
        assert normalize_score(-1) == 0

    def test_over_hundred(self):
        """Test over 100 should clamp to 100"""
        assert normalize_score(150) == 100


class TestFormatPaper:
    """Tests for format_paper function"""

    def test_basic_paper(self):
        """Test basic paper formatting"""
        paper = {
            'title': 'Test Paper',
            'authors': ['Author A', 'Author B', 'Author C'],
            'relevance_score': 0.8,
            'abs': 'https://arxiv.org/abs/1234.5678',
            'summary': 'This is a test summary.',
            'AI': {}
        }
        result = format_paper(paper, 1)
        assert 'Test Paper' in result
        assert 'Author A, Author B, Author C' in result
        assert '80%' in result
        assert 'https://arxiv.org/abs/1234.5678' in result

    def test_paper_with_tldr(self):
        """Test paper with AI tldr field"""
        paper = {
            'title': 'Test Paper',
            'authors': ['Author A'],
            'relevance_score': 10,
            'abs': 'https://arxiv.org/abs/1234.5678',
            'summary': 'Original summary.',
            'AI': {
                'tldr': 'AI generated TLDR.'
            }
        }
        result = format_paper(paper, 1)
        assert 'AI generated TLDR.' in result
        assert '100%' in result  # 10 * 10 = 100

    def test_authors_list_limit(self):
        """Test authors list is limited to 3"""
        paper = {
            'title': 'Test Paper',
            'authors': ['A', 'B', 'C', 'D', 'E'],
            'relevance_score': 0.5,
            'abs': 'https://arxiv.org/abs/1234.5678',
            'summary': 'Summary.',
            'AI': {}
        }
        result = format_paper(paper, 1)
        # Should only have first 3 authors
        assert 'A, B, C' in result
        assert 'D' not in result

    def test_authors_string(self):
        """Test authors as string instead of list"""
        paper = {
            'title': 'Test Paper',
            'authors': 'Single Author String',
            'relevance_score': 0.5,
            'abs': 'https://arxiv.org/abs/1234.5678',
            'summary': 'Summary.',
            'AI': {}
        }
        result = format_paper(paper, 1)
        assert 'Single Author String' in result

    def test_missing_title(self):
        """Test paper with missing title"""
        paper = {
            'authors': ['Author A'],
            'relevance_score': 0.5,
            'summary': 'Summary.',
            'AI': {}
        }
        result = format_paper(paper, 1)
        assert 'Untitled' in result

    def test_no_score(self):
        """Test paper with no relevance score"""
        paper = {
            'title': 'Test Paper',
            'authors': ['Author A'],
            'summary': 'Summary.',
            'AI': {}
        }
        result = format_paper(paper, 1)
        assert '0%' in result  # Default score is 0

    def test_url_fallback(self):
        """Test URL fallback from url when abs is missing"""
        paper = {
            'title': 'Test Paper',
            'authors': ['Author A'],
            'relevance_score': 0.5,
            'url': 'https://arxiv.org/test',
            'summary': 'Summary.',
            'AI': {}
        }
        result = format_paper(paper, 1)
        assert 'https://arxiv.org/test' in result
