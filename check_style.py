#!/usr/bin/env python3
"""Check mechanical markdown style rules.

Add a banned word / phrase / opener to the lists below and the check picks
it up automatically. Each entry maps to a one-line guidance message so the
agent reading the failure knows how to fix it.

Usage:
    check_style.py                    # scan *.md recursively from cwd
    check_style.py path/to/file.md    # check one file
    check_style.py docs/ notes/       # check several dirs

Files and directories listed in a .prose-style-ignore file at the scan
root are skipped (one path per line, # for comments, glob patterns OK).
"""

import argparse
import fnmatch
from pathlib import Path
import re
import sys


LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
QUESTION_HEADING_RE = re.compile(
    r"^#{1,6}\s+(Why|How|What|When|Where|Which|Who)\b"
)
QUESTION_MARK_HEADING_RE = re.compile(r"^#{1,6}\s+.*\?\s*$")
DEEP_HEADING_RE = re.compile(r"^#{3,}\s")
ITALIC_RE = re.compile(
    r"(?<![\w*])\*[^*\s][^*]*\*(?![\w*])|(?<![\w_])_[^_\s][^_]*_(?![\w_])",
)
SMART_QUOTES = {
    "‘": "left smart single quote",
    "’": "right smart single quote",
    "“": "left smart double quote",
    "”": "right smart double quote",
}
BARE_URL_RE = re.compile(r"\bhttps?://")
ANGLE_URL_RE = re.compile(r"<https?://")
DOUBLE_HYPHEN_RE = re.compile(r"(?<!<)(?<!/)--(?!/)(?!>)")
DASH_PARENTHETICAL_RE = re.compile(
    r"[a-zA-Z]\s+-\s+.*?\s+-\s+[a-zA-Z]"
)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
# Sentence-start "No X, no Y..." anaphora — typical verbless rhetorical
# fragment like "No frameworks, no magic - just Python and an LLM."
# Also catches the lazy "There's no X, no Y" / "There is no..." /
# "There are no..." dodge, which keeps the same anaphora behind a thin
# subject+verb scaffold.
ANAPHORIC_NO_RE = re.compile(
    r"(?:^|[.!?]\s+)"
    r"(?:There(?:'s|\s+is|\s+are)\s+no|No)"
    r"\s+\w+(?:\s+\w+){0,2},\s+no\s+\w+"
)
# Label-colon paragraph openers: "The problem: ...", "Goal: ...",
# "Three reasons: ...". Polish.md explains: use colons only to introduce
# lists, not to label a chunk of prose. Requires 2+ words after the
# colon so single-link references like "Code: [notebook.ipynb](url)"
# don't trip the rule.
LABEL_COLON_OPENER_RE = re.compile(
    r"^(?:The\s+)?[A-Z][a-zA-Z]+(?:\s+[A-Za-z]+){0,2}:\s+\w+\s+\w"
)
# Single-word labels that work as callout / admonition blocks. Only
# `Note:` and `Important:` are exempt - other words ("Tip", "Warning",
# "Notice", etc.) read as ad-hoc labels and the rule still flags them.
CALLOUT_LABELS = frozenset({"note", "important"})
# Filler sentence-openers: "Now", "Let's", "Let us". Fine in moderation,
# overuse signals lazy transitions. Flagged at file scope when too many
# appear, or when two of them sit too close together.
NOW_LETS_OPENER_RE = re.compile(r"(?:^|[.!?]\s+)(Now|Let's|Let us)\b")
NOW_LETS_MAX_PER_FILE = 3
NOW_LETS_MIN_GAP_LINES = 30

# Paragraph opening with a rhetorical question, like "Why do we need
# search?" or "What does this mean?". Polish.md says: state the point
# directly instead.
PARAGRAPH_QUESTION_OPENER_RE = re.compile(
    r"^(?:Why|How|What|When|Where|Which|Who|Is|Are|Can|Could|Should|Will|Would|Do|Does|Did)\b[^.!?\n]*\?"
)
# Cleft "[This/That/It] is what X is/are about" - pointless abstract
# framing. Polish.md flags clefts as judgment; this specific variant is
# distinctive enough to script.
THIS_IS_WHAT_ABOUT_RE = re.compile(
    r"\b(?:This|That|It)\s+is\s+what\s+\w+(?:\s+\w+){0,3}\s+(?:is|are|was|were)\s+about\b"
)

