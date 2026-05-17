"""Compiled patterns, thresholds, and rule data."""

import re


LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
QUESTION_HEADING_RE = re.compile(
    r"^#{1,6}\s+(Why|How|What|When|Where|Which|Who)\b"
)
# Allow-list for question-word headings that read as standard section
# names rather than rhetorical questions.
QUESTION_HEADING_ALLOWLIST = frozenset({
    "how it works",
})
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
DOUBLE_HYPHEN_RE = re.compile(r"(?<![<!/])--(?![/>])")
FOOTNOTE_DEF_RE = re.compile(r"^\s*\[\^[^\]]+\]:")
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
# Filler sentence-openers: "Now", "Let's", "Let us". Fine in moderation;
# overuse signals lazy transitions. Counted at file scope: flagged only
# when there are too many in a single document.
NOW_LETS_OPENER_RE = re.compile(r"(?:^|[.!?]\s+)(Now|Let's|Let us)\b")
NOW_LETS_MAX_PER_FILE = 4
# Redundant combos: "Now let's X" / "Let's now X". Almost always
# rewrite, regardless of count. The right rewrite depends on what
# follows:
#   - immediately before a code block: drop both softeners, use
#     the bare imperative ("Now let's run X." -> "Run X.").
#   - in a paragraph that explains rather than instructs: rewrite
#     declaratively ("Now let's use X." -> "We use X." or
#     "This lesson uses X.").
# Keeping just "Let's" is acceptable but not the preferred fix.
NOW_LETS_COMBO_RE = re.compile(
    r"(?:^|[.!?]\s+)(Now\s+let's|Let's\s+now)\b",
    re.IGNORECASE,
)

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
# conversion. The heuristic lives here (and not only in style-guide/polish.md)
# because agents reading the lint output often skip reference docs.
LIST_HEURISTIC_HINT = (
    "Convert to a bullet list only when BOTH (a) each item is 3+ words "
    "and items are parallel in structure, AND (b) the author already "
    "signalled enumeration (colon + items, or 3+ adjacent sentences "
    "with the same opener). Skip conversion when items end in "
    "'and others'/'and more'/'and so on', when commas are clausal "
    "(joining clauses, not items), or when inline reads fine."
)
# The parallel-completion test - the human-facing rule for deciding
# between bullet list and sentence split. The classifier
# (classify_long_with_commas in text.py) is just a hint; the rule below
# is what an editor actually applies.
PARALLEL_COMPLETION_TEST = (
    "Test: can you write a single lead-in line that all the commas "
    "finish without re-introducing the subject or verb? "
    "Yes -> bullet list. "
    "No -> split into 2-3 sentences."
)
# Open enumerations - "..., and others", "..., and so on", "etc.".
# These signal the writer intentionally left the list open, so the
# inline form is the right choice. Skip the long-and-commas fire here.
# Allow trailing footnote refs like [^12][^7] after the closer so the
# rule still fires on cited prose.
OPEN_ENUM_TAIL_RE = re.compile(
    r"(?:,\s+(?:and\s+)?(?:others|more|so\s+on)|\betc\.?)"
    r"(?:\s*\[\^[^\]]+\])*\s*[.!?]?\s*$",
    re.IGNORECASE,
)
# Footnote reference (Pandoc-style): [^1], [^abc]. Strip these before
# classifying long-and-commas so they don't break end-of-sentence anchors.
FOOTNOTE_REF_RE = re.compile(r"\[\^[^\]]+\]")
# Action-chain detection: 2+ comma chunks that start with a transitive
# verb sharing an elided subject ("you open X, pick Y, choose Z").
# These look list-shaped but are sequential actions; bulleting them
# reads as robotic. Classify as clause-likely so the fix is a split.
ACTION_CHAIN_VERBS = (
    r"pick|choose|select|find|get|take|give|send|receive|make|build|do|"
    r"create|delete|remove|add|edit|modify|change|replace|update|"
    r"click|press|type|drag|drop|copy|paste|save|load|"
    r"run|execute|install|uninstall|configure|set|test|debug|fix|"
    r"open|close|start|stop|end|finish|begin|continue|"
    r"write|read|parse|format|convert|transform|fetch|store|"
    r"ask|tell|say|show|hide|display|present|describe|explain|define|"
    r"think|consider|decide|plan|design|"
    r"deploy|ship|release|publish|"
    r"use|try|keep|wait|move|"
    r"correct|verify|validate|review|check"
)
ACTION_CHAIN_RE = re.compile(
    # Match the verb stem optionally followed by -s (3rd person), -ed
    # (past), or -ing (continuous), optionally preceded by a chunk
    # connector like "and"/"or"/"then". Catches "..., and checks X",
    # "..., extracts Y", "..., running Z".
    rf",\s+(?:and\s+|or\s+|then\s+|also\s+)?"
    rf"(?:{ACTION_CHAIN_VERBS})(?:s|es|ed|d|ing)?\s+",
    re.IGNORECASE,
)
# Irregular past-tense action verbs at chunk start. These don't fit
# the stem+suffix pattern above.
IRREGULAR_PAST_RE = re.compile(
    r",\s+(?:and\s+|or\s+|then\s+|also\s+)?"
    r"(?:ran|went|came|took|made|gave|sent|got|saw|said|"
    r"wrote|bought|sold|thought|brought|caught|taught|fought|sought|"
    r"found|kept|left|met|paid|built|spent|held|told|drew|grew|"
    r"knew|threw|flew|drove|broke|spoke|woke|chose|ate|drank|stole)\s+",
    re.IGNORECASE,
)
# Meta-framing: '[The/A/Another] <abstract noun> [of X] is that <claim>'.
# The writer announces the shape of the claim ('here comes an
# advantage / limitation / insight / trick') instead of just stating
# the claim. Same family as label-colon ('The problem: ...') but in
# sentence form with 'is that' as the marker. Fix: drop the framing
# noun phrase and lead with the actual claim.
META_FRAMING_NOUNS = (
    r"advantage|disadvantage|benefit|drawback|downside|upside|"
    r"limitation|restriction|constraint|"
    r"problem|issue|challenge|catch|gotcha|"
    r"point|idea|insight|takeaway|lesson|"
    r"trick|secret|magic|beauty|strength|elegance|simplicity|"
    r"power|value|virtue|"
    r"principle|intent|goal|reason|motivation|rationale|"
    r"difference|distinction|"
    r"hope|fear|"
    r"fact|truth|reality|thing|"
    r"key|core|gist|crux|essence"
)
META_FRAMING_RE = re.compile(
    r"(?i)\b(?:the|a|an|another|one)\s+"
    # 0-2 modifier tokens between the determiner and the framing noun
    # (e.g. 'a big advantage', 'another phone limitation', 'the key insight')
    r"(?:[A-Za-z][\w-]*\s+){0,2}"
    rf"(?:{META_FRAMING_NOUNS})"
    # optional qualifier: "of/about/with/between X (...)"
    r"(?:\s+(?:of|about|with|between|to|for|behind)\s+\S+(?:\s+\S+){0,4})?"
    r"\s+is\s+that\b"
)
# Generic verb-led chunk detector: a comma chunk that does NOT start
# with a determiner/pronoun/preposition is likely verb-led. This
# catches action chains the curated verb list misses (detects,
# extracts, calculates, summarises, ...). Used as a fallback signal.
NON_VERB_STARTERS = frozenset({
    "a", "an", "the", "this", "that", "these", "those",
    "my", "your", "his", "her", "its", "our", "their",
    "some", "any", "no", "every", "each", "all", "both",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "another", "such", "many", "few", "much", "little", "most",
    "of", "in", "on", "at", "to", "for", "by", "with", "from",
    "into", "onto", "through", "around", "over", "under", "above",
    "below", "between", "among", "during", "after", "before", "since",
    "though", "although", "while", "because", "if", "when", "where",
    "as", "than", "but", "or", "and", "so", "yet",
    "which", "that", "who", "whom", "whose", "what", "whatever",
    "however", "moreover", "additionally", "instead",
})
# Subordinating / coordinating conjunctions that appear AFTER a comma
# and signal a clause boundary (not a list item). When any of these
# follow a comma in a long-and-commas sentence, the right fix is a
# sentence split - bullets would butcher the meaning.
CLAUSE_MARKER_RE = re.compile(
    r",\s+(?:which|that|who|whom|whose|while|though|although|because|"
    r"since|but|however|so|when|if|then|after|before|where|whereas)\b",
    re.IGNORECASE,
)
# Colon precedes the comma run: "X includes A, B, and C". Strong
# signal the writer already framed the commas as enumeration.
COLON_BEFORE_COMMAS_RE = re.compile(r":\s+[^,.;:!?\n]+,")
# Terminal "and X" / "or X" closing an enumeration. Combined with 3+
# comma chunks, this is a list-shape closer.
TERMINAL_AND_OR_RE = re.compile(
    r",\s+(?:and|or)\s+[A-Za-z][^.!?\n]*[.!?]?\s*$",
    re.IGNORECASE,
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
