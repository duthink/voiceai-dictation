"""Word-level deduplication for overlap-buffered chunked transcription."""

import re
from difflib import SequenceMatcher

_PUNCT = re.compile(r"[^\w]")
_MAX_OVERLAP_WORDS = 12
_MAX_LEADING_JUNK = 2
_FUZZY_RATIO = 0.8
_FUZZY_MIN_LEN = 4


def _norm(word: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    return _PUNCT.sub("", word).lower()


def _same(a: str, b: str) -> bool:
    """Exact match, or near match for longer words (Whisper re-hears the overlap slightly differently)."""
    if a == b:
        return True
    if min(len(a), len(b)) < _FUZZY_MIN_LEN:
        return False
    return SequenceMatcher(None, a, b).ratio() >= _FUZZY_RATIO


def strip_overlap(prev_text: str, new_text: str) -> str:
    """
    Remove the prefix of *new_text* that repeats the tail of *prev_text*.

    Finds the longest suffix of *prev_text* matching a prefix of *new_text*
    word-by-word (case/punctuation-insensitive, tolerant of small spelling
    differences) and strips it.

    >>> strip_overlap("can you hear what I'm trying", "what I'm trying to say")
    'to say'
    >>> strip_overlap("hello world", "something else entirely")
    'something else entirely'
    """
    if not prev_text or not new_text:
        return new_text

    prev_words = [_norm(w) for w in prev_text.split()]
    new_orig = new_text.split()
    new_words = [_norm(w) for w in new_orig]

    limit = min(len(prev_words), len(new_words), _MAX_OVERLAP_WORDS)
    for length in range(limit, 0, -1):
        tail = prev_words[-length:]
        # Whisper often mis-hears the clipped first word of a chunk, so allow a little junk before the overlap.
        for skip in range(_MAX_LEADING_JUNK + 1):
            if skip and length < 2:
                break
            window = new_words[skip:skip + length]
            if len(window) == length and all(_same(a, b) for a, b in zip(tail, window)):
                return " ".join(new_orig[skip + length:])
    return new_text
