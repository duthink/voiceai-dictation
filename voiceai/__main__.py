"""Entry point for ``python -m voiceai`` and the ``voiceai`` console script."""

import signal
import sys
import time

from voiceai import __version__
from voiceai.config import parse_args, OVERLAP_SECONDS
from voiceai.controller import DictationController
from voiceai.engine import WhisperEngine
from voiceai.hotkey import start_listener
from voiceai.log import info, ok


BANNER = f"""\
  \u256d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e
  \u2502  \U0001f399  VoiceAI Dictation v{__version__:<22s}  \u2502
  \u2502  Local \u00b7 Private \u00b7 GPU-Accelerated          \u2502
  \u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f"""


def main(argv=None) -> None:
    """CLI entry point."""
    args = parse_args(argv)

    print()
    print(BANNER)
    print()

    engine = WhisperEngine(
        model_name=args.model,
        compute_type=args.compute_type,
        device=args.device,
        beam_size=args.beam_size,
        use_vad=not args.no_vad,
    )
    controller = DictationController(
        engine=engine,
        chunk_seconds=args.chunk,
        overlap_seconds=args.overlap,
        language=args.lang,
    )
    listener = start_listener(args.key, controller.toggle)

    ok(f"Ready! Press [{args.key.upper()}] to toggle dictation")
    info(f"Chunk: {args.chunk}s | Overlap: {args.overlap}s | Model: {args.model} | Lang: {args.lang}")
    info("Focus any text box, press the key, and start speaking.")
    info("Press Ctrl+C to quit.\n")

    def shutdown(sig=None, frame=None):
        print()
        info("Shutting down...")
        if controller.active:
            controller._stop()
        listener.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
