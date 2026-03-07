#!/usr/bin/env python3
"""
Quick self-test: verifies mic, GPU, Whisper model, and text injection.

Run:
    python -m voiceai.selftest
    # or
    voiceai-selftest
"""

import os
import subprocess
import sys
import time


def check(label: str, condition: bool, detail: str = "") -> bool:
    icon = "\033[92m\u2713\033[0m" if condition else "\033[91m\u2717\033[0m"
    extra = f" \u2014 {detail}" if detail else ""
    print(f"  {icon} {label}{extra}")
    return condition


def main() -> None:
    print("\n  VoiceAI Self-Test")
    print("  " + "\u2500" * 40)

    all_ok = True

    # 1. Python imports
    try:
        import sounddevice as sd  # noqa: F401
        import numpy as np  # noqa: F401
        from faster_whisper import WhisperModel  # noqa: F401
        from pynput import keyboard  # noqa: F401
        all_ok &= check("Python packages", True)
    except ImportError as exc:
        all_ok &= check("Python packages", False, str(exc))
        sys.exit(1)

    # 2. CUDA + float16
    try:
        import ctranslate2
        types = ctranslate2.get_supported_compute_types("cuda")
        has_fp16 = "float16" in types
        all_ok &= check("CUDA + float16", has_fp16, f"types: {types}")
    except Exception as exc:
        all_ok &= check("CUDA", False, str(exc))

    # 3. Microphone
    try:
        import sounddevice as sd
        import numpy as np
        audio = sd.rec(int(0.5 * 16000), samplerate=16000, channels=1, dtype="int16")
        sd.wait()
        peak = int(np.max(np.abs(audio)))
        all_ok &= check("Microphone", peak > 0, f"peak amplitude: {peak}")
    except Exception as exc:
        all_ok &= check("Microphone", False, str(exc))

    # 4. Text injection
    session = os.environ.get("XDG_SESSION_TYPE", "unknown")
    has_xdotool = subprocess.run(["which", "xdotool"], capture_output=True).returncode == 0
    has_ydotool = subprocess.run(["which", "ydotool"], capture_output=True).returncode == 0
    method = "xdotool" if (session == "x11" and has_xdotool) else ("ydotool" if has_ydotool else "none")
    all_ok &= check("Text injection", method != "none", f"{method} (session: {session})")

    # 5. Whisper model load + inference
    try:
        from faster_whisper import WhisperModel
        import numpy as np
        t0 = time.time()
        model = WhisperModel("distil-large-v3", device="cuda", compute_type="float16")
        load_time = time.time() - t0
        silence = np.zeros(16000, dtype=np.float32)
        segments, _ = model.transcribe(silence, beam_size=1, language="en")
        _ = list(segments)
        all_ok &= check("Whisper model", True, f"loaded in {load_time:.1f}s")
        del model
    except Exception as exc:
        all_ok &= check("Whisper model", False, str(exc))

    # 6. VRAM
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True,
        )
        all_ok &= check("GPU VRAM", True, result.stdout.strip())
    except Exception:
        pass

    print()
    if all_ok:
        print("  \033[92mAll checks passed! Run: voiceai\033[0m\n")
    else:
        print("  \033[91mSome checks failed. Fix the issues above.\033[0m\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
