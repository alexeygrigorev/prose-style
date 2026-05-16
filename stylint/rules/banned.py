"""Banned token rule data."""

from ..patterns import BANNED_OPENERS, BANNED_PHRASES, BANNED_WORDS, OPENER_RE, WORD_RES
from ..models import Finding
from ..tags import Tag

__all__ = [
    "BANNED_OPENERS",
    "BANNED_PHRASES",
    "BANNED_WORDS",
    "OPENER_RE",
    "WORD_RES",
]


def check_banned_line(line: str, plain: str, line_no: int, rel) -> list[Finding]:
    findings: list[Finding] = []
    plain_lower = plain.lower()
    for word, hint in BANNED_WORDS.items():
        if WORD_RES[word].search(plain):
            findings.append(Finding(rel, line_no, Tag.BANNED_WORD, f"'{word}' - {hint}"))

    for phrase, hint in BANNED_PHRASES.items():
        if phrase in plain_lower:
            findings.append(Finding(rel, line_no, Tag.BANNED_PHRASE, f"'{phrase}' - {hint}"))

    opener_match = OPENER_RE.match(line)
    if opener_match:
        opener = opener_match.group(1)
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.BANNED_OPENER,
                f"'{opener}' - {BANNED_OPENERS[opener]}",
            )
        )
    return findings
