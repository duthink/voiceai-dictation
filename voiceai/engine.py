"""GPU-accelerated Whisper speech-to-text engine."""

import time

import numpy as np

from voiceai.config import SAMPLE_RATE, BEAM_SIZE, MODEL_NAME, COMPUTE_TYPE
from voiceai.log import info, ok


class WhisperEngine:
    """
    Wraps faster-whisper with the model kept resident in VRAM.

    The model is loaded once at init and reused for every transcription,
    giving sub-second latency on short audio chunks.
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        compute_type: str = COMPUTE_TYPE,
        device: str = "cuda",
        beam_size: int = BEAM_SIZE,
        use_vad: bool = True,
    ) -> None:
        self.beam_size = beam_size
        self.use_vad = use_vad

        info(f"Loading {model_name} ({compute_type}) on {device}...")
        t0 = time.time()
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
        ok(f"Model loaded in {time.time() - t0:.1f}s")

    def transcribe(self, audio_np: np.ndarray, language: str = "en") -> str:
        """
        Transcribe a numpy int16 audio array and return the text.

        Parameters
        ----------
        audio_np : np.ndarray
            Mono 16 kHz int16 audio samples.
        language : str
            BCP-47 language code.

        Returns
        -------
        str
            Transcribed text, or empty string if audio is too short / silent.
        """
        if len(audio_np) < SAMPLE_RATE * 0.3:
            return ""

        audio_f32 = audio_np.astype(np.float32) / 32768.0

        kwargs: dict = dict(
            beam_size=self.beam_size,
            language=language,
        )
        if self.use_vad:
            kwargs["vad_filter"] = True
            kwargs["vad_parameters"] = dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200,
            )

        segments, _ = self.model.transcribe(audio_f32, **kwargs)
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()
