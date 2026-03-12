"""Tests for to_md/convert.py"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from to_md.convert import escape_template_chars


class TestEscapeTemplateChars:
    """Tests for escape_template_chars function"""

    def test_empty_string(self):
        """Test empty string"""
        assert escape_template_chars('') == ''

    def test_none_input(self):
        """Test None input"""
        assert escape_template_chars(None) == ''

    def test_normal_text(self):
        """Test normal text without braces"""
        result = escape_template_chars('Hello World')
        assert result == 'Hello World'

    def test_single_braces(self):
        """Test single braces are doubled"""
        result = escape_template_chars('Hello {name}')
        assert result == 'Hello {{name}}'

    def test_multiple_braces(self):
        """Test multiple braces"""
        result = escape_template_chars('{title} by {author}')
        assert result == '{{title}} by {{author}}'

    def test_already_escaped_backslash(self):
        """Test backslash-escaped braces are normalized first"""
        result = escape_template_chars(r'\{title\}')
        # First normalizes \{ -> { and \} -> }, then doubles { -> {{ and } -> }}
        assert result == '{{title}}'

    def test_mixed_braces(self):
        """Test mixed escaped and unescaped braces"""
        result = escape_template_chars(r'\{title\} and {author}')
        # \{title\} becomes {title}, then doubled to {{title}}
        assert result == '{{title}} and {{author}}'

    def test_only_opening_brace(self):
        """Test only opening brace"""
        result = escape_template_chars('Hello {')
        assert result == 'Hello {{'

    def test_only_closing_brace(self):
        """Test only closing brace"""
        result = escape_template_chars('Hello }')
        assert result == 'Hello }}'

    def test_integer_input(self):
        """Test integer input is converted to string"""
        result = escape_template_chars(123)
        assert result == '123'

    def test_already_doubled(self):
        """Test already doubled braces get doubled again"""
        # The function doesn't handle {{ specially - it just doubles all braces
        result = escape_template_chars('{{title}}')
        # {{ becomes {{{{ (doubled again)
        assert result == '{{{{title}}}}'
