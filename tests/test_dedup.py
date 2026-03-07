"""Tests for voiceai.dedup — word-level overlap stripping."""

import pytest
from voiceai.dedup import strip_overlap


class TestStripOverlap:
    def test_no_overlap(self):
        assert strip_overlap("hello world", "something new") == "something new"

    def test_simple_overlap(self):
        assert strip_overlap("can you hear what I'm trying", "what I'm trying to say") == "to say"

    def test_single_word_overlap(self):
        assert strip_overlap("the quick brown fox", "fox jumped over") == "jumped over"

    def test_full_overlap(self):
        assert strip_overlap("hello world", "hello world") == ""

    def test_empty_prev(self):
        assert strip_overlap("", "first chunk") == "first chunk"

    def test_empty_new(self):
        assert strip_overlap("previous chunk", "") == ""

    def test_both_empty(self):
        assert strip_overlap("", "") == ""

    def test_case_insensitive(self):
        assert strip_overlap("Hello World", "hello world and more") == "and more"

    def test_no_prev(self):
        assert strip_overlap(None, "some text") == "some text"  # type: ignore[arg-type]

    def test_long_overlap(self):
        prev = "one two three four five six seven eight"
        new = "five six seven eight nine ten"
        assert strip_overlap(prev, new) == "nine ten"

    def test_preserves_original_case(self):
        prev = "the quick brown"
        new = "The Quick Brown Fox Jumped"
        assert strip_overlap(prev, new) == "Fox Jumped"
