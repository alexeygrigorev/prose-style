# Voice and tone

## Tone first

Write like you are explaining the work to a colleague. Keep it direct and
human. The reader is a developer trying to understand what to run and why it
matters.

> The finished app has two main files: `App.jsx` for the page shell and
> `SnakeGame.jsx` for the game logic.

Avoid stiff wording like "The implementation contains two primary artifacts."
Avoid loose wording like "The app is split into two bits."

Prefer reader-facing words.

- `run`, `call`, or `do`, not `execute` unless `execute` is the precise API
  or tool word
- `finished app`, `preview`, `file`, or `tool`, not `artifact`
- `code repo`, `final code`, or `working version`, not `reference
  implementation`

Some words depend on context:

- `workflow` is correct for Temporal, GitHub Actions, and named workflow terms.
  In normal text, prefer `flow`, `way of working`, or the action.
- `production` is a normal engineering word. Keep it when it names real
  production concerns. Replace it when the sentence only means "real",
  "larger", or "more complete".

## Voice rules

Technical write-ups are first-person walkthroughs.

- Use `I`, `you`, `we`, `let's`. No third-person framing. Do not refer to
  yourself by name.
- Use contractions: `it's`, `we'll`, `don't`, `I've`.
- Active voice. `Do this`, not `This should be done`.
- Be concrete. `Ask in Slack` beats `participate through question submission
  mechanisms`.
- Stitch contrasting sentences with `but`, `though`, or `yet` unless the ideas
  are independent.
- Prefer first-person `we use X` / `I add Y` over declarative
  third-person framings.
- Use present tense for the walkthrough. Write as if the reader is doing the
  work now: `we create`, `we run`, `the app shows`, `the agent calls`.
- Keep internal process out of published pages: transcripts, scratch files,
  `/tmp`, subagents, source-of-truth rules, and missing evidence.
- Cut streamy detail with no instructional value: typos, false starts,
  self-corrections, pauses, and asides explaining what was just said. Keep the
  command, prompt, gotcha, or reasoning the reader needs tomorrow.

Always explain why. Every design choice, helper, and new section needs the
reason, not just the fact. Ask why here, why this shape, and what breaks if we
skip it. Put the answer in the text.

Ground every why in a concrete reader benefit, not abstract virtue.

> We use `AsyncOpenAI` because the model response arrives as a live
> stream, not as one big finished string. The notebook listens to that
> stream event by event, so the async client is the natural fit.

## Source notes

When the source explains a choice, code behavior, or tradeoff, use that
explanation with light cleanup. Do not replace source text with invented text.

Match the source's intensity: keep `like`, `works`, and `simple` at the same
strength. When in doubt, copy the source.

Do not invent rationale. If the source has the why, quote or paraphrase close
to it. If not, find it elsewhere or leave it out.

## Content rules: include and leave out

Include these details.

- Every shell command the reader needs, in order.
- Every non-trivial code file, inline or linked.
- The `.env` layout and every env var that matters.
- Concrete versions (Python 3.14, Node 24, etc.) where they affect
  reproducibility.
- Concrete prices and tiers when the reader has to make a purchase decision
  (`$10/month Copilot Pro`, `$200/month Claude Code 20x Pro`). Note that
  these go stale - add the month and year.

Leave these out.

- Notes about how the write-up was produced.
- Personal in-jokes.
- Names of audience members unless attribution is load-bearing.
- Raw transcript paste-ins. Rework them and preserve the meaning.
