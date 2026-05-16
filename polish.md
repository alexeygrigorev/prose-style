# Voice polish

Read this after the mechanical style pass (`check_style.py`). The script
catches banned tokens but not judgment-level prose problems. Re-read each
file with the patterns below in mind and rewrite anything that matches.

This pass usually changes more than the mechanical one. If a sentence
reads like an editor wrote it, rewrite it so it reads like the author.

## Plain words over abstractions

This is a technical document, not prose. Every sentence has to carry
information. If a sentence is ambiguous, gestures at meaning without
giving any, or could be cut without losing the point, cut it.

The audience is technical. Readers follow along with their own code
open in another window. They do not need literary devices, hedge
words, or abstract framings to navigate the page. Sentences should
describe what is happening directly, not gesture at it through
metaphors the reader has to translate first.

Patterns from past drafts and how to rewrite them:

- `the shape of X is...`, `the shape of every X is the same` -
  announces the shape instead of showing it. Use `This is what X
  looks like:` or just introduce the code with one direct sentence.
  See also "Abstract openers" in the banned-words list below.
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
  `clean`, `elegant`, `slick` - name the concrete thing instead. Not
  `it is fiddly`, but `you have to remember the right sequence`. Not
  `clean`, but `each script can be run on its own`.
- `and friends`, `and so on`, `etc.` at the end of an inline list -
  name the category if it is one (`and similar deployment commands`),
  or add one or two more concrete items.
- Heavy noun-phrase subjects pointing at a previous claim: `the
  plain-HTTP contract is also why Lambda runs any language`. Use a
  pronoun pointing at the previous sentence: `This is why Lambda can
  run any language`.
- Colloquial or metaphorical verbs and adjectives that have a plain
  alternative: `chunks land as they arrive` (use `chunks arrive`),
  `load-bearing setting` (use `essential` or `required`), `we drop in
  Y`, `we wire up Y`. If the metaphor is doing work the reader has to
  translate, use the plain word.
- Economic or transactional metaphors: `paying the redeploy
  round-trip`, `that buys us Y`, `the cost of doing X`. Use the
  action: `without redeploying`, `we get Y`.
- Cleft constructions that invert subject and complement: `What RIE
  does not have is the Function URL frontend`, `What we want is X`.
  Always use Subject-Verb-Object: `RIE does not have the Function URL
  frontend`, `We want X`.
- Bare counts as list lead-ins: `Two reasons:`, `Three things:`,
  `Four points:`. The bullets already show their own count. Lead
  with the substantive claim the bullets support, ending in a colon:
  `We run RIE because:` rather than `Two reasons:`. If you cannot
  write a substantive lead-in, the heading above the list is
  probably already the claim and the count phrase is filler.
