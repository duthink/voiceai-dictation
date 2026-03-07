"""System-wide text injection via xdotool (X11) or ydotool (Wayland)."""

import os
import subprocess
import sys

from voiceai.log import ok, err, warn


def _cmd_exists(cmd: str) -> bool:
    return subprocess.run(
        ["which", cmd], capture_output=True,
    ).returncode == 0


class TextInjector:
    """
    Types text into the currently focused window.

    Auto-detects the display session and chooses the best tool:
      - X11:     xdotool (most reliable)
      - Wayland: ydotool (kernel-level uinput, works everywhere)
      - Fallback: xdotool (some Wayland compositors support XWayland)
    """

    def __init__(self) -> None:
        self.method = self._detect_method()
        ok(f"Text injection: {self.method}")

    def _detect_method(self) -> str:
        session = os.environ.get("XDG_SESSION_TYPE", "")
        if session == "x11" and _cmd_exists("xdotool"):
            return "xdotool"
        if _cmd_exists("ydotool"):
            return "ydotool"
        if _cmd_exists("xdotool"):
            return "xdotool"
        err("No text injection tool found! Install xdotool or ydotool.")
        sys.exit(1)

    def type_text(self, text: str) -> None:
        """Type *text* into the focused input field."""
        if not text.strip():
            return
        try:
            if self.method == "xdotool":
                subprocess.run(
                    ["xdotool", "type", "--clearmodifiers", "--delay", "12", "--", text],
                    timeout=10, check=True,
                )
            else:
                subprocess.run(
                    ["ydotool", "type", "--key-delay", "12", "--", text],
                    timeout=10, check=True,
                )
        except subprocess.TimeoutExpired:
            warn("Text injection timed out")
        except subprocess.CalledProcessError as exc:
            warn(f"Text injection failed: {exc}")
