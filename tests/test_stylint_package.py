"""Tests for the stylint package import surface."""

from pathlib import Path

from stylint import (
    Finding,
    Tag,
    agents_guide_file,
    check_page,
    count_sentences,
    find_gerund_starts,
    style_guide_file,
    style_guide_files,
    style_guide_path,
)
from stylint.discovery import iter_markdown_pages


def test_package_exports_public_api():
    assert Tag.BOLD.value == "bold"
    assert Finding.__name__ == "Finding"
    assert check_page.__name__ == "check_page"
    assert count_sentences("One. Two.") == 2
    assert find_gerund_starts("Reading this, we see the point.") == ["Reading"]


def test_package_exposes_discovery_helpers():
    assert iter_markdown_pages([]) == []


def test_discovery_skips_default_ignored_dirs(tmp_path: Path):
    keep = tmp_path / "README.md"
    keep.write_text("Keep me.\n")

    for dirname in [".venv", ".pytest_cache", "node_modules", "build"]:
        ignored_dir = tmp_path / dirname
        ignored_dir.mkdir()
        (ignored_dir / "README.md").write_text("Ignore me.\n")

    pages = iter_markdown_pages([tmp_path])

    assert pages == [(tmp_path.resolve(), keep.resolve())]


def test_discovery_keeps_project_ignore_file_behavior(tmp_path: Path):
    keep = tmp_path / "README.md"
    keep.write_text("Keep me.\n")
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "README.md").write_text("Ignore me.\n")
    (tmp_path / ".prose-style-ignore").write_text("generated\n")

    pages = iter_markdown_pages([tmp_path])

    assert pages == [(tmp_path.resolve(), keep.resolve())]


def test_discovery_excludes_cli_patterns(tmp_path: Path):
    keep = tmp_path / "README.md"
    keep.write_text("Keep me.\n")
    docs = tmp_path / "_docs"
    docs.mkdir()
    (docs / "README.md").write_text("Ignore me.\n")
    nested = tmp_path / "lesson"
    nested.mkdir()
    (nested / "notes.md").write_text("Ignore me too.\n")

    pages = iter_markdown_pages([tmp_path], ["_docs", "lesson/*.md"])

    assert pages == [(tmp_path.resolve(), keep.resolve())]


def test_discovery_excludes_direct_file(tmp_path: Path):
    page = tmp_path / "AGENTS.md"
    page.write_text("Ignore me.\n")

    pages = iter_markdown_pages([page], ["AGENTS.md"])

    assert pages == []


def test_package_exposes_bundled_style_guide():
    guide_path = style_guide_path()
    files = style_guide_files()

    assert guide_path.is_dir()
    assert set(files) == {"voice", "formatting", "code-style", "polish"}
    for path in files.values():
        assert path.is_file()
        assert path.parent == guide_path


def test_package_exposes_one_style_guide_doc():
    path = style_guide_file("voice")
    assert path.name == "voice.md"
    assert path.read_text(encoding="utf-8").startswith("# ")

    same_path = style_guide_file("voice.md")
    assert same_path == path


def test_package_exposes_agents_guide():
    path = agents_guide_file()
    assert path.name == "agents.md"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("Use this before and after editing technical text.")
