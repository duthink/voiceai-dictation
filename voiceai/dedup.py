"""Word-level deduplication for overlap-buffered chunked transcription."""

import re

_PUNCT = re.compile(r"[^\w]")


def _norm(word: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    return _PUNCT.sub("", word).lower()


def strip_overlap(prev_text: str, new_text: str) -> str:
    """
    Remove the duplicate prefix from *new_text* that overlaps with *prev_text*.

    When audio chunks overlap, Whisper re-transcribes the shared segment.
    This function finds the longest suffix of *prev_text* that matches a
    prefix of *new_text* at the word level and strips it, so only genuinely
    new words remain.

    Parameters
    ----------
    prev_text : str
        The transcription from the previous chunk.
    new_text : str
        The transcription from the current (overlapping) chunk.

    Returns
    -------
    str
        *new_text* with any overlapping prefix removed.

    Examples
    --------
    >>> strip_overlap("can you hear what I'm trying", "what I'm trying to say")
    "to say"
    >>> strip_overlap("hello world", "something else entirely")
    "something else entirely"
    >>> strip_overlap("", "first chunk of text")
    "first chunk of text"
    """
    if not prev_text or not new_text:
        return new_text

    prev_words = [_norm(w) for w in prev_text.split()]
    new_norm = [_norm(w) for w in new_text.split()]
    new_orig = new_text.split()

    if not prev_words or not new_norm:
        return new_text

    best = 0
    limit = min(len(prev_words), len(new_norm), 12)

    for length in range(1, limit + 1):
        if prev_words[-length:] == new_norm[:length]:
            best = length

    if best > 0:
        remaining = new_orig[best:]
        return " ".join(remaining) if remaining else ""
    return new_text
