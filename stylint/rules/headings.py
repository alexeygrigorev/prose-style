"""Heading rule patterns."""

from ..patterns import (
    DEEP_HEADING_RE,
    LAZY_HEADING_RE,
    QUESTION_HEADING_ALLOWLIST,
    QUESTION_HEADING_RE,
    QUESTION_MARK_HEADING_RE,
)
from ..models import Finding
from ..tags import Tag

__all__ = [
    "DEEP_HEADING_RE",
    "LAZY_HEADING_RE",
    "QUESTION_HEADING_ALLOWLIST",
    "QUESTION_HEADING_RE",
    "QUESTION_MARK_HEADING_RE",
]


def check_heading(line: str, line_no: int, rel) -> list[Finding]:
    findings: list[Finding] = []
    if QUESTION_HEADING_RE.match(line):
        heading_text = line.lstrip("#").strip().rstrip("?").strip().lower()
        if heading_text not in QUESTION_HEADING_ALLOWLIST:
            findings.append(
                Finding(rel, line_no, Tag.HEADING_QUESTION_WORD, "avoid question-word headings")
            )
    if QUESTION_MARK_HEADING_RE.match(line):
        findings.append(
            Finding(rel, line_no, Tag.HEADING_QUESTION_MARK, "heading ends with '?' (use a statement)")
        )
    if DEEP_HEADING_RE.match(line):
        findings.append(
            Finding(rel, line_no, Tag.HEADING_TOO_DEEP, "heading depth ### or deeper not allowed")
        )
    if LAZY_HEADING_RE.match(line):
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.LAZY_HEADING,
                "lazy heading 'The <problem|issue|...>'; name what the section is actually about",
            )
        )
    return findings
