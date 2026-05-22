"""Command-line interface."""

import argparse
from pathlib import Path
import sys

from .discovery import iter_markdown_pages
from .lint import check_page
from .output import print_findings
from .styleguide import (
    agents_guide_file,
    style_guide_file,
    style_guide_files,
    style_guide_path,
)
from .tags import Tag
from .version import __version__


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check mechanical markdown style rules.",
        epilog=(
            "Agent workflow: run 'stylint --agents' first to see which "
            "style guide to use before editing, during structure changes, "
            "and before the final full check."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan. Defaults to the current directory.",
    )
    parser.add_argument(
        "--ignore",
        default="",
        metavar="TAGS",
        help=(
            "Comma-separated rule tags to suppress "
            "(e.g. --ignore tables,long-clause-likely). Run with --list-tags "
            "to see all known tags."
        ),
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Exclude files or folders by fnmatch pattern. Can be repeated "
            "or comma-separated, e.g. --exclude _docs --exclude AGENTS.md."
        ),
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="Print all known rule tags and exit.",
    )
    parser.add_argument(
        "--agents",
        action="store_true",
        help=(
            "Print the short agent editing checklist: when to read each "
            "style guide and how to verify edits."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"stylint {__version__}",
    )
    parser.add_argument(
        "--style-guide",
        metavar="NAME",
        nargs="?",
        const="",
        help=(
            "Print the installed style guide paths. Pass a guide name "
            "(voice, formatting, code-style, polish) to print that document."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_tags:
        for tag in Tag:
            print(tag.value)
        return 0

    if args.agents:
        print(agents_guide_file().read_text(encoding="utf-8"), end="")
        return 0

    if args.style_guide == "":
        print(style_guide_path())
        for name, path in style_guide_files().items():
            print(f"{name}: {path}")
        return 0

    if args.style_guide:
        try:
            path = style_guide_file(args.style_guide)
        except KeyError:
            print(
                "Unknown style guide. Use one of: "
                + ", ".join(style_guide_files()),
                file=sys.stderr,
            )
            return 2
        print(path.read_text(encoding="utf-8"), end="")
        return 0

    valid_tags = {t.value for t in Tag}
    # Backwards-compat: the single 'long-and-commas' tag was split into
    # two (long-list-likely and long-clause-likely). Accept the old name
    # as an alias that expands to both.
    tag_aliases = {
        "long-and-commas": ("long-list-likely", "long-clause-likely"),
    }
    raw = [t.strip() for t in args.ignore.split(",") if t.strip()]
    ignore_list: list[str] = []
    for t in raw:
        if t in tag_aliases:
            ignore_list.extend(tag_aliases[t])
        else:
            ignore_list.append(t)
    unknown = [t for t in ignore_list if t not in valid_tags]
    if unknown:
        print(f"Unknown tag(s) for --ignore: {', '.join(unknown)}", file=sys.stderr)
        print("Run with --list-tags to see known tags.", file=sys.stderr)
        return 2
    ignore_tags = {Tag(t) for t in ignore_list}

    exclude_patterns = [
        pattern.strip()
        for raw_exclude in args.exclude
        for pattern in raw_exclude.split(",")
        if pattern.strip()
    ]

    paths = [Path(p) for p in args.paths]
    pages = iter_markdown_pages(paths, exclude_patterns)
    if not pages:
        print("No markdown files found.", file=sys.stderr)
        return 0

    findings = []
    for root, page in pages:
        findings.extend(check_page(root, page))

    if ignore_tags:
        findings = [finding for finding in findings if finding.tag not in ignore_tags]

    if findings:
        print_findings(findings)
        return 1

    suffix = "s" if len(pages) != 1 else ""
    print(f"Style check passed ({len(pages)} file{suffix}).")
    return 0
