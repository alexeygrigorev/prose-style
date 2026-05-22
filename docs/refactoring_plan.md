# Refactoring plan

`check_style.py` still owns the whole application. The refactor should expose
the main responsibilities without changing behavior first.

The key constraint is compatibility. Users can run `check_style.py`
directly, packaging exposes `stylint = "stylint.cli:main"` and keeps
`prose-style-lint = "stylint.cli:main"` as an alias, and tests import
helpers from `check_style`. Keep that file as the public shim until the
package API is explicit and documented.

## Goals

Keep the first refactor narrow:

- Keep behavior and output stable during the first passes.
- Preserve existing imports from `check_style`.
- Move pure helpers and data before moving stateful scanning logic.
- Make individual rule groups easier to test and extend.
- Avoid a full rule-engine rewrite until the current behavior is covered
  through smaller modules.

## Target structure

Use this package layout:

```text
stylint/
  __init__.py
  cli.py
  discovery.py
  lint.py
  models.py
  output.py
  patterns.py
  tags.py
  text.py
  rules/
    __init__.py
    banned.py
    code.py
    file_level.py
    headings.py
    markdown.py
    prose.py
```

`check_style.py` should become a thin wrapper that re-exports the current
public names and delegates `main()` to `stylint.cli`.

## Public compatibility surface

Keep these available from `check_style` during the refactor:

- `Tag`
- `Finding`
- `check_page`
- `count_sentences`
- `split_sentences`
- `count_words`
- `find_gerund_starts`
- `iter_markdown_pages`
- `main`

This avoids unnecessary changes to the existing tests and direct script
usage.

## Phase 1: Extract pure data and helpers

Move definitions that do not depend on scanner state.

- `tags.py` - `Tag`.
- `models.py` - `Finding`.
- `patterns.py` - compiled regexes, banned word dictionaries, thresholds,
  and message constants.
- `text.py` - frontmatter stripping, inline-code stripping, sentence helpers,
  word counts, and gerund detection.

Keep `check_style.py` re-exporting the names used by tests. This phase
should be mostly import changes plus tests.

## Phase 2: Extract file discovery

Move filesystem traversal into `discovery.py`.

- `load_ignore_patterns`
- `is_ignored`
- `iter_markdown_pages`

This module should stay independent from linting. It only needs `Path`,
`fnmatch`, and ignore-file semantics.

## Phase 3: Extract CLI and output

Move argument parsing and terminal output away from lint logic.

- `cli.py`: `parse_args`, `main`, ignore-tag validation, path conversion.
- `output.py`: grouped finding formatter and pluralization helper.

The CLI should call `iter_markdown_pages` and `check_page`, then format
findings.

Keep exit codes unchanged:

- `0`: success or no markdown files found.
- `1`: lint findings.
- `2`: unknown ignored tag.

## Phase 4: Split `check_page` without changing its scanner

`check_page` is the risky center of the codebase. It tracks code fences,
paragraph flushing, heading lead-ins, and file-level counters.

Do not replace that control flow first. Extract small functions from the
existing branches while keeping the same loop.

Use these helper boundaries:

- `check_frontmatter_spacing(text, rel) -> list[Finding]`
- `check_heading(line, line_no, rel) -> list[Finding]`
- `check_markdown_line(line, line_no, rel) -> list[Finding]`
- `check_plain_text_line(line, plain, line_no, rel) -> list[Finding]`
- `check_code_line(line, code_lang, line_no, rel) -> list[Finding]`
- `check_paragraph(paragraph_lines, rel) -> ParagraphResult`
- `check_file_level(now_lets_hits, rel) -> list[Finding]`

`ParagraphResult` can carry both findings and the pending
`lead-in-multi` state.

## Phase 5: Group rules by category

Once Phase 4 is stable, move extracted helpers into rule modules.

- `rules/markdown.py` - bold, italic, table rows, horizontal rules, dash
  forms, smart quotes, links, URLs.
- `rules/headings.py` - question headings, heading depth, lazy headings.
- `rules/code.py` - language tags, long code blocks, chained `.get`,
  double blank lines, consecutive code blocks, lead-ins.
- `rules/banned.py` - banned words, phrases, openers, cross-line phrases.
- `rules/prose.py` - sentence length, comma count, paragraph length,
  label-colon, question openers, gerund openers, and semicolons.
- `rules/file_level.py` - file-scope `Now` / `Let's` overuse.

The scanner in `lint.py` should orchestrate state and call these rule
functions.

## Phase 6: Consider a block scanner

Only after the smaller extraction is stable, consider converting the line loop
into a markdown block scanner.

It could emit these objects:

- `Paragraph`
- `Heading`
- `CodeBlock`
- `ListBlock`
- `TableRow`
- `BlockQuote`

This would make rules cleaner, but it is a larger behavioral change.
The current implementation depends on adjacency and line-level details,
so this should be a later refactor, not the starting point.

## Test strategy

Keep the current end-to-end tests for `check_page`. Add module-level
tests only when a helper becomes non-trivial.

Cover these cases before deeper scanner changes:

- frontmatter line-number offsets
- banned phrases across lines
- code block length and language tags
- heading-to-list and heading-to-code lead-ins
- consecutive code blocks
- paragraph sentence counts
- file-level `Now` / `Let's` overuse
- ignored tags and grouped CLI output

Run the full test suite after each phase. If output formatting is touched,
add CLI-level tests before changing the implementation further.

## Risks

Watch these areas.

- Line numbers can drift when frontmatter and paragraph flushing move.
- Cross-line banned phrase detection can double-fire if line and paragraph
  checks are split carelessly.
- Lead-in rules depend on previous heading state and text after that heading.
- Code block rules depend on fence transitions, not only on code lines.
- Moving constants too aggressively can make rule modules harder to read.

## First implementation pass

The first pass should be deliberately mechanical.

1. Create the `stylint` package directory.
2. Move `Tag`, `Finding`, text helpers, constants, and discovery helpers.
3. Update imports.
4. Keep `check_page` behavior in one place.
5. Keep `check_style.py` as a compatibility wrapper.
6. Run tests and compare CLI output on a known sample.

Only start splitting `check_page` after this passes cleanly.
