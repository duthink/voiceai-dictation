"""Post-transcription find-and-replace corrections for known mis-transcriptions."""

import re
from pathlib import Path

CORRECTIONS_FILE = Path.home() / ".config" / "voiceai" / "corrections.txt"

_TEMPLATE = """\
# VoiceAI corrections — deterministic find-and-replace applied after transcription.
#
# Format:  wrong phrase = correct phrase
#
# - Left side (wrong): what Whisper actually outputs — case-insensitive match
# - Right side (correct): what you want injected — used exactly as written
# - Longer phrases are matched before shorter ones (no need to order manually)
# - Lines starting with # are ignored
#
# How to discover wrong transcriptions:
#   Watch the terminal output when you speak — the [chunk] lines show raw text.
#   Copy the wrong word/phrase to the left side, put the correct form on the right.
#
# Examples:
#   PingDink = pingd.in
#   ping dink = pingd.in
#   ping din = pingd.in
#   do think = duthink
#   new think = duthink
#   pictures = pingd.in

PingDink = pingd.in
ping dink = pingd.in
ping din = pingd.in
pictures = pingd.in
do think = duthink
new think = duthink
"""


def ensure_corrections_file() -> Path:
    """Create the corrections file with a template if it doesn't exist yet."""
    CORRECTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CORRECTIONS_FILE.exists():
        CORRECTIONS_FILE.write_text(_TEMPLATE, encoding="utf-8")
    return CORRECTIONS_FILE


def load_corrections() -> list[tuple[re.Pattern, str]]:
    """
    Read the corrections file and return compiled (pattern, replacement) pairs,
    sorted longest-match-first so multi-word phrases win over single words.
    """
    if not CORRECTIONS_FILE.exists():
        return []

    pairs: list[tuple[str, str]] = []
    for line in CORRECTIONS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        wrong, _, correct = stripped.partition("=")
        wrong = wrong.strip()
        correct = correct.strip()
        if wrong and correct:
            pairs.append((wrong, correct))

    # Longest wrong-phrase first — prevents short patterns eating multi-word matches
    pairs.sort(key=lambda p: len(p[0]), reverse=True)

    return [
        (re.compile(r"(?<!\w)" + re.escape(wrong) + r"(?!\w)", re.IGNORECASE), correct)
        for wrong, correct in pairs
    ]


def apply_corrections(text: str) -> str:
    """Apply all corrections from the corrections file to *text*."""
    for pattern, replacement in load_corrections():
        text = pattern.sub(replacement, text)
    return text
