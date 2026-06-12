"""User-editable hotwords file for Whisper decoder biasing."""

from pathlib import Path

HOTWORDS_FILE = Path.home() / ".config" / "voiceai" / "hotwords.txt"

_TEMPLATE = """\
# VoiceAI hotwords — one word or phrase per line.
# Lines starting with # are ignored.
# The app re-reads this file on every transcription — no restart needed.
#
# Examples:
#   VoiceAI
#   duthink
#   Placetime
#
VoiceAI
"""


def ensure_hotwords_file() -> Path:
    """Create the hotwords file with a template if it doesn't exist yet."""
    HOTWORDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HOTWORDS_FILE.exists():
        HOTWORDS_FILE.write_text(_TEMPLATE, encoding="utf-8")
    return HOTWORDS_FILE


def load_hotwords() -> str | None:
    """
    Read the hotwords file and return a comma-separated string suitable
    for faster-whisper's ``hotwords`` parameter, or None if the list is empty.
    """
    if not HOTWORDS_FILE.exists():
        return None
    words = []
    for line in HOTWORDS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            words.append(stripped)
    return ", ".join(words) if words else None
