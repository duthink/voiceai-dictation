"""Microphone audio capture via sounddevice."""

import threading

import numpy as np
import sounddevice as sd

from voiceai.config import SAMPLE_RATE, CHANNELS, DTYPE
from voiceai.log import warn


class AudioRecorder:
    """
    Records audio from the default microphone using a callback stream.

    Audio frames are accumulated in an internal buffer and can be
    retrieved with or without clearing, supporting overlap-buffered
    chunked transcription.
    """

    def __init__(self) -> None:
        self._buffer: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._recording = False
        self._lock = threading.Lock()

    # ── lifecycle ───────────────────────────────────────────────────────

    def start(self) -> None:
        """Begin capturing audio."""
        with self._lock:
            self._buffer.clear()
            self._recording = True
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
            blocksize=int(SAMPLE_RATE * 0.1),  # 100 ms blocks
        )
        self._stream.start()

    def stop(self) -> None:
        """Stop capturing audio."""
        with self._lock:
            self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    # ── buffer access ───────────────────────────────────────────────────

    def get_audio_and_clear(self) -> np.ndarray:
        """Return all accumulated audio (int16, 1-D) and clear the buffer."""
        with self._lock:
            if not self._buffer:
                return np.array([], dtype=np.int16)
            audio = np.concatenate(self._buffer)
            self._buffer.clear()
        return audio.flatten()

    def get_audio_keeping_tail(self, keep_samples: int) -> np.ndarray:
        """
        Return all audio (int16, 1-D) but keep the last *keep_samples*
        in the buffer so the next chunk gets overlap context.
        """
        with self._lock:
            if not self._buffer:
                return np.array([], dtype=np.int16)
            audio = np.concatenate(self._buffer).flatten()
            if keep_samples > 0 and len(audio) > keep_samples:
                # Reshape to (N, 1) to match the 2-D frames from sounddevice
                self._buffer = [audio[-keep_samples:].reshape(-1, 1)]
            else:
                self._buffer.clear()
        return audio

    def has_audio(self) -> bool:
        with self._lock:
            return len(self._buffer) > 0

    # ── sounddevice callback ────────────────────────────────────────────

    def _callback(self, indata, frames, time_info, status) -> None:
        if status:
            warn(f"Audio stream: {status}")
        if self._recording:
            with self._lock:
                self._buffer.append(indata.copy())