# Lazy headings starting with "The X". Catches both the bare "## The
# problem" and the suffix form "## The RAG idea" / "## The chunking
# problem" - any heading that opens with "The" and contains one of these
# vague abstract nouns. Specific nouns are fine ("## The Function URL").
LAZY_HEADING_LABELS = (
    "problem", "issue", "challenge", "solution", "goal", "idea",
    "reason", "answer", "catch", "fix", "approach", "trick",
    "concept", "point", "result", "way", "story", "principle",
    "takeaway", "insight", "lesson",
)
LAZY_HEADING_RE = re.compile(
    r"^#{1,6}\s+The\s+.*?\b(?:"
    + "|".join(LAZY_HEADING_LABELS)
    + r")\b",
    re.IGNORECASE,
)

# Single banned tokens. Whole-word, case-insensitive in prose.
BANNED_WORDS: dict[str, str] = {
    "delve": "use 'look at' / 'dig into' / 'explore'",
    "crucial": "drop or use 'important' / 'essential'",
    "pivotal": "drop the puffery",
    "vibrant": "drop the puffery",
    "intricate": "use 'detailed' or rewrite",
    "garner": "use 'gather' / 'get'",
    "bolster": "use 'strengthen' / 'add'",
    "foster": "use 'build' / 'help'",
    "showcase": "use 'show'",
    "enhance": "use a specific verb (improve / add / extend)",
    "emphasize": "name the concrete thing",
    "leverage": "use 'use'",
    "multifaceted": "drop or use the concrete description",
    "realm": "drop the metaphor",
    "captivating": "drop the puffery",
    "elevate": "use 'raise' / 'improve'",
    "suddenly": "drop",
    "basically": "drop",
    "very": "drop",
    "really": "drop",
    "underneath": "use 'under the hood' / 'inside' / 'behind'",
    "surprisingly": "drop the editorializing",
    "remarkably": "drop the editorializing",
    "faithful": "drop the metaphor; describe the concrete match",
    "itself": "use sparingly; if it does not change the meaning, drop it",
}

