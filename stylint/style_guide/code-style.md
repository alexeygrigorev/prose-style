# Code style inside examples

Educational clarity beats defensive coding:

- Access known keys directly. Write `data['web']['results']`, not
  `data.get('web', {}).get('results', [])`. Let required keys fail loudly.
- No `try/except` unless the example is specifically about error handling.
- No speculative validation. Examples are here to show the happy path.
- Use `.get(key, default)` only when the key is optional and absence
  is expected.

This does not apply to production code pasted as reference. Show it as-is, but
say when the final version handles edge cases the notebook skips.

The checker catches double blank lines inside Python examples.
