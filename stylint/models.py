"""Shared data models."""

from dataclasses import dataclass
from pathlib import Path

from .tags import Tag


@dataclass(frozen=True)
class Finding:
    """One lint finding. `line` is None for file-level rules."""

    file: Path
    line: int | None
    tag: Tag
    message: str

    def format(self) -> str:
        location = f"{self.file}:{self.line}" if self.line is not None else str(self.file)
        return f"{location}: [{self.tag.value}] {self.message}"

    def __str__(self) -> str:
        return self.format()

    def __contains__(self, item: str) -> bool:
        # Lets `"substring" in finding` work in tests and grep-style checks.
        return item in self.format()
