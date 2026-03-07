"""Configuration constants and CLI argument parsing."""

import argparse

# ─── Defaults ───────────────────────────────────────────────────────────────

DEFAULT_KEY = "f9"
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"
CHUNK_SECONDS = 4
OVERLAP_SECONDS = 0.8
MODEL_NAME = "distil-large-v3"
COMPUTE_TYPE = "float16"  # DO NOT use int8 on RTX 50-series (Blackwell cuBLAS bug)
BEAM_SIZE = 5
LANGUAGE = "en"


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="voiceai",
        description="Local, privacy-first voice-to-text dictation for Linux.",
        epilog="Project: https://github.com/duthink/voiceai-dictation",
    )
    parser.add_argument(
        "--key", default=DEFAULT_KEY, metavar="KEY",
        help=f"Toggle key: f1-f12, scroll_lock, pause (default: {DEFAULT_KEY})",
    )
    parser.add_argument(
        "--chunk", type=float, default=CHUNK_SECONDS, metavar="SEC",
        help=f"Transcription chunk interval in seconds (default: {CHUNK_SECONDS})",
    )
    parser.add_argument(
        "--overlap", type=float, default=OVERLAP_SECONDS, metavar="SEC",
        help=f"Audio overlap between chunks in seconds (default: {OVERLAP_SECONDS})",
    )
    parser.add_argument(
        "--model", default=MODEL_NAME, metavar="NAME",
        help=f"Whisper model name (default: {MODEL_NAME})",
    )
    parser.add_argument(
        "--compute-type", default=COMPUTE_TYPE, metavar="TYPE",
        choices=["float16", "float32", "bfloat16", "int8", "int8_float16"],
        help=f"Compute type for inference (default: {COMPUTE_TYPE})",
    )
    parser.add_argument(
        "--lang", default=LANGUAGE, metavar="CODE",
        help=f"Language code for transcription (default: {LANGUAGE})",
    )
    parser.add_argument(
        "--beam-size", type=int, default=BEAM_SIZE, metavar="N",
        help=f"Beam size for decoding (default: {BEAM_SIZE})",
    )
    parser.add_argument(
        "--no-vad", action="store_true",
        help="Disable voice activity detection filter",
    )
    parser.add_argument(
        "--device", default="cuda", choices=["cuda", "cpu"],
        help="Inference device (default: cuda)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s 0.1.0",
    )
    return parser.parse_args(argv)
