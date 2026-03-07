"""Colored terminal output helpers."""

import sys


def cprint(color: str, icon: str, msg: str) -> None:
    colors = {
        "g": "\033[92m", "r": "\033[91m", "y": "\033[93m",
        "b": "\033[94m", "c": "\033[96m", "w": "\033[0m",
    }
    code = colors.get(color, "")
    print(f"{code}{icon}  {msg}\033[0m", file=sys.stderr, flush=True)


def info(msg: str) -> None:
    cprint("c", "\u2139", msg)


def ok(msg: str) -> None:
    cprint("g", "\u2713", msg)


def warn(msg: str) -> None:
    cprint("y", "\u26a0", msg)


def err(msg: str) -> None:
    cprint("r", "\u2717", msg)


def mic(msg: str) -> None:
    cprint("r", "\U0001f399", msg)


def snd(msg: str) -> None:
    cprint("b", "\u2328", msg)
