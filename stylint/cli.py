"""Command-line interface."""

import argparse
from pathlib import Path
import sys

from .discovery import iter_markdown_pages
from .lint import check_page
from .output import print_findings
from .tags import Tag
from .version import __version__


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check mechanical markdown style rules.",
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
            "(e.g. --ignore tables,long-and-commas). Run with --list-tags "
            "to see all known tags."
        ),
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="Print all known rule tags and exit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"stylint {__version__}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_tags:
        for tag in Tag:
            print(tag.value)
        return 0

    valid_tags = {t.value for t in Tag}
    ignore_list = [t.strip() for t in args.ignore.split(",") if t.strip()]
    unknown = [t for t in ignore_list if t not in valid_tags]
    if unknown:
        print(f"Unknown tag(s) for --ignore: {', '.join(unknown)}", file=sys.stderr)
        print("Run with --list-tags to see known tags.", file=sys.stderr)
        return 2
    ignore_tags = {Tag(t) for t in ignore_list}

    paths = [Path(p) for p in args.paths]
    pages = iter_markdown_pages(paths)
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
