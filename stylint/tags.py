"""Rule tags emitted by stylint."""

from enum import Enum


class Tag(str, Enum):
    """All rule tags emitted by the linter. The string value is what
    appears between `[...]` in the formatted output and is what users
    pass to `--ignore`."""

    # Mechanical markdown
    BOLD = "bold"
    ITALIC = "italic"
    TABLES = "tables"
    HR = "hr"
    EM_DASH = "em-dash"
    DOUBLE_HYPHEN = "double-hyphen"
    DASH_PARENTHETICAL = "dash-parenthetical"
    SMART_QUOTES = "smart-quotes"
    BACKTICKS_IN_LINK = "backticks-in-link"
    BARE_URL = "bare-url"
    ANGLE_URL = "angle-url"
    FRONTMATTER_BLANK = "frontmatter-blank"
    BLOCKQUOTE_LONG = "blockquote-long"
    # Headings
    HEADING_QUESTION_WORD = "heading-question-word"
    HEADING_QUESTION_MARK = "heading-question-mark"
    HEADING_TOO_DEEP = "heading-too-deep"
    LAZY_HEADING = "lazy-heading"
    # Code blocks
    CODE_NO_LANG = "code-no-lang"
    CODE_TOO_LONG = "code-too-long"
    CONSECUTIVE_CODE = "consecutive-code"
    LEAD_IN = "lead-in"
    LEAD_IN_MULTI = "lead-in-multi"
    CHAINED_GET = "chained-get"
    DOUBLE_BLANK = "double-blank"
    # Banned tokens
    BANNED_WORD = "banned-word"
    BANNED_PHRASE = "banned-phrase"
    BANNED_OPENER = "banned-opener"
    # Voice / fragments
    THIRD_PERSON = "third-person"
    ANAPHORIC_NO = "anaphoric-no"
    SEMICOLON = "semicolon"
    CLEFT = "cleft"
    GERUND_OPENER = "gerund-opener"
    PAST_TENSE_FRAGMENT = "past-tense-fragment"
    # Paragraph / sentence shape
    PARAGRAPH_TOO_LONG = "paragraph-too-long"
    LONG_SENTENCE = "long-sentence"
    # Long sentence with commas, split by likely fix shape:
    LONG_LIST_LIKELY = "long-list-likely"
    LONG_CLAUSE_LIKELY = "long-clause-likely"
    MANY_COMMAS = "many-commas"
    COLON_INLINE = "colon-inline"
    PARALLEL_SENTENCES = "parallel-sentences"
    CHOPPY_RHYTHM = "choppy-rhythm"
    LABEL_COLON = "label-colon"
    META_FRAMING = "meta-framing"
    QUESTION_OPENER = "question-opener"
    REPEATED_AND = "repeated-and"
    # File-level
    NOW_LETS_OVERUSE = "now-lets-overuse"
    NOW_LETS_COMBO = "now-lets-combo"
