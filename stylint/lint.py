"""Page-level lint orchestration."""

from pathlib import Path

from .models import Finding
from .patterns import *
from .rules.banned import check_banned_line
from .rules.code import check_code_block_length, check_python_code_line
from .rules.file_level import check_now_lets_overuse
from .rules.headings import check_heading
from .rules.markdown import check_markdown_line, check_table_row
from .rules.prose import check_paragraph, check_prose_line
from .tags import Tag
from .text import (
    strip_double_quoted,
    strip_frontmatter,
    strip_inline_code,
    strip_link_urls,
)

def check_page(root: Path, path: Path) -> list[Finding]:
    errors: list[Finding] = []
    now_lets_hits: list[tuple[int, str]] = []
    # State that survives flush_paragraph(). Mutable dict so the inner
    # flush can mutate without `nonlocal`. Tracks the start line of the
    # last flushed paragraph that was multi-sentence and ended with ':'
    # so we can fire `lead-in-multi` if the very next block is a list
    # or code fence.
    flush_state: dict[str, int | None] = {
        "multi_colon_line": None,
        "this_is_code_lead_in_line": None,
    }
    text = path.read_text()
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3 and parts[2] and not parts[2].startswith("\n"):
            fm_close_line = parts[0].count("\n") + parts[1].count("\n") + 2
            errors.append(Finding(
                rel, fm_close_line + 1, Tag.FRONTMATTER_BLANK,
                "insert a blank line between frontmatter and body",
            ))
    body = strip_frontmatter(text)
    fm_lines = text.count("\n") - body.count("\n") if body != text else 0
    line_offset = fm_lines
    lines = body.splitlines()
    in_code = False
    code_lang = ""
    previous_code_block_end: int | None = None
    code_block_start: int | None = None
    code_block_line_count = 0
    last_heading_line: int | None = None
    seen_prose_since_heading = False
    previous_code_line_blank = False
    blockquote_start: int | None = None
    blockquote_line_count = 0
    pending_short_label_line: int | None = None
    allow_questions_in_section = False

    paragraph_lines: list[tuple[int, str]] = []

    def heading_allows_questions(line: str) -> bool:
        text = strip_inline_code(strip_link_urls(line))
        text = text.lstrip("#").strip().lower()
        return (
            "q&a" in text
            or "q/a" in text
            or "q and a" in text
            or "questions and answers" in text
            or text in {"questions", "faq"}
            or text.startswith("questions ")
            or text.startswith("faq ")
        )

    def is_short_label_colon_line(value: str) -> bool:
        match = SHORT_LABEL_COLON_RE.match(value)
        if not match:
            return False
        label = match.group(0)[:-1].lower()
        return label not in CALLOUT_LABELS

    def emit_short_label_if_pending() -> None:
        nonlocal pending_short_label_line
        if pending_short_label_line is None:
            return
        errors.append(
            Finding(
                rel,
                pending_short_label_line,
                Tag.LABEL_COLON,
                "short label-colon line with 2-3 words. "
                "Use it only as a lead-in to a list or code block; "
                "otherwise drop the label and state the point directly.",
            )
        )
        pending_short_label_line = None

    def clear_short_label_if_pending() -> None:
        nonlocal pending_short_label_line
        pending_short_label_line = None

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        findings, pending_multi_colon_line = check_paragraph(
            paragraph_lines,
            rel,
            allow_questions=allow_questions_in_section,
        )
        errors.extend(findings)
        flush_state["multi_colon_line"] = pending_multi_colon_line
        start_line = paragraph_lines[0][0]
        joined = " ".join(text for _, text in paragraph_lines)
        if THIS_IS_CODE_LEAD_IN_RE.match(joined):
            flush_state["this_is_code_lead_in_line"] = start_line
        else:
            flush_state["this_is_code_lead_in_line"] = None
        paragraph_lines.clear()

    def flush_blockquote() -> None:
        nonlocal blockquote_start, blockquote_line_count
        if blockquote_start is None:
            return
        if blockquote_line_count > BLOCKQUOTE_MAX_LINES:
            errors.append(Finding(
                rel,
                blockquote_start,
                Tag.BLOCKQUOTE_LONG,
                "blockquote is longer than 3 lines; rework it into prose or a subsection",
            ))
        blockquote_start = None
        blockquote_line_count = 0

    def emit_lead_in_multi_if_pending() -> None:
        """If the last flushed paragraph was multi-sentence and ended
        with ':', emit the lead-in-multi finding (called when we see a
        list or code fence)."""
        line_no = flush_state.get("multi_colon_line")
        if line_no is None:
            return
        errors.append(Finding(
            rel, line_no, Tag.LEAD_IN_MULTI,
            "paragraph ending in ':' has multiple sentences but introduces a "
            "list or code block; make the lead-in (the sentence with the colon) "
            "its own one-sentence paragraph",
        ))
        flush_state["multi_colon_line"] = None

    def emit_this_is_code_lead_in_if_pending() -> None:
        line_no = flush_state.get("this_is_code_lead_in_line")
        if line_no is None:
            return
        errors.append(Finding(
            rel, line_no, Tag.LEAD_IN,
            "code lead-in starts with 'This is'; show the code first or name "
            "the action directly",
        ))
        flush_state["this_is_code_lead_in_line"] = None

    for line_no, line in enumerate(lines, start=1 + line_offset):
        stripped = line.strip()
        starts_fence = line.lstrip().startswith("```")

        if not BLOCKQUOTE_RE.match(line):
            flush_blockquote()

        if not in_code and previous_code_block_end is not None and stripped:
            if starts_fence:
                errors.append(Finding(
                    rel, line_no, Tag.CONSECUTIVE_CODE,
                    "consecutive code blocks need prose between them",
                ))
            previous_code_block_end = None

        if starts_fence:
            flush_paragraph()
            if not in_code:
                clear_short_label_if_pending()
                emit_lead_in_multi_if_pending()
                emit_this_is_code_lead_in_if_pending()
            if not in_code:
                fence_tail = line.lstrip()[3:].strip()
                if not fence_tail:
                    errors.append(Finding(
                        rel, line_no, Tag.CODE_NO_LANG,
                        "code block missing language tag (use ```python, ```bash, ...)",
                    ))
                if last_heading_line is not None and not seen_prose_since_heading:
                    errors.append(Finding(
                        rel, line_no, Tag.LEAD_IN,
                        f"code block needs a lead-in sentence after the heading on line {last_heading_line}",
                    ))
                code_lang = fence_tail.lower()
                code_block_start = line_no
                code_block_line_count = 0
                previous_code_line_blank = False
            else:
                errors.extend(
                    check_code_block_length(code_block_start, code_block_line_count, rel)
                )
                code_block_start = None
                code_lang = ""
            in_code = not in_code
            if not in_code:
                previous_code_block_end = line_no
            continue

        if in_code:
            code_block_line_count += 1
            if code_lang == "python":
                errors.extend(
                    check_python_code_line(line, previous_code_line_blank, line_no, rel)
                )
                previous_code_line_blank = line.strip() == ""
            continue

        if FOOTNOTE_DEF_RE.match(line):
            flush_paragraph()
            emit_short_label_if_pending()
            continue

        if HEADING_RE.match(line):
            flush_paragraph()
            emit_short_label_if_pending()
            errors.extend(check_heading(line, line_no, rel))
            plain = strip_inline_code(strip_link_urls(line))
            errors.extend(check_banned_line(line, plain, line_no, rel))
            last_heading_line = line_no
            seen_prose_since_heading = False
            allow_questions_in_section = heading_allows_questions(line)
            continue

        if not stripped:
            flush_paragraph()
        elif LIST_RE.match(line):
            flush_paragraph()
            clear_short_label_if_pending()
            emit_lead_in_multi_if_pending()
            if last_heading_line is not None and not seen_prose_since_heading:
                errors.append(Finding(
                    rel, line_no, Tag.LEAD_IN,
                    f"list needs a lead-in sentence after the heading on line {last_heading_line}",
                ))
                last_heading_line = None
            seen_prose_since_heading = True
        elif BLOCKQUOTE_RE.match(line) or line.startswith("|"):
            flush_paragraph()
            emit_short_label_if_pending()
            seen_prose_since_heading = True
            if BLOCKQUOTE_RE.match(line):
                if blockquote_start is None:
                    blockquote_start = line_no
                blockquote_line_count += 1
                # Blockquotes are verbatim quoted material (testimonials,
                # citations). Skip prose-level checks.
                continue
            # Table rows hold data (cells with names, dates, URLs,
            # descriptions). The 'tables are not used' finding still
            # fires above on the line.startswith('|') branch; here we
            # skip prose-level inline checks on cell content.
            errors.append(check_table_row(rel, line_no))
            continue
        elif line.lstrip().startswith("<"):
            emit_short_label_if_pending()
            # HTML markup (figure, img, figcaption, video, iframe).
            # Don't accumulate into paragraph_lines so the word count
            # of figcaption text + HTML attribute strings doesn't
            # trigger long-sentence. Still run inline rules below.
            seen_prose_since_heading = True
        elif is_short_label_colon_line(stripped):
            flush_paragraph()
            emit_short_label_if_pending()
            pending_short_label_line = line_no
            seen_prose_since_heading = True
        else:
            emit_short_label_if_pending()
            seen_prose_since_heading = True
            paragraph_lines.append((line_no, stripped))

        plain = strip_inline_code(strip_link_urls(line))
        errors.extend(check_markdown_line(line, plain, line_no, rel))
        prose_findings, line_now_lets_hits = check_prose_line(plain, line_no, rel)
        errors.extend(prose_findings)
        now_lets_hits.extend(line_now_lets_hits)
        errors.extend(check_banned_line(line, plain, line_no, rel))

    flush_paragraph()
    emit_short_label_if_pending()
    flush_blockquote()

    errors.extend(check_now_lets_overuse(now_lets_hits, rel))

    return errors
