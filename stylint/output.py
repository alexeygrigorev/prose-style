"""Terminal output formatting."""

from collections import defaultdict

from .models import Finding


def pluralize(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def print_findings(findings: list[Finding]) -> None:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[str(finding.file)].append(finding)

    print(
        f"Style check failed ({pluralize(len(findings), 'finding')} across "
        f"{pluralize(len(grouped), 'file')}):"
    )
    for file_path in sorted(grouped):
        file_findings = grouped[file_path]
        print(f"\n{file_path} ({pluralize(len(file_findings), 'finding')}):")
        for finding in file_findings:
            line_part = f"{finding.line}: " if finding.line is not None else ""
            print(f"  {line_part}[{finding.tag.value}] {finding.message}")
