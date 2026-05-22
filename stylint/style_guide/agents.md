Use this before and after editing technical text.

1. Run `stylint --style-guide voice` before rewriting paragraphs: tone, cuts,
   and how personal the writing should be.
2. Run `stylint --style-guide formatting` when changing headings, lists, code
   blocks, links, captions, or callouts.
3. Run `stylint --style-guide code-style` when editing example code or command
   snippets.
4. Run `stylint --style-guide polish` for the final pass: fluff, abstractions,
   bridges, redundant setup, and topic-introducer sentences.
5. After editing, run the full `stylint` check without `--ignore`.

Use `--ignore` only for investigation. It is not a verification pass.
