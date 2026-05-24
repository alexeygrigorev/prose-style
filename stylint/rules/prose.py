"""Prose shape rule patterns and thresholds."""

from ..patterns import (
    ANAPHORIC_NO_RE,
    CALLOUT_LABELS,
    CHOPPY_SENTENCE_MAX_WORDS,
    CHOPPY_SENTENCE_MIN_RUN,
    COLON_INLINE_LIST_RE,
    LABEL_COLON_OPENER_RE,
    LIST_HEURISTIC_HINT,
    META_FRAMING_RE,
    PARAGRAPH_MAX_SENTENCES,
    PARAGRAPH_QUESTION_OPENER_RE,
    PARALLEL_COMPLETION_TEST,
    PAST_TENSE_FRAGMENT_RE,
    REPEATED_AND_RE,
    PARALLEL_SENTENCE_MIN_RUN,
    SENTENCE_MAX_COMMAS,
    SENTENCE_MAX_WORDS,
    SHORT_LABEL_COLON_RE,
    THIS_IS_WHAT_ABOUT_RE,
    BANNED_PHRASES,
    BANNED_PHRASE_PATTERNS,
    NOW_LETS_COMBO_RE,
    NOW_LETS_OPENER_RE,
)
from ..models import Finding
from ..tags import Tag
from ..text import (
    classify_long_with_commas,
    count_sentences,
    count_words,
    find_gerund_starts,
    split_sentences,
    strip_double_quoted,
    strip_inline_code,
    strip_link_urls,
)

__all__ = [
    "ANAPHORIC_NO_RE",
    "CALLOUT_LABELS",
    "COLON_INLINE_LIST_RE",
    "LABEL_COLON_OPENER_RE",
    "LIST_HEURISTIC_HINT",
    "PARAGRAPH_MAX_SENTENCES",
    "PARAGRAPH_QUESTION_OPENER_RE",
    "PARALLEL_SENTENCE_MIN_RUN",
    "PAST_TENSE_FRAGMENT_RE",
    "SENTENCE_MAX_COMMAS",
    "SENTENCE_MAX_WORDS",
    "SHORT_LABEL_COLON_RE",
    "THIS_IS_WHAT_ABOUT_RE",
]


def _two_word_opener(sentence: str) -> str:
    words = sentence.split()
    return " ".join(words[:2]).lower() if len(words) >= 2 else ""


