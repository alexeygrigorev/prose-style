# stylint

Voice, formatting, and code-style rules for technical write-ups, plus a
mechanical checker that catches the worst offenders.

## Install

```bash
uv tool install git+https://github.com/alexeygrigorev/prose-style-lint
```

Or from a local clone:

```bash
git clone https://github.com/alexeygrigorev/prose-style-lint ~/git/prose-style-lint
uv tool install --from ~/git/prose-style-lint stylint
```

Then run:

```bash
stylint docs/
stylint --list-tags
stylint --ignore tables docs/
```

## What's here

- `voice.md` - tone, voice rules, content rules (include/leave out).
- `formatting.md` - markdown mechanics: headings, code blocks, lists,
  links, asides.
- `code-style.md` - educational code style inside example blocks
  (no defensive `try/except`, no chained `.get()`, one blank line
  between definitions).
- `polish.md` - judgment-level prose patterns the script cannot detect
  (plain words over abstractions, banned-but-context-sensitive words).
- `stylint/` - mechanical checker package. Edit `BANNED_WORDS`,
  `BANNED_PHRASES`, `BANNED_OPENERS` in `stylint/patterns.py` to
  extend the enforced list.
- `check_style.py` - compatibility wrapper for direct script usage.

## Run the checker

Scan the current directory:

```bash
stylint
```

Scan one file or a specific folder:

```bash
stylint path/to/post.md
stylint docs/
```

Suppress specific rules with `--ignore`:

```bash
stylint --ignore tables docs/
stylint --ignore tables,long-and-commas docs/
stylint --list-tags
```

To skip files, drop a `.prose-style-ignore` at the scan root, one
fnmatch pattern per line:

```text
# build outputs
_site/*
node_modules/*
# generated docs
docs/api/*
```

## Rule tags

Every finding starts with a `[tag]` so you know which rule fired and
can pass that tag to `--ignore`.

### Markdown mechanics

- `bold` - `**text**` or `__text__` used for emphasis.
- `italic` - `*text*` or `_text_` used for emphasis.
- `tables` - GFM table row (a line starting with `|`).
- `hr` - horizontal rule `---` on its own line.
- `em-dash` - the em-dash character `—`.
- `double-hyphen` - `--` used as a substitute for an em dash.
- `dash-parenthetical` - sentence with two ` - ` dashes inserting a
  parenthetical.
- `smart-quotes` - curly quotes `‘`, `’`, `“`, `”`.
- `backticks-in-link` - link text wrapped in backticks like
  `` [`file.py`](url) ``.
- `bare-url` - raw URL in prose like `see https://example.com`.
- `angle-url` - URL wrapped in angle brackets like `<https://...>`.
- `frontmatter-blank` - missing blank line between YAML frontmatter
  closing `---` and the body.

### Headings

- `heading-question-word` - heading starts with `Why`, `How`, `What`,
  etc.
- `heading-question-mark` - heading ends with `?`.
- `heading-too-deep` - heading depth `###` or deeper.
- `lazy-heading` - heading like `## The problem`, `## The RAG idea`,
  `## The challenge`.

### Code blocks

- `code-no-lang` - fenced code block with no language tag.
- `code-too-long` - code block over 40 lines.
- `consecutive-code` - two code blocks back-to-back with no prose
  between them.
- `lead-in` - code block or list directly under a heading with no
  lead-in sentence.
- `lead-in-multi` - the paragraph that introduces a list or code
  block has multiple sentences and ends with `:`. The lead-in
  sentence should be its own one-sentence paragraph.
- `chained-get` - chained `.get(...).get(...)` in example Python.
- `double-blank` - two blank lines between Python definitions.

### Banned tokens (extend in `stylint/patterns.py`)

- `banned-word` - single word on the BANNED_WORDS list (e.g. `delve`,
  `leverage`, `crucial`).
- `banned-phrase` - multi-word phrase on the BANNED_PHRASES list
  (e.g. `the power of`, `serves as`, `in action`, `the backbone of`).
- `banned-opener` - sentence-start word on the BANNED_OPENERS list
  (e.g. `Additionally`, `Moreover`).

### Voice / fragments

- `third-person` - the string `Alexey` appears in prose (third-person
  presenter reference).
- `anaphoric-no` - sentence-start `No X, no Y` verbless fragment
  (e.g. `No frameworks, no magic`).
- `semicolon` - any `;` in prose.
- `cleft` - pointless `[This/That/It] is what X is about` cleft.
- `gerund-opener` - sentence opens with an `-ing` participial phrase
  (e.g. `Reading through it, I noticed...`).

### Paragraph / sentence shape

- `paragraph-too-long` - paragraph with more than 5 sentences.
- `long-sentence` - sentence over 20 words, no commas.
- `long-and-commas` - sentence over 20 words and contains commas.
- `many-commas` - sentence with more than 3 commas.
- `colon-inline` - colon followed by 3+ comma-separated items and a
  terminal `and`/`or` (likely should be a bullet list).
- `parallel-sentences` - 3+ adjacent sentences sharing the same 1-2
  word opener (e.g. `Maybe it should... Maybe it should...`).
- `label-colon` - paragraph opens with `The problem:`, `Goal:`,
  `What we want:` followed by prose. `Note:` and `Important:` are
  exempt as callouts.
- `question-opener` - paragraph opens with a rhetorical question
  (`Why do we need X?`).

### File-level

- `now-lets-overuse` - file uses more than 3 sentence-starting
  `Now`/`Let's` openers total. Vary openers or use the bare imperative.
- `now-lets-combo` - sentence starts with the redundant pair
  `Now let's...` or `Let's now...`. Drop both softeners and use the
  bare imperative.

## Reading order for a write-up

1. `voice.md` while drafting.
2. `formatting.md` for any markdown syntax question.
3. `code-style.md` for example code blocks.
4. Run `stylint` and fix every reported finding.
5. `polish.md` for a final judgment-level pass.

## Hooking it into a project

The simplest setup is a pre-commit hook. From the target project root:

```bash
ln -s ~/git/prose-style-lint/check_style.py .git/hooks/post-add-style-check
```

Or run it from CI:

```yaml
- run: stylint docs/
```

## Notes on what's enforced vs. what's judgment

The script catches every rule listed in the "Rule tags" section above.
Each error message includes the tag, a numbered list of common fixes,
and (for list-conversion rules) the inline heuristic for deciding
whether a bullet list is right.

Everything else (tone, voice, abstractions, "explain why", source
material handling) is in the reference docs and needs a human or
agent to apply judgment.
