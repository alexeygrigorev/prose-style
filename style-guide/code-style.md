# Code style inside examples

Read this when writing or reviewing the code blocks shown in technical
write-ups. For markdown formatting around the code (block size, language
tag, no consecutive blocks), see `formatting.md`.

Educational clarity beats defensive coding. In example code:

- Access known keys directly. Write `data['web']['results']`, not
  `data.get('web', {}).get('results', [])`. If a key is required by the API
  contract, reaching it directly and blowing up on failure teaches the
  reader the contract.
- No `try/except` unless the example is specifically about error handling.
- No speculative validation. Examples are here to show the happy path.
- Use `.get(key, default)` only when the key is optional and absence
  is expected.

This rule does not extend to production code you are pasting in as a
reference - if the final `app.py` has defensive code in it, show it as-is,
but mention in prose that the production version handles edge cases the
notebook does not.

## Blank lines inside code blocks

Use one empty line between logical pieces, not two. Python's PEP 8 suggests
two blank lines between top-level class or function definitions. Write-ups
use one. Double blank lines waste vertical space and push prose further
from the code it describes.

Bad:

```python
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ToolCall(BaseModel):
    name: str
    arguments: dict
```

Good:

```python
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)

class ToolCall(BaseModel):
    name: str
    arguments: dict
```

The same applies inside functions: one blank line between logical
sections, never two.
