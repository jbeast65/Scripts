import re
from typing import Dict


PUNCTUATION_COMMANDS: Dict[str, str] = {
    "comma": ",",
    "period": ".",
    "full stop": ".",
    "question mark": "?",
    "exclamation point": "!",
    "colon": ":",
    "semicolon": ";",
    "dash": "—",
    "open quote": "\u201c",
    "close quote": "\u201d",
    "open paren": "(",
    "close paren": ")",
}


LINE_BREAK_COMMANDS: Dict[str, str] = {
    "new line": "\n",
    "new paragraph": "\n\n",
    "next line": "\n",
}


AUTOTEXT_MACROS: Dict[str, str] = {
    # Examples – customize to your practice
    "macro hip exam": (
        "Inspection reveals no deformity. Range of motion is full with flexion, extension, abduction, and adduction. "
        "Strength 5/5 in all groups. Negative impingement signs. Sensation intact."
    ),
    "macro shoulder exam": (
        "No visible atrophy. Full active and passive range of motion. Strength 5/5 in rotator cuff groups. "
        "Negative Hawkins and Neer tests."
    ),
    "macro knee plan": (
        "We discussed conservative management including activity modification, NSAIDs as tolerated, and physical therapy. "
        "Patient will follow up as needed."
    ),
}


def _apply_macros(text: str) -> str:
    lowered = text.lower()
    for trigger, expansion in AUTOTEXT_MACROS.items():
        if trigger in lowered:
            # Replace the trigger phrase with the expansion
            pattern = re.compile(re.escape(trigger), flags=re.IGNORECASE)
            text = pattern.sub(expansion, text)
    return text


def _apply_punctuation(text: str) -> str:
    # Replace isolated punctuation words with symbols
    def repl(match: re.Match[str]) -> str:
        cmd = match.group(0).lower()
        return PUNCTUATION_COMMANDS.get(cmd, cmd)

    # Word-boundary replacements
    if PUNCTUATION_COMMANDS:
        pattern = re.compile(r"\\b(" + "|".join(map(re.escape, PUNCTUATION_COMMANDS.keys())) + r")\\b", re.IGNORECASE)
        text = pattern.sub(repl, text)

    if LINE_BREAK_COMMANDS:
        lb_pattern = re.compile(r"\\b(" + "|".join(map(re.escape, LINE_BREAK_COMMANDS.keys())) + r")\\b", re.IGNORECASE)
        text = lb_pattern.sub(lambda m: LINE_BREAK_COMMANDS[m.group(0).lower()], text)

    # Normalize spaces around punctuation
    text = re.sub(r"\s+([,.;:!?])", r"\1 ", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text.strip()


def process_text_with_commands(text: str) -> str:
    if not text:
        return text
    text = _apply_macros(text)
    text = _apply_punctuation(text)
    return text