# Multi-word banned phrases. Substring match, case-insensitive.
BANNED_PHRASES: dict[str, str] = {
    "in order to": "use 'to'",
    "this matters because": "give the concrete reason directly",
    "at this point": "use 'now' or cut",
    "this gives us": "use 'now we have' / 'we'll use'",
    "this is useful because": "name the use directly",
    "the point is": "rewrite around what the reader should learn",
    "the point of": "rewrite around what the reader should learn",
    "the intent is": "name the action directly; abstract opener",
    "the goal is": "state what we are doing, not the goal",
    "the idea is": "state the idea directly",
    "the short rule": "drop the preamble; state the rule",
    "the short answer": "drop the preamble; give the answer",
    "the longer answer": "drop the preamble; give the answer",
    "the long answer": "drop the preamble; give the answer",
    "the important difference": "rewrite as a direct contrast",
    "reference implementation": "use 'finished app' / 'example app' / 'working version'",
    "demo artifact": "name the file/app/output",
    "framework-agnostic": "use 'works across frameworks'",
    "direct command interception": "use 'run slash commands before the model sees them'",
    "further reading": "use 'to learn more'",
    "known-good version": "use 'working version'",
    "a clear pattern emerged": "drop the cliche",
    "here's the catch": "drop the cliche",
    "plot twist": "drop the cliche",
    "but there's a twist": "drop the cliche",
    "now for the fun part": "drop the cliche",
    "marks a pivotal moment": "drop the puffery",
    "a testament to": "drop the puffery",
    "reflects broader trends": "drop the puffery",
    "experts argue": "drop the vague attribution",
    "industry reports suggest": "drop the vague attribution",
    "the wider picture": "use a concrete pivot",
    "the bigger picture": "use a concrete pivot",
    "zooming out": "use a concrete pivot",
    "stepping back": "use a concrete pivot",
    "if you squint": "use a concrete pivot",
    "the bird's-eye view": "use a concrete pivot",
    "low-hanging fruit": "drop the idiom",
    "off the table": "say it directly",
    "at the end of the day": "drop the idiom",
    "cut to the chase": "drop the idiom",
    "the elephant in the room": "drop the idiom",
    "that bites us": "describe the event neutrally",
    "that bit me": "describe the event neutrally",
    "we got burned": "describe the event neutrally",
    "what follows is": "drop; let the headings show what is next",
    "in this section we will": "drop the meta-narration",
    "below you will find": "drop the meta-narration",
    "the next few paragraphs": "drop the meta-narration",
    "as we shall see": "drop the meta-narration",
    "for reasons that will become clear": "give the reason on the same line",
    "the single most": "drop the superlative",
    "the hardest part": "drop the superlative",
    "the trickiest step": "drop the superlative",
    "the key insight": "drop the editorializing",
    "the big idea is": "state the idea directly",
    "this is where it gets interesting": "drop the editorializing",
    "the shape of": "show the shape, do not announce it",
    "on the wire": "name the bytes/payload directly; 'on the wire' is network jargon",
    "out of the box": "describe the default behavior in plain words",
    "tight inner loop": "describe the actual workflow (rebuild time, edit-test cycle)",
    "tight loop": "describe the actual workflow (rebuild time, edit-test cycle)",
    "reusable principle": "name the workflow or habit directly",
    "serves as": "use 'is'",
    "stands as": "use 'is'",
    "diverse array": "drop the puffery",
    "commitment to excellence": "drop the puffery",
    "boasts a": "use 'has'",
    "let me tell you": "drop the filler",
    "let me explain": "drop the filler",
    "let me expand on": "drop the filler",
    "i want to be clear": "state the thing directly",
    "is a reminder that": "drop the abstract framing; state the point directly",
    "pull request ceremony": "drop the jargon noun",
    "one benefit of": "state the benefit directly",
    "on the table": "say it directly",
    "in action": "drop the cliche; describe what is actually happening",
    "the power of": "drop the abstract framing; describe what the design does",
    "the advantage of": "drop the abstract framing; name the concrete benefit",
    "the beauty of": "drop the puffery; describe the concrete property",
    "the magic of": "drop the puffery; describe the concrete mechanism",
    "the strength of": "drop the abstract framing; name the concrete property",
    "the elegance of": "drop the puffery; describe the concrete property",
    "the simplicity of": "drop the abstract framing; describe the concrete property",
    "the backbone of": "drop the metaphor; describe what the component actually does",
    "the heart of": "drop the metaphor; describe what the component actually does",
    "the core of": "drop the metaphor; describe what the component actually does",
    "the cornerstone of": "drop the metaphor; describe what the component actually does",
    "the foundation of": "drop the metaphor; describe what the component actually does",
    "works well": "drop the filler; name the concrete property that fits",
    "works great": "drop the filler; name the concrete property that fits",
    "fits well": "drop the filler; name the concrete property that fits",
    "suffer": "do not anthropomorphize - inanimate things don't suffer; "
               "describe what actually goes wrong "
               "('the answer is wrong', 'the latency doubles')",
}

# Sentence openers. Capitalized, must start the line (allowing optional list
# marker). Match is case-sensitive on the opener token itself.
BANNED_OPENERS: dict[str, str] = {
    "Additionally": "drop or rewrite",
    "Moreover": "drop or rewrite",
    "Furthermore": "drop or rewrite",
    "Notably": "drop or rewrite",
    "Importantly": "drop or rewrite",
    "Consequently": "drop or rewrite",
}
OPENER_RE = re.compile(
    r"^(?:[-*]\s+|\d+\.\s+)?(" + "|".join(re.escape(w) for w in BANNED_OPENERS) + r")\b"
)
WORD_RES: dict[str, re.Pattern[str]] = {
    word: re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
    for word in BANNED_WORDS
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check mechanical markdown style rules.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan. Defaults to the current directory.",
    )
    return parser.parse_args()


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text

    parts = text.split("---\n", 2)
    if len(parts) == 3:
        return parts[2]
    return text


