"""Markdown file discovery and ignore-file handling."""

import fnmatch
from pathlib import Path


def load_ignore_patterns(root: Path) -> list[str]:
    ignore_file = root / ".prose-style-ignore"
    if not ignore_file.is_file():
        return []
    patterns: list[str] = []
    for raw in ignore_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def is_ignored(rel: Path, patterns: list[str]) -> bool:
    rel_str = str(rel)
    for pattern in patterns:
        if fnmatch.fnmatch(rel_str, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in rel.parts):
            return True
    return False


def iter_markdown_pages(paths: list[Path]) -> list[tuple[Path, Path]]:
    """Return [(root, page)] pairs so error paths can stay relative to the scan root."""
    pages: list[tuple[Path, Path]] = []
    for p in paths:
        p = p.resolve()
        if p.is_file() and p.suffix.lower() == ".md":
            pages.append((p.parent, p))
        elif p.is_dir():
            ignore = load_ignore_patterns(p)
            for md in sorted(p.rglob("*.md")):
                rel = md.relative_to(p)
                if is_ignored(rel, ignore):
                    continue
                pages.append((p, md))
    return pages
