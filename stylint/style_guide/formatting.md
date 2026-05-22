# Formatting and markdown mechanics

This doc covers formatting choices that need judgment after `stylint` runs.

## Formatting choices

Use these formatting conventions.

- One dash per sentence. If you are reaching for two dashes to insert
  a parenthetical, split the sentence instead.
- Use code ticks around code-like identifiers: filenames, function names,
  class names, env vars, module names, and regexes.

## Headings

Use this heading structure.

- `#` once at the top for the title.
- `##` for every major section. This is the default.
- No emoji prefixes on headings.
- Do not number headings unless a table of contents uses the same numbers.

Each `##` section should be substantial. If it has one code block and two
sentences, merge it with a sibling.

## Code blocks

Use these block conventions:

- For plain output, prompts, folder trees, and `.env` examples, use
  ` ```text `.
- For shell transcripts, use ` ```console ` and a `$` prefix on commands.
- A 30-line dataclass can stay together. A 30-line function that does four
  things should become four blocks.
- Import statements live in the block where the library is first
  used. Do not group imports in a separate cell at the top.
- Import each library once per write-up. If you need it again later,
  assume the reader already has it.

## Block splitting

Separate a class or function definition from its first call. Do not hide the
call at the bottom of a long definition block.

Use two blocks.

```python
class NotebookRenderer:
    async def handle_event(self, event_type, payload): ...
    # (handlers omitted)
```

Then instantiate or call it.

```python
renderer = NotebookRenderer()
```

Same for helper functions: define once, show usage next.

## Links

Keep links reader-facing.

- Do not link into unrelated repos by relative path. For external
  references, use a full URL.
- External links use descriptive text, not `click here` or `link`.
- Readers see published pages, not your local checkout. Do not say `local
  source`, `source material`, or `the source folder`. Include the code inline
  or link to the public GitHub file.
- Avoid authoring phrases like `in your checkout`, `local checkout`, and
  `open it in the reference repo`. Write for the published page instead.