- `let's X` / `let us X` as a softener. Drop it; the bare imperative
  remains. Keep `let's` only on the rare line where it carries
  meaning the imperative loses (a genuine "let us together decide
  between A and B").
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

When editing, ask: does this sentence describe what is happening, or
gesture at it? The first is workshop prose. The second makes the
reader work harder than they need to.

## Banned words and patterns

The mechanical token / phrase / opener lists are enforced by
`check_style.py` (`BANNED_WORDS`, `BANNED_PHRASES`,
`BANNED_OPENERS` near the top of the file). Run the script and fix
what it reports. Add new entries to the script, not to this doc.

The patterns below need judgment and are not in the script:

- `actually`, `just`, `key` (adj), `highlight`, `boasts`, `underscore` -
  banned in most uses but legitimate in some. If the word is the
  precise one (correcting a misconception, the main key in a dict, a
  code identifier), keep it.
- `execute` is fine for APIs, tool names, command names, and exact
  technical behavior (`execute_workflow`, `execute_command`, `your
  code executes the tool`). In ordinary prose, use `run`, `do`, or
  `call`.
- `Not X, but Y` / rule-of-three patterns used for rhythm.
- Abstract openers that announce the shape of what follows without
  adding information: `The first prompt sets the shape`, `The next
  move is...`, `First things first`, `With that out of the way`,
  `The idea is`. Replace with the concrete action.
- Sentence fragments for rhythm or emphasis. `Just a plain HTML page.
  No React.` are two fragments. Write `A plain HTML page is enough.
  React would be overkill`, or fold into one sentence. Same for
  trailing word fragments ("build something together, live") and
  hanging clauses ("Same approach, one difference"). Always use a
  subject and a verb. The script enforces one specific instance of
  this rule: the sentence-start anaphora `No X, no Y...` (as in
  `No frameworks, no magic - just Python and an LLM`). The general
  verbless-fragment case is still judgment.
- Jargon verbs and trade idioms that the reader has to decode:
  `pin the folder`, `wire up X`, `bake it in`, `slot in`,
  `on the wire`, `out of the box`, `out of band`, `in the wild`.
  Prefer plain words: `name the folder in the prompt`,
  `connect X to Y`, `include it in the build`, `drop it in`. For the
  noun-phrase idioms, name what they actually mean in the sentence:
  `on the wire` becomes `in the response bytes` or `over the
  connection`; `out of the box` becomes `by default`; `in the wild`
  becomes `in real deployments`.
- Meta-narration of the document itself beyond what the script
  catches. Headings and visible content already tell the reader what
  is next.
- Sentences where a document or artifact is the subject of an action
  verb: `Full sources live in the reference repo`, `The fragments
  below cover only...`. Address the reader instead.
- Repeating a point you already made. Trust the reader to remember
  the previous sentence. Cut, do not rephrase.
- Do not anthropomorphize tools, products, projects, or frameworks.
  `The agent calls the search tool` is fine. `FastAPI asks the agent
  what it needs` is not. Same applies to project names: a project
  cannot "ask" or "answer". Describe what the project is and what it
  does directly.
- No subjective editorializing or dramatic superlatives unless the
  source actually said them. State the fact and move on.

## Address the reader, not "the user"

Write `you`, not `the user`. `A user sends a message on Telegram`
becomes `You send a message on Telegram`. `The user swaps providers`
becomes `You can swap providers`. The reader is the user; addressing
them in third person reads as a product spec, not a tutorial.

## Define on first use

When introducing a technical or project-specific term (`frozen
identity`, `manifest-first`, `hub-and-spoke`), define it briefly in
plain language on first use. Tie the definition to what the reader
can or cannot do because of it. For example: `Frozen identity means
you cannot change the system prompt mid-conversation; mutable identity
means you can.` Assume general software-engineering knowledge but
not familiarity with the project's docs.

## Repeat words rather than swap synonyms

Pick one name for a thing and stick with it. Referring to the same
project as `the tool`, `the platform`, and `the solution` across
three paragraphs reads as variety-for-variety's-sake and forces the
reader to reconfirm what each label points at. Repetition is not a
prose flaw in technical writing.

## Trailing -ing clauses

Sentences that end with `...highlighting its importance`,
`...reflecting the growing trend`, `...emphasizing the value` close
with an abstract gerund clause that adds no information. Drop the
clause, or rewrite the point as a finite verb in its own sentence.
The script catches `-ing` sentence *openers*; the trailing form
needs judgment.

## Gender-neutral language

Use `person`, `someone`, `they` instead of `guy`, `man`, `he` when
the referent is generic. `marketing person`, not `marketing guy`.
`a developer wants to know what they ship`, not `what he ships`.

## Bridge sentences and section flow

Consecutive paragraphs that feel disconnected need a bridge sentence
or a restructure. For long pieces, open with a short map of what is
coming - which sections cover which groups of things and how they
relate. When moving between sections, add one sentence that reminds
the reader where they are and what comes next. Sub-sections inside
a section should relate to each other, not read as separate
fragments.

## Place content where it belongs

A paragraph that answers "why something new" goes in that section,
not in "the problem". If you find yourself writing "as I mentioned
above" or "as I'll cover below", the content is probably in the
wrong section - move it.

## Punctuation inside quotes

Only put punctuation inside the quotes when the quote is a full
sentence. `Use "platform".` (the period belongs to the sentence,
not the word). `She said, "the deploy worked."` (the period belongs
to the quoted sentence).

## Cleft variants ending with "is what you'll"

The script-catchable cleft form is `What we want is X`. The trailing
form is `X is what you'll do`: `Scripts are what you'll write for
most of the course` becomes `You'll write a lot of scripts in this
course`. Same fix - put the subject and verb in their natural order.

## Wordy verb constructions

Collapse `have had... to` forms into the plain past or present:

- `I've had this idea for a long time to X` becomes `I wanted to X for
  a long time`.
- `I'd already described` becomes `I already described`.
- `I have been meaning to` becomes `I want to` or `I planned to`.

## Don't bury an idea in a bullet

Bullets are for scannable parallel items. If one bullet needs a
paragraph of explanation to land, pull it out of the list into
prose, give it its own short paragraph or subsection, and leave the
list to the items that actually fit a one-line form.

## Anti-duplication when expanding an overview

When the overview lists bullets and the body then expands each one,
the overview is a table of contents - it names the items. The
expanded section adds new detail. Do not repeat the same one-line
description in both. If the expanded section says nothing the
overview did not already say, cut the expansion.

## "may need" vs "need"

`You need to install X` is presumptuous if the dependency only
applies in some setups. `You may need to install X` is more accurate
when the requirement is conditional. Use `need` when the requirement
is universal; otherwise hedge.

## "do" for verb emphasis

`Or you do start at the README` reads as awkward in written prose.
Drop the `do`: `Or you start at the README`. The `do` was meaningful
in speech for emphasis; on the page it just slows the sentence down.

## Don't assume facts not in the source

If the source does not specify the platform (Slack vs. Discord), the
version, or the name, leave it unspecified. Better vague than wrong.
Guessing creates content that drifts from reality and propagates
once published. The same rule applies to rationale - if you cannot
find why a choice was made, leave the why out rather than invent one.
