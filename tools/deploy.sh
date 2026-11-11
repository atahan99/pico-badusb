#!/usr/bin/env bash
# Copy firmware + selected payload to the Pico.
# Prefers mounted CIRCUITPY; falls back to mpremote when MSC is hidden.
# Usage:
#   ./tools/deploy.sh rickroll
#   ./tools/deploy.sh rickroll mac|linux|android   # force OS (writes os.txt)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"
shift || true
OS_FORCE=""
DEST=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    win|windows) OS_FORCE=win ;;
    mac|macos|osx) OS_FORCE=mac ;;
    linux) OS_FORCE=linux ;;
    android) OS_FORCE=android ;;
    *) DEST="$1" ;;
  esac
  shift
done

if [[ -z "$NAME" ]]; then
  echo "usage: $0 <payload-name> [win|mac|linux|android] [CIRCUITPY_PATH]" >&2
  ls "$ROOT/payloads"/*.dd 2>/dev/null | xargs -n1 basename | sed 's/\.dd$//' >&2
  exit 1
fi

SRC_DD="$ROOT/payloads/${NAME}.dd"
[[ -f "$SRC_DD" ]] || { echo "missing $SRC_DD" >&2; exit 1; }

write_os() {
  local dest="$1"
  if [[ -n "$OS_FORCE" ]]; then
    printf '%s\n' "$OS_FORCE" > "$dest/os.txt"
    echo "forced OS=$OS_FORCE (os.txt)"
  fi
}

deploy_fs() {
  local dest="$1"
  cp -X "$ROOT/firmware/boot.py" "$dest/boot.py"
  cp -X "$ROOT/firmware/code.py" "$dest/code.py"
  cp -X "$ROOT/firmware/ducky.py" "$dest/ducky.py"
  cp -X "$SRC_DD" "$dest/payload.dd"
  write_os "$dest"
  echo "deployed $NAME -> $dest/payload.dd (filesystem)"
}

deploy_mpremote() {
  command -v mpremote >/dev/null || {
    echo "CIRCUITPY not mounted and mpremote not found. Install: pip install mpremote" >&2
    exit 1
  }
  echo "CIRCUITPY hidden — deploying over serial (mpremote)..."
  mpremote connect auto cp "$ROOT/firmware/boot.py" :boot.py
  mpremote connect auto cp "$ROOT/firmware/code.py" :code.py
  mpremote connect auto cp "$ROOT/firmware/ducky.py" :ducky.py
  mpremote connect auto cp "$SRC_DD" :payload.dd
  if [[ -n "$OS_FORCE" ]]; then
    printf '%s\n' "$OS_FORCE" > /tmp/pico-os.txt
    mpremote connect auto cp /tmp/pico-os.txt :os.txt
    echo "forced OS=$OS_FORCE (os.txt)"
  fi
  echo "deployed $NAME -> :payload.dd (mpremote)"
  echo "Resetting board..."
  mpremote connect auto reset || true
}

if [[ -n "$DEST" && -d "$DEST" ]]; then
  deploy_fs "$DEST"
elif [[ -d /Volumes/CIRCUITPY ]]; then
  deploy_fs /Volumes/CIRCUITPY
elif [[ -d "$HOME/CIRCUITPY" ]]; then
  deploy_fs "$HOME/CIRCUITPY"
else
  deploy_mpremote
fi
echo "Ensure lib/adafruit_hid is on the board (see README)."
