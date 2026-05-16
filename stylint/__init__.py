"""Markdown style linter for technical prose."""

from .lint import check_page
from .models import Finding
from .tags import Tag
from .text import count_sentences, count_words, find_gerund_starts, split_sentences
from .version import __version__

__all__ = [
    "Finding",
    "Tag",
    "__version__",
    "check_page",
    "count_sentences",
    "count_words",
    "find_gerund_starts",
    "split_sentences",
]
