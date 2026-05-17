# Formatting and markdown mechanics

Mechanical markdown rules (no bold/italic, no tables, no em dashes,
smart quotes, backticks-in-link-text, consecutive code blocks, code
block language tag, code block max length, lead-in for code/list,
blank line after frontmatter, heading depth, question-word headings,
bare URLs) are enforced by `stylint` - run it and follow the
inline guidance for each finding.

This doc collects the formatting choices that need agent judgment.

## Hard formatting rules not in the script

- Use ` - ` with spaces around dashes, not bare `-`, in prose.
- One dash per sentence. If you are reaching for two dashes to insert
  a parenthetical, split the sentence instead.
- Code ticks around every code-like identifier: filenames (`.env`,
  `app.py`), function names (`run_agent`), class names (`AsyncOpenAI`),
  env vars (`OPENAI_API_KEY`), module names (`minsearch`), regexes.
- Block quotes (`>`) are allowed for asides and warnings.

## Headings

- `#` once at the top for the title.
- `##` for every major section. This is the default.
- No emoji prefixes on headings.
- Do not number headings (`## 3. Part 1...`) unless you have a table
  of contents that uses the same numbers - then the numbers must
  match.

Section sizing: each `##` section should be substantial - multiple
code blocks, multiple paragraphs of explanation. If a section has one
code block and two sentences, merge it with a sibling.

## Code blocks

- For plain output, prompts, folder trees, and `.env` examples, use
  ` ```text `.
- For shell session transcripts where input and output matter, use
  ` ```console ` and a `$` prefix on the command, so syntax
  highlighting does not color the output as code.
- A 30-line dataclass that is read once is fine; a 30-line function
  that does four things should be four blocks. Split at the natural
  boundaries.
- Import statements live in the block where the library is first
  used. Do not group imports in a separate cell at the top.
- Import each library once per write-up. If you need it again later,
  assume the reader already has it.

For code style inside example blocks (defensive coding, blank-line
spacing), see `code-style.md`.

### Block splitting for pacing

Separate a class or function definition from its instantiation or
first call. A block that ends with `class NotebookRenderer: ...` and
then has `renderer = NotebookRenderer()` on the last line forces the
reader to scan to the bottom of a long block to find the thing that
actually runs. Two blocks with one sentence between them read faster:

```python
class NotebookRenderer:
    async def handle_event(self, event_type, payload): ...
    # (handlers omitted)
```

Then:

```python
renderer = NotebookRenderer()
```

The same rule applies to a helper function you define and then
immediately call. Define once, show usage next.

## Links

- Relative links between files in the same folder are fine.
- Do not link into unrelated repos by relative path. For external
  references, use a full URL.
- External links use descriptive text, not `click here` or `link`.
- Readers see the published markdown pages, not the local source
  checkout used to prepare them. Do not say `local source`,
  `source material`, or `the source folder` as if the reader can
  browse your machine. If a reader needs a reference file, either
  include the relevant code inline or link to the public GitHub file
  or folder with a full external URL.
- Do not use local-repo authoring phrases like `in your checkout`,
  `inspect it in your checkout`, `local checkout`, `source checkout`,
  or `open it in the reference repo or...`. They sound like internal
  maintenance notes. Use a direct reader-facing sentence instead:
  `The reference implementation has two main files: [App.jsx](...)
  and [SnakeGame.jsx](...).`
- Prefer `look at` over `inspect` when talking to the reader.
  `Inspect` sounds like a tool trace or code-review command. `Look at
  the messages` reads like normal prose.
- Prefer `To learn more` over `For follow-up reading`. It is shorter,
  direct, and sounds like an invitation rather than a bibliography
  note.

## Lists

Unordered lists use `- ` (dash + space). Ordered lists use `1.`,
`2.`, `3.`.

- Use bulleted lists when the reader wants to scan.
- Use numbered lists only for sequential steps.
- One item per line. No nested bullets unless the nesting is
  load-bearing.
- Keep item text short - one line each when possible. If one item
  needs a paragraph of explanation, pull it out into prose instead.

## Asides and warnings

Use block quotes for small warnings or asides that are worth pulling
out of the prose. Keep each one to one short paragraph - if the
aside runs longer, it is not an aside, it is a subsection.

```markdown
> The async Responses API expects `arguments` as the original JSON
> string, not as a parsed dict. If you re-serialize, OpenAI rejects
> the next request.
```
