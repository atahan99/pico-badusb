# Hide CIRCUITPY from the host (no Explorer / Finder window).
# Redeploy with: ./tools/deploy.sh <payload>  (uses mpremote when drive is hidden)
# Or hold BOOTSEL and copy files to the RP2/RP2350 volume.
import storage

storage.disable_usb_drive()
