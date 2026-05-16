"""Text normalization and sentence helpers."""

import re

from .patterns import (
    ABBREVIATION_RE,
    GERUND_LINE_START_RE,
    GERUND_MIDLINE_RE,
    GERUND_NOUN_EXCEPTIONS,
    LINK_RE,
    SENTENCE_END_RE,
)


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text

    parts = text.split("---\n", 2)
    if len(parts) == 3:
        return parts[2]
    return text


def strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def strip_link_urls(line: str) -> str:
    return LINK_RE.sub(lambda match: match.group(1), line)


def strip_double_quoted(line: str) -> str:
    return re.sub(r'"[^"]*"', "", line)


def count_sentences(text: str) -> int:
    text = re.sub(r"`[^`]*`", " ", text)
    text = ABBREVIATION_RE.sub("", text)
    return len(SENTENCE_END_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    """Split prose into individual sentences (ignoring abbreviations and code)."""
    text = re.sub(r"`[^`]*`", " ", text)
    text = ABBREVIATION_RE.sub("", text)
    return [s.strip() for s in SENTENCE_END_RE.split(text) if s.strip()]


def count_words(text: str) -> int:
    """Count whitespace-delimited tokens that contain at least one word char."""
    return sum(1 for token in text.split() if re.search(r"\w", token))


def find_gerund_starts(plain: str) -> list[str]:
    flagged: list[str] = []
    line_match = GERUND_LINE_START_RE.match(plain.lstrip())
    if line_match and line_match.group(1).lower() not in GERUND_NOUN_EXCEPTIONS:
        flagged.append(line_match.group(1))
    for match in GERUND_MIDLINE_RE.finditer(plain):
        word = match.group(1)
        if word.lower() not in GERUND_NOUN_EXCEPTIONS:
            flagged.append(word)
    return flagged
