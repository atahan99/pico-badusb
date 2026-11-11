# Pico BadUSB runner. Inspired by dbisu/pico-ducky (GPLv2).
# Every Pico variant: run payload.dd on boot.

import time
import supervisor
from ducky import run_script

supervisor.runtime.autoreload = False
time.sleep(2.0)

print("running payload.dd")
run_script("payload.dd")
print("done")
while True:
    time.sleep(1)
