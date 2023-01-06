#!/usr/bin/env fish

set -l IFS
set -l NEW_KEYMAP (./convert_to_zmk.py ~/qmk_firmware/keyboards/ergodox_ez/keymaps/sadf/keymap.c)

if test $status -ne 0
    echo "Unable to get new keymap"
    exit 1
end

set -l KEYMAP_PATH "./config/adv360.keymap"

if not test -f "$KEYMAP_PATH"
    echo "Unable to find $KEYMAP_PATH"
    exit 2
end

set -l START_CHUNK (sed -n '1,/LAYER_START/p' "$KEYMAP_PATH")
set -l END_CHUNK (sed -n '/LAYER_END/,$p' "$KEYMAP_PATH")

printf "%s\n%s\n%s\n" "$START_CHUNK" "$NEW_KEYMAP" "$END_CHUNK" > "$KEYMAP_PATH"