def load_ignore_patterns(root: Path) -> list[str]:
    ignore_file = root / ".prose-style-ignore"
    if not ignore_file.is_file():
        return []
    patterns: list[str] = []
    for raw in ignore_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def is_ignored(rel: Path, patterns: list[str]) -> bool:
    rel_str = str(rel)
    for pattern in patterns:
        if fnmatch.fnmatch(rel_str, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in rel.parts):
            return True
    return False


def iter_markdown_pages(paths: list[Path]) -> list[tuple[Path, Path]]:
    """Return [(root, page)] pairs so error paths can stay relative to the scan root."""
    pages: list[tuple[Path, Path]] = []
    for p in paths:
        p = p.resolve()
        if p.is_file() and p.suffix.lower() == ".md":
            pages.append((p.parent, p))
        elif p.is_dir():
            ignore = load_ignore_patterns(p)
            for md in sorted(p.rglob("*.md")):
                rel = md.relative_to(p)
                if is_ignored(rel, ignore):
                    continue
                pages.append((p, md))
    return pages


def strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def strip_link_urls(line: str) -> str:
    return LINK_RE.sub(lambda match: match.group(1), line)


CODE_BLOCK_MAX_LINES = 40
HEADING_RE = re.compile(r"^#{1,6}\s")
LIST_RE = re.compile(r"^\s*[-*]\s|^\s*\d+\.\s")
BLOCKQUOTE_RE = re.compile(r"^\s*>")
PYTHON_CHAINED_GET_RE = re.compile(r"\.get\([^)]*\)\.get\(")
PARAGRAPH_MAX_SENTENCES = 5
SENTENCE_MAX_WORDS = 20
SENTENCE_MAX_COMMAS = 3
SENTENCE_END_RE = re.compile(r"[.!?](?=[\s\"')\]]|$)")
# Colon-introduced inline list with 3+ items and a terminal and/or.
# "We use these tools: numpy, pandas, scikit-learn, and matplotlib" -
# the colon signals enumeration intent, so the items should be bullets.
COLON_INLINE_LIST_RE = re.compile(
    r":\s+(?:[^,.;:!?\n]+,\s+){2,}(?:and|or)\s+[^.!?\n]+[.!?]?\s*$"
)
# Minimum consecutive sentences sharing a 2-word opener that triggers
# a "consider a bullet list" flag. Three is the smallest run that reads
# as repeated parallel structure rather than coincidence.
PARALLEL_SENTENCE_MIN_RUN = 3

# Shared decision hint embedded in error messages that suggest list
# conversion. The heuristic lives here (and not only in polish.md)
# because agents reading the lint output often skip reference docs.
LIST_HEURISTIC_HINT = (
    "Convert to a bullet list only when BOTH (a) each item is 3+ words "
    "and items are parallel in structure, AND (b) the author already "
    "signalled enumeration (colon + items, or 3+ adjacent sentences "
    "with the same opener). Skip conversion when items end in "
    "'and others'/'and more'/'and so on', when commas are clausal "
    "(joining clauses, not items), or when inline reads fine."
)
ABBREVIATION_RE = re.compile(
    r"\b(?:e\.g|i\.e|etc|vs|cf|Mr|Mrs|Ms|Dr|St|Jr|Sr|U\.S|U\.K|a\.m|p\.m|Inc|Ltd|Co)\.",
    re.IGNORECASE,
)
GERUND_NOUN_EXCEPTIONS = {
    "spring", "string", "building", "setting", "meeting",
    "heading", "wedding", "beginning", "ending", "standing",
    "wing", "sing", "ring", "king", "thing", "bring",
    "everything", "nothing", "something", "anything",
    "morning", "evening", "saying", "streaming",
}
# Participial phrases: -ing phrase, then COMMA, then a likely new subject.
# Matches "Reading through it, I noticed..." but not "Calling them works, but..."
# (the gerund-as-subject form, where the verb sits before the comma).
_PARTICIPIAL_TAIL = r"\b[^.!?]{0,150},\s+(?:I|we|you|they|he|she|it|the|a|an|this|that|these|those)\b"
GERUND_LINE_START_RE = re.compile(r"^([A-Z][a-z]{3,}ing)" + _PARTICIPIAL_TAIL)
GERUND_MIDLINE_RE = re.compile(r"[.!?]\s+([A-Z][a-z]{3,}ing)" + _PARTICIPIAL_TAIL)


