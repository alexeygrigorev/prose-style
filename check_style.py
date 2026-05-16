#!/usr/bin/env python3
"""Compatibility wrapper for the stylint package."""

import sys

from stylint.cli import main, parse_args
from stylint.discovery import iter_markdown_pages, is_ignored, load_ignore_patterns
from stylint.lint import check_page
from stylint.models import Finding
from stylint.tags import Tag
from stylint.text import (
    count_sentences,
    count_words,
    find_gerund_starts,
    split_sentences,
    strip_double_quoted,
    strip_frontmatter,
    strip_inline_code,
    strip_link_urls,
)

__all__ = [
    "Finding",
    "Tag",
    "check_page",
    "count_sentences",
    "count_words",
    "find_gerund_starts",
    "is_ignored",
    "iter_markdown_pages",
    "load_ignore_patterns",
    "main",
    "parse_args",
    "split_sentences",
    "strip_double_quoted",
    "strip_frontmatter",
    "strip_inline_code",
    "strip_link_urls",
]


if __name__ == "__main__":
    sys.exit(main())
