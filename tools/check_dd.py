#!/usr/bin/env python3
"""Fail on non-ASCII or unknown DuckyScript keywords in payloads/*.dd"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAYLOADS = ROOT / "payloads"

PREFIXES = (
    "REM", "DELAY", "DEFAULT_DELAY", "DEFAULTDELAY", "STRINGLN", "STRING",
    "MOUSE_MOVE", "MOUSE_CLICK", "WAIT_FOR_CAPS_ON", "WAIT_FOR_CAPS_OFF",
    "IF_WIN", "IF_MAC", "IF_LINUX", "IF_ANDROID", "END_IF",
)
KEYWORDS = {
    "ENTER", "WINDOWS", "GUI", "COMMAND", "CTRL", "CONTROL", "ALT", "OPTION",
    "SHIFT", "ESCAPE", "ESC", "TAB", "SPACE", "BACKSPACE", "DELETE",
    "UP", "DOWN", "LEFT", "RIGHT", "UPARROW", "DOWNARROW", "LEFTARROW", "RIGHTARROW",
    "HOME", "END", "PAGEUP", "PAGEDOWN", "CAPSLOCK",
    "EQUAL", "EQUALS", "MINUS",
    "MK_VOLUP", "MK_VOLDOWN", "MK_MUTE",
}
KEYWORDS.update(chr(c) for c in range(ord("A"), ord("Z") + 1))
KEYWORDS.update(str(d) for d in range(10))
KEYWORDS.update(f"F{i}" for i in range(1, 13))

errors: list[str] = []

for path in sorted(PAYLOADS.glob("*.dd")):
    data = path.read_bytes()
    if any(b > 127 for b in data):
        errors.append(f"{path.name}: non-ASCII byte")
        continue
    for i, raw in enumerate(data.decode("ascii").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        head = line.split(None, 1)[0].upper()
        if any(head == p or line.upper().startswith(p + " ") or line.upper() == p for p in PREFIXES):
            continue
        for p in line.replace("-", " ").split():
            if p.upper() not in KEYWORDS:
                errors.append(f"{path.name}:{i}: unknown token {p!r}")
                break

# Branch skip logic must match firmware/ducky.py OS_TAGS
def _branch(host: str, lines: list[str]) -> list[str]:
    tags = {"WIN", "MAC", "LINUX", "ANDROID"}
    out: list[str] = []
    skip = None
    for line in lines:
        u = line.strip().upper()
        if u.startswith("IF_") and u[3:] in tags:
            skip = None if host == u[3:] else u[3:]
            continue
        if u == "END_IF":
            skip = None
            continue
        if skip:
            continue
        out.append(line)
    return out


_demo = ["IF_WIN", "W", "END_IF", "IF_LINUX", "L", "END_IF", "IF_ANDROID", "A", "END_IF"]
assert _branch("WIN", _demo) == ["W"]
assert _branch("LINUX", _demo) == ["L"]
assert _branch("ANDROID", _demo) == ["A"]
assert _branch("MAC", _demo) == []

if errors:
    print("check_dd FAILED:")
    for e in errors:
        print(" ", e)
    sys.exit(1)
print(f"check_dd OK ({len(list(PAYLOADS.glob('*.dd')))} files)")