def count_sentences(text: str) -> int:
    text = re.sub(r"`[^`]*`", " ", text)
    text = ABBREVIATION_RE.sub("", text)
    return len(SENTENCE_END_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    """Split prose into individual sentences (ignoring abbreviations and code)."""
    text = re.sub(r"`[^`]*`", " ", text)
    text = ABBREVIATION_RE.sub("", text)
    return [s.strip() for s in SENTENCE_END_RE.split(text) if s.strip()]


def count_words(text: str) -> int:
    """Count whitespace-delimited tokens that contain at least one word char."""
    return sum(1 for token in text.split() if re.search(r"\w", token))


def find_gerund_starts(plain: str) -> list[str]:
    flagged: list[str] = []
    line_match = GERUND_LINE_START_RE.match(plain.lstrip())
    if line_match and line_match.group(1).lower() not in GERUND_NOUN_EXCEPTIONS:
        flagged.append(line_match.group(1))
    for match in GERUND_MIDLINE_RE.finditer(plain):
        word = match.group(1)
        if word.lower() not in GERUND_NOUN_EXCEPTIONS:
            flagged.append(word)
    return flagged


def check_page(root: Path, path: Path) -> list[str]:
    errors: list[str] = []
    now_lets_hits: list[tuple[int, str]] = []
    text = path.read_text()
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3 and parts[2] and not parts[2].startswith("\n"):
            fm_close_line = parts[0].count("\n") + parts[1].count("\n") + 2
            errors.append(
                f"{rel}:{fm_close_line + 1}: insert a blank line between frontmatter and body"
            )
    body = strip_frontmatter(text)
    fm_lines = text.count("\n") - body.count("\n") if body != text else 0
    line_offset = fm_lines
    lines = body.splitlines()
    in_code = False
    code_lang = ""
    previous_code_block_end: int | None = None
    code_block_start: int | None = None
    code_block_line_count = 0
    last_heading_line: int | None = None
    seen_prose_since_heading = False
    previous_code_line_blank = False

    paragraph_lines: list[tuple[int, str]] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        start_line = paragraph_lines[0][0]
        joined_raw = " ".join(text for _, text in paragraph_lines)
        joined = strip_inline_code(strip_link_urls(joined_raw))
        joined_lower = joined.lower()

        sentence_count = count_sentences(joined)
        if sentence_count > PARAGRAPH_MAX_SENTENCES:
            errors.append(
                f"{rel}:{start_line}: paragraph has {sentence_count} sentences (max {PARAGRAPH_MAX_SENTENCES}); split into 2-4 sentence paragraphs"
            )

        sentences = split_sentences(joined)
        for sentence in sentences:
            wc = count_words(sentence)
            commas = sentence.count(",")
            too_long = wc > SENTENCE_MAX_WORDS
            too_many_commas = commas > SENTENCE_MAX_COMMAS
            if too_long and commas > 0:
                comma_word = "comma" if commas == 1 else "commas"
                errors.append(
                    f"{rel}:{start_line}: [long-and-commas] sentence has {wc} words and {commas} {comma_word}. "
                    f"Fixes: (1) split into shorter sentences; (2) convert to a bullet list. "
                    f"{LIST_HEURISTIC_HINT}"
                )
            elif too_long:
                errors.append(
                    f"{rel}:{start_line}: [long-sentence] sentence has {wc} words (max {SENTENCE_MAX_WORDS}). "
                    f"Fixes: (1) split into shorter sentences; (2) drop filler words; "
                    f"(3) convert to a list if you find embedded enumeration. {LIST_HEURISTIC_HINT}"
                )
            elif too_many_commas:
                errors.append(
                    f"{rel}:{start_line}: [many-commas] sentence has {commas} commas (max {SENTENCE_MAX_COMMAS}). "
                    f"Fixes: (1) convert to a bullet list; (2) split into shorter sentences. "
                    f"{LIST_HEURISTIC_HINT}"
                )
            if COLON_INLINE_LIST_RE.search(sentence):
                errors.append(
                    f"{rel}:{start_line}: [colon-inline] colon-introduced inline run of 3+ items. "
                    f"Fixes: (1) convert items to bullets; (2) drop the colon and let items flow as prose; "
                    f"(3) split the sentence in two. {LIST_HEURISTIC_HINT}"
                )

        # Parallel-sentence runs: 3+ adjacent sentences sharing a 2-word
        # opener almost always read better as bullets. Catches "The agent
        # does X. The agent does Y. The agent does Z." style prose-lists.
        def two_word_opener(s):
            words = s.split()
            return " ".join(words[:2]).lower() if len(words) >= 2 else ""

        prefixes = [two_word_opener(s) for s in sentences]
        run_start = 0
        for i in range(1, len(prefixes) + 1):
            same = (
                i < len(prefixes)
                and prefixes[i]
                and prefixes[i] == prefixes[run_start]
            )
            if not same:
                run_len = i - run_start
                if run_len >= PARALLEL_SENTENCE_MIN_RUN and prefixes[run_start]:
                    errors.append(
                        f"{rel}:{start_line}: [parallel-sentences] {run_len} consecutive sentences "
                        f"start with '{prefixes[run_start]}'. "
                        f"Fixes: (1) convert to a bullet list (strong signal: author wrote list shape "
                        f"in prose); (2) vary the sentence openers if the items aren't really parallel. "
                        f"{LIST_HEURISTIC_HINT}"
                    )
                run_start = i

        if LABEL_COLON_OPENER_RE.match(joined):
            label_before_colon = joined.split(":", 1)[0].strip().lower()
            if label_before_colon not in CALLOUT_LABELS:
                errors.append(
                    f"{rel}:{start_line}: [label-colon] paragraph opens with a "
                    "label-colon pattern ('The problem: ...', 'Goal: ...', "
                    "'What we want: ...'). "
                    "Fixes: (1) drop the label and state the point directly; "
                    "(2) rewrite as a sentence introducing the topic. "
                    "Exempt callouts: 'Note:' and 'Important:'."
                )
        if PARAGRAPH_QUESTION_OPENER_RE.match(joined):
            errors.append(
                f"{rel}:{start_line}: [question-opener] paragraph opens with a "
                "rhetorical question. "
                "Fixes: (1) drop the question and lead with the substantive "
                "claim it gestures at; (2) rewrite the answer as the opening "
                "sentence (e.g., 'Why do we need X?' -> 'X exists because...'); "
                "(3) keep the question only if a real reader is likely to ask "
                "exactly that wording."
            )

        for phrase, hint in BANNED_PHRASES.items():
            if phrase in joined_lower:
                already_flagged = any(
                    phrase in strip_inline_code(strip_link_urls(line)).lower()
                    for _, line in paragraph_lines
                )
                if not already_flagged:
                    errors.append(
                        f"{rel}:{start_line}: banned phrase '{phrase}' across lines ({hint})"
                    )

        for word in find_gerund_starts(joined):
            errors.append(
                f"{rel}:{start_line}: sentence opens with '-ing' word '{word}'; rewrite if it is a participial phrase"
            )

        paragraph_lines.clear()

    for line_no, line in enumerate(lines, start=1 + line_offset):
        stripped = line.strip()
        starts_fence = line.lstrip().startswith("```")

        if not in_code and previous_code_block_end is not None and stripped:
            if starts_fence:
                errors.append(
                    f"{rel}:{line_no}: consecutive code blocks need prose between them"
                )
            previous_code_block_end = None

        if starts_fence:
            flush_paragraph()
            if not in_code:
                fence_tail = line.lstrip()[3:].strip()
                if not fence_tail:
                    errors.append(
                        f"{rel}:{line_no}: code block missing language tag (use ```python, ```bash, ...)"
                    )
                if last_heading_line is not None and not seen_prose_since_heading:
                    errors.append(
                        f"{rel}:{line_no}: code block needs a lead-in sentence after the heading on line {last_heading_line}"
                    )
                code_lang = fence_tail.lower()
                code_block_start = line_no
                code_block_line_count = 0
                previous_code_line_blank = False
            else:
                if (
                    code_block_start is not None
                    and code_block_line_count > CODE_BLOCK_MAX_LINES
                ):
                    errors.append(
                        f"{rel}:{code_block_start}: code block has {code_block_line_count} lines (max {CODE_BLOCK_MAX_LINES}); split with prose"
                    )
                code_block_start = None
                code_lang = ""
            in_code = not in_code
            if not in_code:
                previous_code_block_end = line_no
            continue

        if in_code:
            code_block_line_count += 1
            if code_lang == "python":
                if PYTHON_CHAINED_GET_RE.search(line):
                    errors.append(
                        f"{rel}:{line_no}: chained .get(...).get(...) in example; access known keys directly"
                    )
                if line.strip() == "" and previous_code_line_blank:
                    errors.append(
                        f"{rel}:{line_no}: double blank line in code; use one blank line between definitions"
                    )
                previous_code_line_blank = line.strip() == ""
            continue

        if HEADING_RE.match(line):
            flush_paragraph()
            if QUESTION_HEADING_RE.match(line):
                errors.append(f"{rel}:{line_no}: avoid question-word headings")
            if QUESTION_MARK_HEADING_RE.match(line):
                errors.append(f"{rel}:{line_no}: heading ends with '?' (use a statement)")
            if DEEP_HEADING_RE.match(line):
                errors.append(f"{rel}:{line_no}: heading depth ### or deeper not allowed")
            if LAZY_HEADING_RE.match(line):
                errors.append(
                    f"{rel}:{line_no}: lazy heading 'The <problem|issue|...>'; "
                    "name what the section is actually about"
                )
            last_heading_line = line_no
            seen_prose_since_heading = False
            continue

        if not stripped:
            flush_paragraph()
        elif LIST_RE.match(line):
            flush_paragraph()
            if last_heading_line is not None and not seen_prose_since_heading:
                errors.append(
                    f"{rel}:{line_no}: list needs a lead-in sentence after the heading on line {last_heading_line}"
                )
                last_heading_line = None
            seen_prose_since_heading = True
        elif BLOCKQUOTE_RE.match(line) or line.startswith("|"):
            flush_paragraph()
            seen_prose_since_heading = True
        else:
            seen_prose_since_heading = True
            paragraph_lines.append((line_no, stripped))

        plain = strip_inline_code(strip_link_urls(line))
        plain_lower = plain.lower()

        if "**" in plain or "__" in plain:
            errors.append(f"{rel}:{line_no}: bold markdown is not used")
        if ITALIC_RE.search(plain):
            errors.append(f"{rel}:{line_no}: italic markdown is not used")
        if line.startswith("|"):
            errors.append(f"{rel}:{line_no}: markdown tables are not used")
        if line.strip() == "---":
            errors.append(f"{rel}:{line_no}: horizontal rules are not used")
        if "—" in line:
            errors.append(f"{rel}:{line_no}: use a hyphen instead of an em dash")
        if DOUBLE_HYPHEN_RE.search(plain):
            errors.append(f"{rel}:{line_no}: use a single hyphen, not '--'")
        if DASH_PARENTHETICAL_RE.search(plain) and not LIST_ITEM_RE.match(line):
            errors.append(
                f"{rel}:{line_no}: dash-enclosed parenthetical in prose; "
                "split into two sentences or simplify"
            )
        for char, name in SMART_QUOTES.items():
            if char in line:
                errors.append(f"{rel}:{line_no}: use straight quotes, not {name}")
        for match in LINK_RE.finditer(line):
            if "`" in match.group(1):
                errors.append(f"{rel}:{line_no}: do not put backticks inside link text")
        if "Alexey" in plain:
            errors.append(f"{rel}:{line_no}: avoid third-person presenter references")
        if ANAPHORIC_NO_RE.search(plain):
            errors.append(
                f"{rel}:{line_no}: 'No X, no Y' verbless fragment; "
                "rewrite by describing what is actually happening "
                "('Lambda boots only when a request arrives', "
                "'we skip the usual API Gateway'). Do NOT just prepend "
                "'There's' - that satisfies the regex but does not add "
                "information."
            )
        if ";" in plain:
            errors.append(
                f"{rel}:{line_no}: semicolon in prose; use two sentences instead"
            )
        if THIS_IS_WHAT_ABOUT_RE.search(plain):
            errors.append(
                f"{rel}:{line_no}: pointless cleft '[This/That/It] is what X is about'; "
                "state directly what X does or is"
            )
        for m in NOW_LETS_OPENER_RE.finditer(plain):
            now_lets_hits.append((line_no, m.group(1)))

        if BARE_URL_RE.search(plain):
            errors.append(f"{rel}:{line_no}: bare URL in prose; use [name](url)")
        if ANGLE_URL_RE.search(line):
            errors.append(f"{rel}:{line_no}: angle-bracket URL form not used; use [name](url)")

        for word, hint in BANNED_WORDS.items():
            if WORD_RES[word].search(plain):
                errors.append(f"{rel}:{line_no}: banned word '{word}' ({hint})")

        for phrase, hint in BANNED_PHRASES.items():
            if phrase in plain_lower:
                errors.append(f"{rel}:{line_no}: banned phrase '{phrase}' ({hint})")

        opener_match = OPENER_RE.match(line)
        if opener_match:
            opener = opener_match.group(1)
            errors.append(
                f"{rel}:{line_no}: banned opener '{opener}' ({BANNED_OPENERS[opener]})"
            )

    flush_paragraph()

    if len(now_lets_hits) > NOW_LETS_MAX_PER_FILE:
        lines = ", ".join(str(ln) for ln, _ in now_lets_hits)
        errors.append(
            f"{rel}: file uses {len(now_lets_hits)} 'Now' / 'Let's' "
            f"sentence-starters (max {NOW_LETS_MAX_PER_FILE}; lines {lines}); "
            "vary openers - try 'After that', 'Then', 'Next', or drop the "
            "softener entirely and use a bare imperative"
        )
    for (prev_line, prev_word), (this_line, this_word) in zip(now_lets_hits, now_lets_hits[1:]):
        gap = this_line - prev_line
        if 0 < gap < NOW_LETS_MIN_GAP_LINES:
            errors.append(
                f"{rel}:{this_line}: '{this_word}' opener only {gap} lines "
                f"after '{prev_word}' on line {prev_line}; "
                "try 'After that' / 'Then' / 'Next' or drop the softener"
            )

    return errors


def main() -> int:
    args = parse_args()
    paths = [Path(p) for p in args.paths]
    pages = iter_markdown_pages(paths)
    if not pages:
        print("No markdown files found.", file=sys.stderr)
        return 0

    errors: list[str] = []
    for root, page in pages:
        errors.extend(check_page(root, page))

    if errors:
        # Group errors by file. Each error string starts with the file
        # path followed by an optional ":<line>:". Print one header per
        # file so the agent can fix one file at a time.
        from collections import defaultdict
        grouped: dict[str, list[str]] = defaultdict(list)
        for error in errors:
            # error format: "<file>:<line>: <message>" or "<file>: <message>"
            head, _, rest = error.partition(":")
            grouped[head].append(rest.lstrip())
        def s(n: int, word: str) -> str:
            return f"{n} {word}{'' if n == 1 else 's'}"

        print(
            f"Style check failed ({s(len(errors), 'finding')} across "
            f"{s(len(grouped), 'file')}):"
        )
        for file_path in sorted(grouped):
            print(f"\n{file_path} ({s(len(grouped[file_path]), 'finding')}):")
            for msg in grouped[file_path]:
                print(f"  {msg}")
        return 1

    print(f"Style check passed ({len(pages)} file{'s' if len(pages) != 1 else ''}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
