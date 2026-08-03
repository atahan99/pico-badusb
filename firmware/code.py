# Pico BadUSB runner. Inspired by dbisu/pico-ducky (GPLv2).
# Non-W: run payload.dd on boot.
# Pico W / Pico 2W: start soft-AP web UI (no auto-inject); trigger from browser.

import time
import board
import supervisor
from ducky import run_script

supervisor.runtime.autoreload = False
time.sleep(2.0)

_is_w = board.board_id in (
    "raspberry_pi_pico_w",
    "raspberry_pi_pico2_w",
)

if _is_w:
    print("Pico W: soft-AP mode")
    from wifi_ap import start_ap_and_serve
    start_ap_and_serve()
else:
    print("running payload.dd")
    run_script("payload.dd")
    print("done")
    while True:
        time.sleep(1)
