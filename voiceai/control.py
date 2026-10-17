"""Unix-socket control channel: an external hotkey script sends TOGGLE to start/stop dictation."""

import os
import socket
import threading


def start_control_server(on_toggle) -> socket.socket:
    """Listen on $XDG_RUNTIME_DIR/voiceai-toggle.sock and call *on_toggle* per TOGGLE datagram."""
    path = os.path.join(os.environ["XDG_RUNTIME_DIR"], "voiceai-toggle.sock")
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(path)
    os.chmod(path, 0o600)

    def run() -> None:
        while True:
            try:
                msg = server.recv(32)
            except OSError:
                break
            if msg == b"TOGGLE":
                threading.Thread(target=on_toggle, daemon=True).start()

    threading.Thread(target=run, daemon=True).start()
    return server
