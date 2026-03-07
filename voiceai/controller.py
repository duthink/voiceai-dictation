"""Dictation controller: orchestrates recording, transcription, dedup, and text injection."""

import threading
import time

from voiceai.config import SAMPLE_RATE, CHUNK_SECONDS, OVERLAP_SECONDS, LANGUAGE
from voiceai.dedup import strip_overlap
from voiceai.engine import WhisperEngine
from voiceai.injector import TextInjector
from voiceai.log import info, ok, mic, snd
from voiceai.recorder import AudioRecorder


class DictationController:
    """
    Toggle-key dictation with overlap-buffered chunked transcription.

    Workflow
    --------
    1. ``toggle()`` starts recording and launches a background chunk loop.
    2. Every *chunk_seconds*, accumulated audio (with overlap tail from the
       previous chunk) is transcribed.
    3. Word-level dedup removes any repeated prefix caused by the overlap.
    4. Only new words are injected into the focused text field.
    5. ``toggle()`` again stops recording and transcribes the remainder.
    """

    def __init__(
        self,
        engine: WhisperEngine,
        chunk_seconds: float = CHUNK_SECONDS,
        overlap_seconds: float = OVERLAP_SECONDS,
        language: str = LANGUAGE,
    ) -> None:
        self.engine = engine
        self.recorder = AudioRecorder()
        self.injector = TextInjector()
        self.chunk_seconds = chunk_seconds
        self.language = language
        self.overlap_samples = int(overlap_seconds * SAMPLE_RATE)

        self.active = False
        self._chunk_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._prev_text = ""
        self._toggle_lock = threading.Lock()

    # ── public API ──────────────────────────────────────────────────────

    def toggle(self) -> None:
        """Start dictation if idle, stop if recording."""
        with self._toggle_lock:
            if not self.active:
                self._start()
            else:
                self._stop()

    # ── internals ───────────────────────────────────────────────────────

    def _start(self) -> None:
        self.active = True
        self._stop_event.clear()
        self._prev_text = ""
        self.recorder.start()
        mic("RECORDING \u2014 speak now (press key again to stop)")

        self._chunk_thread = threading.Thread(target=self._chunk_loop, daemon=True)
        self._chunk_thread.start()

    def _stop(self) -> None:
        self.active = False
        self._stop_event.set()
        self.recorder.stop()
        info("Processing final audio...")

        if self._chunk_thread is not None:
            self._chunk_thread.join(timeout=5)

        remaining = self.recorder.get_audio_and_clear()
        if len(remaining) > 0:
            t0 = time.time()
            text = self.engine.transcribe(remaining, language=self.language)
            elapsed = time.time() - t0
            if text:
                clean = strip_overlap(self._prev_text, text)
                if clean:
                    self.injector.type_text(" " + clean)
                    snd(f"[final] ({elapsed:.1f}s): {clean}")

        self._prev_text = ""
        ok("STOPPED \u2014 press key to dictate again\n")

    def _chunk_loop(self) -> None:
        """Background loop: transcribe audio chunks with overlap context."""
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self.chunk_seconds)
            if self._stop_event.is_set():
                break
            if not self.recorder.has_audio():
                continue

            audio = self.recorder.get_audio_keeping_tail(self.overlap_samples)
            if len(audio) < SAMPLE_RATE * 0.5:
                continue

            t0 = time.time()
            full_text = self.engine.transcribe(audio, language=self.language)
            elapsed = time.time() - t0

            if full_text:
                clean = strip_overlap(self._prev_text, full_text)
                self._prev_text = full_text
                if clean:
                    self.injector.type_text(" " + clean)
                    snd(f"[chunk] ({elapsed:.1f}s): {clean}")
            else:
                self._prev_text = ""