def check_paragraph(
    paragraph_lines: list[tuple[int, str]],
    rel,
    *,
    allow_questions: bool = False,
) -> tuple[list[Finding], int | None]:
    if not paragraph_lines:
        return [], None

    findings: list[Finding] = []
    start_line = paragraph_lines[0][0]
    joined_raw = " ".join(text for _, text in paragraph_lines)
    joined = strip_inline_code(strip_link_urls(joined_raw))
    joined_lower = joined.lower()

    if "?" in joined and not allow_questions:
        findings.append(
            Finding(
                rel,
                start_line,
                Tag.PROSE_QUESTION,
                "question in prose. In technical docs, use questions only "
                "in Q&A sections. Rewrite as a direct statement, move it "
                "under a Q&A heading, or ignore 'prose-question' for a real "
                "Q&A file",
            )
        )

    sentence_count = count_sentences(joined)
    if sentence_count > PARAGRAPH_MAX_SENTENCES:
        findings.append(
            Finding(
                rel,
                start_line,
                Tag.PARAGRAPH_TOO_LONG,
                f"paragraph has {sentence_count} sentences (max {PARAGRAPH_MAX_SENTENCES}); "
                "split into 2-4 sentence paragraphs",
            )
        )

    sentences = split_sentences(joined)
    for sentence in sentences:
        word_count = count_words(sentence)
        commas = sentence.count(",")
        too_long = word_count > SENTENCE_MAX_WORDS
        too_many_commas = commas > SENTENCE_MAX_COMMAS
        if too_long and commas > 0:
            comma_word = "comma" if commas == 1 else "commas"
            shape = classify_long_with_commas(sentence)
            if shape == "inline-ok":
                # Open enumeration (..., and others / etc.) - the
                # writer signalled the list is intentionally inline.
                # Don't flag.
                pass
            elif shape == "list":
                findings.append(
                    Finding(
                        rel,
                        start_line,
                        Tag.LONG_LIST_LIKELY,
                        f"sentence has {word_count} words and {commas} {comma_word}, "
                        "and the commas look like enumeration (colon or 'and X' closer). "
                        "Fix: convert the items to a bullet list. "
                        f"{PARALLEL_COMPLETION_TEST} {LIST_HEURISTIC_HINT}",
                    )
                )
            else:
                findings.append(
                    Finding(
                        rel,
                        start_line,
                        Tag.LONG_CLAUSE_LIKELY,
                        f"sentence has {word_count} words and {commas} {comma_word}, "
                        "and the commas look like clause boundaries (subordinating "
                        "conjunction, chain of actions, or mixed subjects). "
                        "Fix: split into 2-3 shorter sentences; do NOT convert to "
                        "bullets - that would break the meaning. "
                        f"{PARALLEL_COMPLETION_TEST}",
                    )
                )
        elif too_long:
            findings.append(
                Finding(
                    rel,
                    start_line,
                    Tag.LONG_SENTENCE,
                    f"sentence has {word_count} words (max {SENTENCE_MAX_WORDS}). "
                    "Fixes: (1) split into shorter sentences; (2) drop filler words; "
                    f"(3) convert to a list if you find embedded enumeration. {LIST_HEURISTIC_HINT}",
                )
            )
        elif too_many_commas:
            findings.append(
                Finding(
                    rel,
                    start_line,
                    Tag.MANY_COMMAS,
                    f"sentence has {commas} commas (max {SENTENCE_MAX_COMMAS}). "
                    "Fixes: (1) convert to a bullet list; (2) split into shorter sentences. "
                    f"{LIST_HEURISTIC_HINT}",
                )
            )
        if COLON_INLINE_LIST_RE.search(sentence):
            findings.append(
                Finding(
                    rel,
                    start_line,
                    Tag.COLON_INLINE,
                    "colon-introduced inline run of 3+ items. "
                    "Fixes: (1) convert items to bullets; (2) drop the colon and let items flow as prose; "
                    f"(3) split the sentence in two. {LIST_HEURISTIC_HINT}",
                )
            )

    prefixes = [_two_word_opener(sentence) for sentence in sentences]
    run_start = 0
    for i in range(1, len(prefixes) + 1):
        same = i < len(prefixes) and prefixes[i] and prefixes[i] == prefixes[run_start]
        if not same:
            run_len = i - run_start
            if run_len >= PARALLEL_SENTENCE_MIN_RUN and prefixes[run_start]:
                findings.append(
                    Finding(
                        rel,
                        start_line,
                        Tag.PARALLEL_SENTENCES,
                        f"{run_len} consecutive sentences start with '{prefixes[run_start]}'. "
                        "Fixes: (1) convert to a bullet list (strong signal: author wrote list shape "
                        "in prose); (2) vary the sentence openers if the items aren't really parallel. "
                        f"{LIST_HEURISTIC_HINT}",
                    )
                )
            run_start = i

    # Choppy rhythm: 3+ short sentences in a row read as staccato.
    # "Or hand them a new task. I don't have a lot of free time.
    # This is how I make more of it." -> combine: "I don't have a lot
    # of free time, so this is how I make more of it."
    short_flags = [count_words(s) <= CHOPPY_SENTENCE_MAX_WORDS for s in sentences]
    short_run_start = 0
    for i in range(1, len(short_flags) + 1):
        in_run = i < len(short_flags) and short_flags[i]
        if not in_run:
            run_len = i - short_run_start
            if run_len >= CHOPPY_SENTENCE_MIN_RUN and short_flags[short_run_start]:
                findings.append(
                    Finding(
                        rel,
                        start_line,
                        Tag.CHOPPY_RHYTHM,
                        f"{run_len} consecutive short sentences "
                        f"(<= {CHOPPY_SENTENCE_MAX_WORDS} words each). "
                        "The staccato rhythm reads worse than one or two joined "
                        "sentences. Fix: combine two of them with a conjunction "
                        "('so', 'because', 'and', 'but') or restructure as a "
                        "single longer sentence.",
                    )
                )
            short_run_start = i

    if LABEL_COLON_OPENER_RE.match(joined):
        label_before_colon = joined.split(":", 1)[0].strip().lower()
        if label_before_colon not in CALLOUT_LABELS:
            findings.append(
                Finding(
                    rel,
                    start_line,
                    Tag.LABEL_COLON,
                    "paragraph opens with a label-colon pattern "
                    "('The problem: ...', 'Goal: ...', 'What we want: ...'). "
                    "Fixes: (1) drop the label and state the point directly; "
                    "(2) rewrite as a sentence introducing the topic. "
                    "Exempt callouts: 'Note:' and 'Important:'.",
                )
            )
    if PARAGRAPH_QUESTION_OPENER_RE.match(joined):
        findings.append(
            Finding(
                rel,
                start_line,
                Tag.QUESTION_OPENER,
                "paragraph opens with a rhetorical question. "
                "Fixes: (1) drop the question and lead with the substantive "
                "claim it gestures at; (2) rewrite the answer as the opening "
                "sentence (e.g., 'Why do we need X?' -> 'X exists because...'); "
                "(3) keep the question only if a real reader is likely to ask "
                "exactly that wording.",
            )
        )

    for phrase, hint in BANNED_PHRASES.items():
        if phrase in joined_lower:
            already_flagged = any(
                phrase in strip_inline_code(strip_link_urls(line)).lower()
                for _, line in paragraph_lines
            )
            if not already_flagged:
                findings.append(
                    Finding(
                        rel,
                        start_line,
                        Tag.BANNED_PHRASE,
                        f"'{phrase}' across lines - {hint}",
                    )
                )

    for label, (pattern, hint) in BANNED_PHRASE_PATTERNS.items():
        if pattern.search(joined):
            already_flagged = any(
                pattern.search(strip_inline_code(strip_link_urls(line)))
                for _, line in paragraph_lines
            )
            if not already_flagged:
                findings.append(
                    Finding(
                        rel,
                        start_line,
                        Tag.BANNED_PHRASE,
                        f"'{label}' across lines - {hint}",
                    )
                )

    for word in find_gerund_starts(joined):
        findings.append(
            Finding(
                rel,
                start_line,
                Tag.GERUND_OPENER,
                f"sentence opens with '-ing' word '{word}'; rewrite if it is a participial phrase",
            )
        )

    for match in PAST_TENSE_FRAGMENT_RE.finditer(joined):
        verb = match.group(1)
        findings.append(
            Finding(
                rel,
                start_line,
                Tag.PAST_TENSE_FRAGMENT,
                f"sentence starts with past-tense action or participle '{verb}'. "
                "Add the actor ('I ran...', 'we add...'), rewrite in present tense, "
                "or rewrite the participle clause.",
            )
        )

    pending_multi_colon_line = start_line if len(sentences) >= 2 and joined.rstrip().endswith(":") else None
    return findings, pending_multi_colon_line


