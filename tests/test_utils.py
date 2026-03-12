"""Tests for ai/utils.py"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock os.environ before importing the module
from unittest.mock import patch


class TestLoadResearchProfile:
    """Tests for load_research_profile function"""

    @patch.dict(os.environ, {}, clear=True)
    def test_empty(self):
        """Test with no environment variables set"""
        from ai import utils
        # Need to reload to pick up the mocked environ
        import importlib
        importlib.reload(utils)
        result = utils.load_research_profile()
        assert result is None

    @patch.dict(os.environ, {}, clear=True)
    def test_json_string_argument(self):
        """Test JSON string passed as argument"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        profile_str = '{"field": "Machine Learning", "methods": ["DL", "RL"]}'
        result = utils.load_research_profile(profile_str)
        assert result == {
            'field': 'Machine Learning',
            'methods': ['DL', 'RL']
        }

    @patch.dict(os.environ, {}, clear=True)
    def test_invalid_json_string(self):
        """Test invalid JSON string"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.load_research_profile('not valid json')
        # Should return None and print error (we don't check stderr here)
        assert result is None

    @patch.dict(os.environ, {'RESEARCH_PROFILE': '{"field": "AI"}'}, clear=True)
    def test_env_variable(self):
        """Test RESEARCH_PROFILE environment variable"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.load_research_profile()
        assert result == {'field': 'AI'}

    @patch.dict(os.environ, {
        'RESEARCH_FIELD': 'Computer Vision',
        'RESEARCH_PAIN_POINTS': 'small dataset, limited compute',
        'RESEARCH_METHODS': 'transformers, cnns'
    }, clear=True)
    def test_individual_env_vars(self):
        """Test individual environment variables"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.load_research_profile()
        assert result == {
            'field': 'Computer Vision',
            'pain_points': ['small dataset', 'limited compute'],
            'methods': ['transformers', 'cnns']
        }

    @patch.dict(os.environ, {'RESEARCH_FIELD': 'Only Field'}, clear=True)
    def test_only_field(self):
        """Test with only RESEARCH_FIELD set"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.load_research_profile()
        assert result == {'field': 'Only Field'}

    @patch.dict(os.environ, {
        'RESEARCH_PAIN_POINTS': 'a, b, c'
    }, clear=True)
    def test_comma_separated_pain_points(self):
        """Test comma-separated pain points"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.load_research_profile()
        assert result == {'pain_points': ['a', 'b', 'c']}

    @patch.dict(os.environ, {}, clear=True)
    def test_empty_env_vars(self):
        """Test with empty string environment variables"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        # Set empty strings
        with patch.dict(os.environ, {
            'RESEARCH_FIELD': '',
            'RESEARCH_PAIN_POINTS': '',
            'RESEARCH_METHODS': ''
        }):
            result = utils.load_research_profile()
            assert result is None


class TestGetSensitiveCheckUrl:
    """Tests for get_sensitive_check_url function"""

    @patch.dict(os.environ, {}, clear=True)
    def test_default_url(self):
        """Test default URL when env var not set"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.get_sensitive_check_url()
        assert result == 'https://spam.dw-dengwei.workers.dev'

    @patch.dict(os.environ, {'SENSITIVE_CHECK_URL': 'https://custom.example.com'}, clear=True)
    def test_custom_url(self):
        """Test custom URL from environment variable"""
        from ai import utils
        import importlib
        importlib.reload(utils)
        result = utils.get_sensitive_check_url()
        assert result == 'https://custom.example.com'
