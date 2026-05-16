"""File-level rule constants."""

from ..patterns import NOW_LETS_MAX_PER_FILE, NOW_LETS_OPENER_RE
from ..models import Finding
from ..tags import Tag

__all__ = ["NOW_LETS_MAX_PER_FILE", "NOW_LETS_OPENER_RE"]


def check_now_lets_overuse(now_lets_hits: list[tuple[int, str]], rel) -> list[Finding]:
    if len(now_lets_hits) <= NOW_LETS_MAX_PER_FILE:
        return []
    lines = ", ".join(str(ln) for ln, _ in now_lets_hits)
    return [
        Finding(
            rel,
            None,
            Tag.NOW_LETS_OVERUSE,
            f"file uses {len(now_lets_hits)} 'Now' / 'Let's' sentence-starters "
            f"(max {NOW_LETS_MAX_PER_FILE}; lines {lines}); "
            "vary openers - try 'After that', 'Then', 'Next', or drop the "
            "softener entirely and use a bare imperative",
        )
    ]
