# Voice polish

Read this after `stylint`. Keep only judgment-level fixes here. If a pattern
can be checked reliably, add it to the script instead.

After editing, run the full `stylint` check without `--ignore`.

This pass usually changes more than the mechanical one. If a sentence
reads like an editor wrote it, rewrite it so it reads like the author.

## Plain words over abstractions

Every sentence has to carry information. If it could be cut without losing the
point, cut it.

Rewrite these patterns.

- Shape-framing like `the X shape is...` - introduce the code directly.
- `we control the POST ourselves` - what does "control" mean? Name
  the actions: `we send the POST ourselves, set the streaming header
  on it, and write each chunk as we go`.
- `two views of the same function`, `the X perspective`, `from a
  certain angle` - drop the view/angle framing. Describe what is
  actually true on each side: `From outside, X. From inside, Y.`
- `the public-facing command` and `the private implementation` for a
  shell script and its helpers - the OOP encapsulation metaphor does
  not apply. Use `the entry point you run` and `the steps it
  sequences`.
- `the managed runtime takes care of talking to Lambda for you` -
  what does "takes care of" mean? Name the actions: `reads the
  event off the Runtime API, calls your function with it, sends the
  return value back as the response`.
- Vague evaluative words: `fiddly`, `tricky`, `nice`, `convenient`,
  `clean`, `elegant`, `slick` - name the concrete thing instead.
- `and friends`, `and so on`, `etc.` - name the category or add concrete items.
- Heavy noun-phrase subjects pointing at a previous claim: `the
  plain-HTTP contract is also why Lambda runs any language`. Use a
  pronoun pointing at the previous sentence: `This is why Lambda can
  run any language`.
- Colloquial or metaphorical verbs that have a plain alternative: `chunks land`
  (use `chunks arrive`), `load-bearing setting` (use `required`).
- Economic or transactional metaphors. Name the concrete result.
- Bare counts as list lead-ins: `Two reasons:`, `Three things:`,
  `Four points:`. The bullets already show their own count. Lead
  with the substantive claim the bullets support.
- `cut` as a noun (`the first cut of the code`, `a clean cut`). It
  reads as film/print jargon and the reader has to translate. Use
  `version`, `draft`, or `pass` instead: `the first version of the
  code`, `the first pass at the Dockerfile`. The verb form
  (`cut the sentence`) is fine.
- Nominalized actions and abstract subjects when `we`/`you` and a
  plain verb would do. `The next two prompts are corrections to fix
  both before the rest of the work continues` hides a direct
  instruction behind a noun phrase (`are corrections to fix`) and an
  abstract subject (`the rest of the work continues`). Rewrite with
  the actor and the action: `We need to fix both before we continue`.
  Same pattern: `An additional check is performed` becomes `We also
  check`; `The approach taken here is to` becomes `Here we`.

Ask whether the sentence describes what is happening or gestures at it.

## Judgment patterns

Watch for these judgment-only patterns:

- Words that are often filler but sometimes precise: `actually`, `just`, `key`,
  `highlight`, `boasts`, `underscore`.
- `Not X, but Y` / rule-of-three patterns used for rhythm.
- Abstract openers that announce the next move without adding information.
  Replace them with the concrete action.
- Sentence fragments for rhythm or emphasis. Use a subject and a verb.
- Jargon verbs and trade idioms that need decoding. Use plain words.
- Meta-narration of the document. Headings already tell the reader what
  is next.
- Sentences where a document or artifact is the subject of an action
  verb. Address the reader instead.
- Repeating a point you already made. Trust the reader to remember
  the previous sentence. Cut, do not rephrase.
- Do not anthropomorphize tools, products, projects, or frameworks.
  `The agent calls the search tool` is fine. `FastAPI asks the agent
  what it needs` is not. Same applies to project names: a project
  cannot "ask" or "answer". Describe what the project is and what it
  does directly.
- No editorializing unless the source said it. State the fact and move on.

## Address the reader, not "the user"

Write `you`, not `the user`.

## Define on first use

Define project-specific terms on first use. Tie the definition to what the
reader can or cannot do because of it.

## Repeat words rather than swap synonyms

Pick one name for a thing and stick with it. Do not rotate through `the tool`,
`the platform`, and `the solution` for variety.

## Trailing -ing clauses

Drop trailing abstract gerunds like `highlighting its importance`,
`reflecting the trend`, and `emphasizing the value`.

## Gender-neutral language

Use `person`, `someone`, and `they` for generic referents.

## Bridge sentences and section flow

Consecutive paragraphs that feel disconnected need a bridge or a restructure.
Subsections inside one section should relate to each other.

## Place content where it belongs

If you write a backward or forward reference, move the content.

## Punctuation inside quotes

Only put punctuation inside quotes when the quote is a full sentence.

## Wordy verb constructions

Collapse `have had... to` forms into the plain past or present:

- `I've had this idea for a long time to X` becomes `I wanted to X for
  a long time`.
- `I'd already described` becomes `I already described`.
- `I have been meaning to` becomes `I want to` or `I planned to`.

## Don't bury an idea in a bullet

Bullets are for scannable parallel items. If one bullet needs a paragraph,
pull it out into text.

## List vs sentence split: the parallel-completion test

When `stylint` flags a long comma sentence, use this test.

> Can you write a single lead-in line that all the items finish
> without re-introducing the subject or verb?

If yes, use a list.

> Five sponsors back the course: MongoDB, Comet, Opik, Unsloth and
> ZenML.

If no, split the sentence.

> Claude segmented the image, converted each piece to SVG, then
> assembled the result, which Codex later refined.

Bulleting a chain of actions makes the text feel robotic.

## Anti-duplication when expanding an overview

If an overview lists bullets and the body expands them, do not repeat the same
one-line description in both.

## "may need" vs "need"

Use `need` only for universal requirements. Use `may need` for conditional
ones.

## "do" for verb emphasis

Drop emphasis `do`: `Or you do start` becomes `Or you start`.

## Don't assume facts not in the source

If the source does not specify a fact or rationale, leave it out. Vague is
better than wrong.
