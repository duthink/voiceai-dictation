"""Global hotkey listener using pynput."""

import sys
import threading
import time

from voiceai.log import err


# Supported toggle keys (pynput Key enum names)
_KEY_NAMES = [
    "scroll_lock", "pause",
    "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12",
]

DEBOUNCE_MS = 300


def start_listener(key_name: str, on_toggle) -> "keyboard.Listener":
    """
    Start a background keyboard listener that calls *on_toggle* when
    the named key is pressed.

    Parameters
    ----------
    key_name : str
        One of the supported key names (f1-f12, scroll_lock, pause).
    on_toggle : callable
        Zero-argument function invoked on each (debounced) key press.

    Returns
    -------
    pynput.keyboard.Listener
        The running listener (call ``.stop()`` to shut down).
    """
    from pynput import keyboard

    key_map = {name: getattr(keyboard.Key, name) for name in _KEY_NAMES}
    target = key_map.get(key_name.lower())
    if target is None:
        err(f"Unknown key: {key_name!r}. Supported: {', '.join(_KEY_NAMES)}")
        sys.exit(1)

    last_press = [0.0]

    def on_press(key):
        if key == target:
            now = time.time() * 1000
            if now - last_press[0] < DEBOUNCE_MS:
                return
            last_press[0] = now
            threading.Thread(target=on_toggle, daemon=True).start()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener
