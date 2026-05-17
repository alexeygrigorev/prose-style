# Voice and tone

Read this when writing or editing prose in any technical document.

## Tone first

Write like you are explaining the work to a colleague on your team. The tone
is informal, but not colloquial. It should sound like a practical work
conversation: direct, clear, and human, without academic distance or internet
slang.

The reader is not an academic reviewer and not a stranger reading a white
paper. They are a developer trying to understand what to run, what to look at,
and why the step matters.

Good default:

> The finished app has two main files: `App.jsx` for the page shell and
> `SnakeGame.jsx` for the game logic.

Too formal: "The reference implementation contains two primary artifacts."
Too colloquial: "The app is basically split into two bits."

Use plain reader-facing verbs:

- `check`, `see`, `take a look`, or `look at`, not `inspect`
- `run`, `call`, or `do`, not `execute` unless `execute` is the precise API
  or tool word
- `under the hood`, `behind`, or `inside`, not `underneath` or `at the core`
- `To learn more`, not `For follow-up reading`
- `finished app`, `preview`, `file`, or `tool`, not `artifact`
- `code repo`, `final code`, or `working version`, not `reference
  implementation`

The script (`stylint`) catches mechanical banned phrases via
its `BANNED_PHRASES` list. This doc lists only the judgment calls.

The rule is not to ban every technical word. Use judgment:

- `workflow` is correct for Temporal, GitHub Actions, and named workflow
  concepts. In normal prose, prefer `flow`, `way of working`, or a direct
  rewrite around the action.
- `execute` is correct for APIs, method names, tool names, and exact
  tool-call behavior. In normal prose, prefer `run`, `call`, `do`, or `use`.
- `production` is a normal engineering word. Keep it when it names real
  production concerns. Replace it when the sentence only means "real",
  "larger", or "more complete".

## Voice rules

Technical write-ups are conversational and first-person, written as if the
author is walking the reader through a screen-share. The essentials:

- Use `I`, `you`, `we`, `let's`. No third-person framing. Do not refer to
  yourself by name ("Alexey used...", "Alexey's prompt"). The reader does
  not care who typed what. They care about what to do next.
- Use contractions: `it's`, `we'll`, `don't`, `I've`.
- Short sentences for emphasis. Mix with medium ones for flow. Keep
  paragraphs to 2-4 sentences. Anything longer is a wall of text and
  should be split at the next topic boundary. A six-sentence paragraph
  comparing two concepts splits cleanly into three. Splitting costs
  nothing and gives the reader a breath between ideas.
- Prefer lists over prose for enumerations of three or more parallel
  items, or for short steps the reader will want to scan. Lead with
  a sentence ending in a colon, then bullet the items, then resume
  the paragraph. Two-item enumerations that read fine inline
  ("we use Vite for the frontend and uv for Python packaging") stay
  inline. But when each item is a full sentence or longer, use a
  list even for two items. A two-bullet list with a colon lead-in
  reads as scannable; running the same content as prose reads as a
  wall.
