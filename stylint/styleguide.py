"""Helpers for locating the bundled style guide."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


def style_guide_path() -> Path:
    """Return the installed directory that contains the style guide docs."""
    return Path(str(resources.files("stylint.style_guide")))


def style_guide_files() -> dict[str, Path]:
    """Return style guide document names mapped to installed paths."""
    guide = style_guide_path()
    return {
        "voice": guide / "voice.md",
        "formatting": guide / "formatting.md",
        "code-style": guide / "code-style.md",
        "polish": guide / "polish.md",
    }


def style_guide_file(name: str) -> Path:
    """Return one style guide document by short name or filename."""
    normalized = name.removesuffix(".md")
    files = style_guide_files()
    if normalized not in files:
        names = ", ".join(files)
        raise KeyError(f"unknown style guide document '{name}' (choose one of: {names})")
    return files[normalized]


def agents_guide_file() -> Path:
    """Return the short agent-facing guide document."""
    return style_guide_path() / "agents.md"