def check_prose_line(plain: str, line_no: int, rel) -> tuple[list[Finding], list[tuple[int, str]]]:
    findings: list[Finding] = []
    now_lets_hits: list[tuple[int, str]] = []
    if "Alexey" in strip_double_quoted(plain):
        findings.append(Finding(rel, line_no, Tag.THIRD_PERSON, "avoid third-person presenter references"))
    if ANAPHORIC_NO_RE.search(plain):
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.ANAPHORIC_NO,
                "'No X, no Y' verbless fragment. "
                "Rewrite by describing what is actually happening "
                "('Lambda boots only when a request arrives', "
                "'we skip the usual API Gateway'). Do NOT just prepend "
                "'There's' - that satisfies the regex but does not add information.",
            )
        )
    if ";" in plain:
        findings.append(Finding(rel, line_no, Tag.SEMICOLON, "semicolon in prose; use two sentences instead"))
    if THIS_IS_WHAT_ABOUT_RE.search(plain):
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.CLEFT,
                "pointless cleft '[This/That/It] is what X is about'; state directly what X does or is",
            )
        )
    for match in META_FRAMING_RE.finditer(plain):
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.META_FRAMING,
                f"meta-framing '{match.group(0).strip()}': the writer announces "
                "the shape of the claim ('here comes an advantage / limitation / "
                "insight / trick') instead of just stating it. Fix: drop the "
                "framing noun phrase and lead with the actual claim "
                "('A big advantage of Recorder is that it keeps recording' -> "
                "'Recorder keeps recording').",
            )
        )
    for match in REPEATED_AND_RE.finditer(plain):
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.REPEATED_AND,
                f"polysyndetic chain '{match.group(0).strip()}': three or more "
                "items joined by 'and' instead of commas. Fix: use the oxford "
                "comma form ('Claude Code, Codex and OpenCode'). Keep the "
                "repeated 'and' only when the rhythm is intentional (rare).",
            )
        )
    for match in NOW_LETS_OPENER_RE.finditer(plain):
        now_lets_hits.append((line_no, match.group(1)))
    for match in NOW_LETS_COMBO_RE.finditer(plain):
        findings.append(
            Finding(
                rel,
                line_no,
                Tag.NOW_LETS_COMBO,
                f"redundant '{match.group(1)}' pair - almost always rewrite. "
                "If the sentence immediately introduces a code block: drop both "
                "softeners and use the bare imperative ('Now let's run X.' -> 'Run X.'). "
                "If the sentence is explanatory (mid-paragraph, transition): "
                "rewrite declaratively ('Now let's use X.' -> 'We use X.' or "
                "'This lesson uses X.'). Keeping just 'Let's' is acceptable "
                "but not preferred.",
            )
        )
    return findings, now_lets_hits
