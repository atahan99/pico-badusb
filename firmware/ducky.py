# Thin DuckyScript runner for CircuitPython HID.
# Inspired by dbisu/pico-ducky (GPLv2).
# IF_WIN / IF_MAC / IF_LINUX / IF_ANDROID / END_IF
# Force OS with /os.txt (win|mac|linux|android). Else Caps LED -> WIN vs MAC.

import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

KEYS = {
    "WINDOWS": Keycode.GUI,
    "GUI": Keycode.GUI,
    "COMMAND": Keycode.GUI,
    "CTRL": Keycode.CONTROL,
    "CONTROL": Keycode.CONTROL,
    "ALT": Keycode.ALT,
    "OPTION": Keycode.ALT,
    "SHIFT": Keycode.SHIFT,
    "ENTER": Keycode.ENTER,
    "ESCAPE": Keycode.ESCAPE,
    "ESC": Keycode.ESCAPE,
    "TAB": Keycode.TAB,
    "SPACE": Keycode.SPACE,
    "BACKSPACE": Keycode.BACKSPACE,
    "DELETE": Keycode.DELETE,
    "UP": Keycode.UP_ARROW,
    "DOWN": Keycode.DOWN_ARROW,
    "LEFT": Keycode.LEFT_ARROW,
    "RIGHT": Keycode.RIGHT_ARROW,
    "UPARROW": Keycode.UP_ARROW,
    "DOWNARROW": Keycode.DOWN_ARROW,
    "LEFTARROW": Keycode.LEFT_ARROW,
    "RIGHTARROW": Keycode.RIGHT_ARROW,
    "HOME": Keycode.HOME,
    "END": Keycode.END,
    "PAGEUP": Keycode.PAGE_UP,
    "PAGEDOWN": Keycode.PAGE_DOWN,
    "CAPSLOCK": Keycode.CAPS_LOCK,
    "EQUAL": Keycode.EQUALS,
    "EQUALS": Keycode.EQUALS,
    "MINUS": Keycode.MINUS,
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    KEYS[_c] = getattr(Keycode, _c)
for _i, _name in enumerate(
    ("ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE")
):
    KEYS[str(_i)] = getattr(Keycode, _name)
for _i in range(1, 13):
    KEYS["F%d" % _i] = getattr(Keycode, "F%d" % _i)

CONSUMER = {
    "MK_VOLUP": ConsumerControlCode.VOLUME_INCREMENT,
    "MK_VOLDOWN": ConsumerControlCode.VOLUME_DECREMENT,
    "MK_MUTE": ConsumerControlCode.MUTE,
}

OS_TAGS = ("WIN", "MAC", "LINUX", "ANDROID")
_host_os = "WIN"


def _press_combo(parts):
    codes = []
    for p in parts:
        p = p.strip().upper()
        if p in CONSUMER:
            cc.send(CONSUMER[p])
            return
        if p not in KEYS:
            raise ValueError("unknown key: " + p)
        codes.append(KEYS[p])
    if codes:
        kbd.press(*codes)
        kbd.release_all()


def _wait_caps(want_on, timeout_s=30):
    end = time.monotonic() + timeout_s
    while time.monotonic() < end:
        if kbd.led_on(Keyboard.LED_CAPS_LOCK) == want_on:
            return
        time.sleep(0.05)


def detect_os():
    try:
        with open("/os.txt", "r") as f:
            v = f.read().strip().lower()
        m = {
            "win": "WIN", "windows": "WIN",
            "mac": "MAC", "macos": "MAC", "osx": "MAC",
            "linux": "LINUX",
            "android": "ANDROID",
        }
        if v in m:
            return m[v]
    except OSError:
        pass

    # ponytail: Caps LED ~WIN; not ~MAC. linux/android need os.txt.
    was_on = kbd.led_on(Keyboard.LED_CAPS_LOCK)
    if was_on:
        _press_combo(["CAPSLOCK"])
        time.sleep(0.12)
    _press_combo(["CAPSLOCK"])
    time.sleep(0.18)
    follows = kbd.led_on(Keyboard.LED_CAPS_LOCK)
    if follows:
        _press_combo(["CAPSLOCK"])
        time.sleep(0.12)
        return "WIN"
    if was_on:
        _press_combo(["CAPSLOCK"])
        time.sleep(0.12)
    return "MAC"


def run_script(path):
    global _host_os
    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except OSError:
        print("missing payload", path)
        return

    _host_os = detect_os()
    print("os", _host_os)
    default_delay = 0
    skip = None
    print("running", path)

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()

        if upper.startswith("IF_") and upper[3:] in OS_TAGS:
            tag = upper[3:]
            skip = None if _host_os == tag else tag
            continue
        if upper == "END_IF":
            skip = None
            continue
        if skip:
            continue

        if upper.startswith("REM"):
            continue
        if upper.startswith("DELAY "):
            time.sleep(float(line.split(None, 1)[1]) / 1000.0)
            continue
        if upper.startswith("DEFAULT_DELAY") or upper.startswith("DEFAULTDELAY"):
            default_delay = int(line.split(None, 1)[1])
            continue
        if upper.startswith("STRINGLN"):
            layout.write(line.split(None, 1)[1] if " " in line else "")
            _press_combo(["ENTER"])
        elif upper.startswith("STRING"):
            layout.write(line.split(None, 1)[1] if " " in line else "")
        elif upper.startswith("MOUSE_MOVE"):
            bits = line.split()
            mouse.move(x=int(bits[1]), y=int(bits[2]))
        elif upper.startswith("MOUSE_CLICK"):
            mouse.click(Mouse.LEFT_BUTTON)
        elif upper.startswith("WAIT_FOR_CAPS_ON"):
            _wait_caps(True)
        elif upper.startswith("WAIT_FOR_CAPS_OFF"):
            _wait_caps(False)
        elif upper == "ENTER":
            _press_combo(["ENTER"])
        else:
            _press_combo(line.replace("-", " ").split())
        if default_delay:
            time.sleep(default_delay / 1000.0)
    kbd.release_all()
    print("done", path)
