# pico-badusb

![Raspberry Pi Pico BadUSB — all versions](pico-badusb.png)

**TL;DR:** CircuitPython Rubber Ducky for Pico / Pico W / Pico H / Pico 2 W. Plugs in as a USB keyboard/mouse, runs a `.dd` payload. **27 scripts** for **Windows, macOS, Linux, Android** via `IF_WIN` / `IF_MAC` / `IF_LINUX` / `IF_ANDROID`. US QWERTY. Authorized hosts only — [DISCLAIMER.md](DISCLAIMER.md).

Force OS with `os.txt` or `./tools/deploy.sh <name> win|mac|linux|android`. Without it, Caps Lock LED guesses **Win vs Mac** only (linux/android need a force).

## Setup

1. Flash CircuitPython 10.x UF2 from [circuitpython.org](https://circuitpython.org/downloads).
2. Drop `adafruit_hid` into `CIRCUITPY/lib/` ([bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest)).
3. Deploy:

```bash
./tools/deploy.sh rickroll
./tools/deploy.sh rickroll linux
./tools/deploy.sh rickroll android
```

`boot.py` hides CIRCUITPY → later deploys use mpremote.  
**Pico W / 2 W:** AP `PicoBadUSB` / `badusb1234` → `http://192.168.4.1/`

```bash
python3 tools/check_dd.py
```

## Payloads (27)

![OS](https://skillicons.dev/icons?i=windows,apple,linux,androidstudio)

| payload | OS | notes |
|---------|:--:|-------|
| rickroll | ![OS](https://skillicons.dev/icons?i=windows,apple,linux,androidstudio) | YouTube |
| hackertyper | ![OS](https://skillicons.dev/icons?i=windows,apple,linux,androidstudio) | hackertyper.com |
| fake_update | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | fakeupdate.io + fullscreen |
| volume_party | ![OS](https://skillicons.dev/icons?i=windows,apple,linux,androidstudio) | Settings / MK_VOL |
| mouse_jiggler | ![OS](https://skillicons.dev/icons?i=windows,apple,linux,androidstudio) | Mouse move |
| caps_blink | ![OS](https://skillicons.dev/icons?i=windows,apple,linux,androidstudio) | Caps toggle |
| notepad_meme | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Notepad / TextEdit / gedit |
| awareness_banner | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | HID-trust banner |
| speak_warning | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | SAPI / say / spd-say |
| desktop_marker | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Desktop test file |
| calc_spam | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Calculator |
| alt_tab_storm | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | App switcher |
| zoom_party | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Zoom in/out |
| screensaver_poke | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Lock screen |
| open_security_settings | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Security / privacy |
| net_info_local | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | ipconfig / ifconfig / ip |
| local_fingerprint | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | Local OS info |
| whoami_desktop | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | whoami + hostname |
| jitter_countdown | ![OS](https://skillicons.dev/icons?i=windows,apple,linux) | 3-2-1 |
| snap_dance | ![OS](https://skillicons.dev/icons?i=windows,linux) | Snap / tile |
| caps_sync | ![OS](https://skillicons.dev/icons?i=windows,linux) | WAIT_FOR_CAPS_* |
| activity_monitor | ![OS](https://skillicons.dev/icons?i=apple) | Activity Monitor |
| mac_screenshot | ![OS](https://skillicons.dev/icons?i=apple) | Shift-Cmd-3 |
| linux_notify | ![OS](https://skillicons.dev/icons?i=linux) | notify-send |
| linux_terminal_banner | ![OS](https://skillicons.dev/icons?i=linux) | Terminal banner |
| android_volume | ![OS](https://skillicons.dev/icons?i=androidstudio) | MK_VOL spam |
| android_type | ![OS](https://skillicons.dev/icons?i=androidstudio) | Type into focus |