- Block elements need a blank line above them. Code blocks, bulleted
  and numbered lists, Mermaid diagrams, and blockquotes all need a
  blank line between them and any prose above. The lead-in sentence
  that introduces a block (a sentence ending in a colon, like "The
  prompt I sent:") is its own paragraph: blank line above it, blank
  line between it and the block. Running a prose paragraph directly
  into a lead-in or directly into a block produces a wall of text
  where the eye expects a break.
- Active voice. `Do this`, not `This should be done`.
- Be concrete. `Ask in Slack` beats `participate through question submission
  mechanisms`.
- Stitch contrasting sentences with `but`. Two flat sentences that are
  in contrast drop the signal: `The architecture was right. The first
  version had problems.` Rewrite as `The architecture was right, but
  the first version had problems.` Same idea for `though` and `yet`.
  Leave them as separate sentences only when the ideas are genuinely
  independent.
- Do not lead a sentence with an `-ing` participial phrase. `Reading
  through it, I would simplify` and `Starting from a draft is faster`
  delay the subject and read formally. Rewrite with a finite verb:
  `I read through it and simplify` or `I prefer to start from a
  draft because...`. Gerunds as plain noun subjects are fine
  (`Streaming arrives token by token`), it is the participial
  opener that reads off.
- Prefer first-person `we use X` / `I add Y` over declarative
  third-person framings. `The frontend is the same Vite app` becomes
  `We use the same Vite app`. The walkthrough voice is conversational;
  the third-person form reads like a textbook.
- Use present tense for the walkthrough. Write as if the reader is doing the
  work now: `we create`, `we run`, `the app shows`, `the agent calls`.
  Use past tense only for historical facts that are not part of the reader's
  workflow.
- Open with a natural reader-facing intro, not a meta note. The first
  paragraph should say what the reader will build, compare, or look at. Do
  not open with labels like `Scope`, `Source material`, or
  `This write-up is based on...`.
- Keep internal process out of published pages. Do not mention that you used
  a transcript, local scratch files, `/tmp` paths, subagents, source-of-truth
  rules, or missing evidence. Turn those into reader-facing prose, or cut
  the sentence if it only explains how the document was produced.
- Cut streamy detail with no instructional value. The output is a curated
  document, not a transcription. Typos and self-corrections, false starts,
  mid-sentence pauses, and parenthetical asides explaining what was just said
  are noise to a later reader. Cut them. Keep the actual command or prompt
  the reader needs, the gotcha that explains a real workaround, and the
  reasoning that justifies a non-obvious choice. Test: would a reader
  following this tomorrow benefit from this detail? If not, drop it.
Always explain why. Every design choice, every extracted helper, every
new section needs the reason, not just the fact. A reader who only
learns what code exists cannot adapt it to their own project; a reader
who understands why the choice was made can. Before writing a step,
ask yourself: why are we doing this here rather than somewhere else,
why this shape rather than a simpler one, and what would go wrong if
we skipped it? The answers go into the prose, not into the reader's
head.

Ground every why in a concrete reader benefit, not abstract virtue.

> We use `AsyncOpenAI` because the model response arrives as a live
> stream, not as one big finished string. The notebook listens to that
> stream event by event, so the async client is the natural fit.

If you find yourself writing "let's extract X" or "here's a helper" or
"we split this into Y files", add the reason in the same breath: what
does the extraction buy us, why now, what would the alternative cost.

## When you have a source (transcript, interview, voice note)

When the source explained something - why a choice was made, what a
piece of code does, what the tradeoffs are - pull that explanation
from the source and use it, with light cleanup for dictation
artifacts. Do not write your own prose when the source's prose
exists. The source's phrasing carries expertise and tone that
synthesized explanations do not.

Match the intensity of the source's words. `like` / `don't like`
stays `like` / `don't like` - do not inflate to `love` / `hate`.
`works` / `doesn't work` stays that way - do not inflate to
`nails it` / `falls apart`. `simple` stays `simple` - do not inflate
to `elegant`, `beautiful`, or `powerful`. This kind of inflation
creeps in whenever you paraphrase instead of quoting. The source
sounds off because the voice is now slightly bigger than they are.
When in doubt, copy the source.

Do not invent rationale. Every "why" sentence in the write-up is a
claim about what the source thought. If the source has the rationale,
quote it or paraphrase close to it. If the source does not, either
find it elsewhere, or leave the rationale out. Writing something like
"Typing this command every time is fine once, annoying twice, and a
liability when we later want it in Docker and CI" when all the source
actually said was "I don't want to memorize these commands" puts
words in the source's mouth. The fabricated reason sounds smarter
and may even be true, but it is not theirs.

## Content rules: include and leave out

Include:

- Every shell command the reader needs, in order.
- Every non-trivial code file, either inline or via a link to the source repo.
  Prefer inline for anything under ~40 lines.
- The `.env` layout and every env var that matters.
- Concrete versions (Python 3.14, Node 24, etc.) where they affect
  reproducibility.
- Concrete prices and tiers when the reader has to make a purchase decision
  (`$10/month Copilot Pro`, `$200/month Claude Code 20x Pro`). Note that
  these go stale - add the month and year.

Leave out:

- Meta-commentary about the content creation process (`this section was
  consolidated from the video`, `we'll iterate on this`).
- Notes about how the write-up was produced.
- Personal in-jokes.
- Names of audience members unless attribution is load-bearing.
- The author's name as a third-person subject. Use `I` instead. "Alexey
  switched to `gpt-5.4-mini`" becomes "I switched to `gpt-5.4-mini`".
- Raw transcript paste-ins. Speech is full of `so`, `um`, and backtracks.
  If one line captures the reason behind a choice, quote that line. Do not
  paste the surrounding paragraph with it.
