#!/usr/bin/env python3

import fileinput
import re

relevant_lines = []
active = False
with fileinput.input() as f:
    for line in f:
        if active:
            if line.strip() == "};":
                break
            relevant_lines.append(line)
        if re.search(r"keymaps.* = {", line):  # }
            active = True

keymaps = "".join(relevant_lines)

keymaps = re.sub(
    r"[\n ]*\[(.*)\] = LAYOUT_ergodox_pretty\(", r"Layer(\1,", keymaps
)  # ))
keymaps = re.sub(r"(KC_[A-Z_0-9]+)", r'"\1"', keymaps)
keymaps = re.sub(r"MOD_([A-Z_0-9]+)", r'"\1"', keymaps)
keymaps = re.sub(
    r"(TIC_TAC_TOE_LAYER|WEBUSB_PAIR|DANCE_\d|RESET|ST_MACRO_\d)", r'"\1"', keymaps
)


layer_names = ["default_layer", "umlt", "fn"]


class Layer:
    def __init__(self, layer, *args):
        self.layer = layer
        self.args = args

    def __str__(self):
        if isinstance(self.layer, int):
            layer_name = layer_names[self.layer]
        else:
            layer_name = self.layer

        return f"""\
    {layer_name} {{
      bindings = <
{format_bindings(self.args)}
      >;
    }};"""


column_width = len("&kp EQUAL   ")


def format_key(key: str) -> str:
    if key == "KC_NONUS_BSLASH":
        key = "NUBS"
    elif key == "KC_BSLASH":
        key = "BSLH"
    elif key == "KC_BSPACE":
        key = "BSPC"
    elif key == "KC_PSCR":
        key = "PSCRN"
    elif key == "KC_QUOTE":
        key = "SQT"
    elif key == "KC_TRANSPARENT":
        return "&trans"
    elif key == "KC_SCOLON":
        key = "SEMI"
    elif key == "KC_LBRACKET":
        key = "LBKT"
    elif key == "KC_RBRACKET":
        key = "RBKT"
    elif key == "KC_LCBR":
        key = "LBRC"
    elif key == "KC_RCBR":
        key = "RBRC"
    elif key == "KC_PGUP":
        key = "PG_UP"
    elif key == "KC_PGDOWN":
        key = "PG_DN"
    elif key == "KC_MEDIA_NEXT_TRACK":
        key = "C_NEXT"
    elif key == "KC_MEDIA_PREV_TRACK":
        key = "C_PREV"
    elif key == "KC_MEDIA_PLAY_PAUSE":
        key = "C_PP"
        # TODO:
    elif key == "KC_NO" or key == "WEBUSB_PAIR" or key == "KC_HYPR" or key == "KC_MS_BTN4" or key == "RESET":
        return "&none"

    assert not key.startswith("KC_MEDIA")
    if key.startswith("ST_MACRO"):
        return "&none" # TODO

    if key.startswith("KC_"):
        key = key[3:]
    if key.isdecimal():
        key = f"N{key}"
    return f"&kp {key}"


def format_bindings(bindings):
    bindings = list(bindings)
    for i in range(len(bindings)):
        if isinstance(bindings[i], str):
            bindings[i] = format_key(bindings[i])
        else:
            bindings[i] = str(bindings[i])

    cols = [7, 7, 6, 7, 5, 2, 1, 3]
    total_width = 11

    num_keyboard = sum(cols[:5]) * 2
    keyboard = bindings[:num_keyboard]
    thumb_clusters = bindings[num_keyboard:]

    thumb_cluster_cols = [0, 0, 2, 1, 3]
    keyboard_cols = [7, 7, 6, 7, 5]
    padding_after_keyboard = [0, 0, 1, 1, 2]

    result = []
    cur_keyboard = 0
    cur_thumb = 0
    WIDTH = 10
    for row in range(len(thumb_cluster_cols)):
        next_keyboard = cur_keyboard + keyboard_cols[row]
        next_thumb = cur_thumb + thumb_cluster_cols[row]
        left = (
            keyboard[cur_keyboard:next_keyboard]
            + [Padding() for _ in range(padding_after_keyboard[row])]
            + thumb_clusters[cur_thumb:next_thumb]
        )

        left += [Padding() for _ in range(WIDTH - len(left))]

        if row == 3:
            # The ergodox has a key that we don't have on the 360 here. For now we just drop it. We could move it one up.
            # For some reason zmk uses some keycodes here that don't seem to map to physical keys??
            left[-1] = "&none"
            left[-3] = "&none"
            left[-4] = "&none"


        cur_thumb = next_thumb
        cur_keyboard = next_keyboard

        next_keyboard = cur_keyboard + keyboard_cols[row]
        next_thumb = cur_thumb + thumb_cluster_cols[row]

        right = (
            thumb_clusters[cur_thumb:next_thumb]
            + [Padding() for _ in range(padding_after_keyboard[row])]
            + keyboard[cur_keyboard:next_keyboard]
        )
        right = [Padding() for _ in range(WIDTH - len(right))] + right

        if row == 3:
            # The ergodox has a key that we don't have on the 360 here. For now we just drop it. We could move it one up.
            # For some reason zmk uses some keycodes here that don't seem to map to physical keys??
            right[0] = "&none"
            right[2] = "&none"
            right[3] = "&none"
            pass


        result.append(left + right)

        cur_thumb = next_thumb
        cur_keyboard = next_keyboard

    result[2][6] = "&none"
    result[2][WIDTH + 3] = "&none"
    result[4][0] = "&mo mod"
    result[4][-1] = "&mo mod"

    return "\n".join(
        ("".join((str(s).ljust(column_width) for s in row)) for row in result)
    )


class Padding:
    def __str__(self):
        return " " * column_width


class TD:
    def __init__(self, keycode):
        self.keycode = keycode

    def __str__(self):
        return "&trans" # TODO


class MOD_RCTL:
    def __init__(self, keycode):
        self.keycode = keycode

    def __str__(self):
        return "RCTRL"



class MT:
    def __init__(self, modifier, keycode):
        self.modifier = modifier
        self.keycode = keycode

    def __str__(self):
        mod = str(self.modifier)
        return f"&mt {mod} {format_key(self.keycode)[4:]}"


class MO:
    def __init__(self, layer):
        self.layer = layer_names[layer] if isinstance(layer, int) else layer

    def __str__(self):
        return f"&mo {self.layer}"

class TG:
    def __init__(self, layer):
        self.layer = layer_names[layer] if isinstance(layer, int) else layer

    def __str__(self):
        return f"&tog {self.layer}"


layers = eval(keymaps)
print('\n'.join(map(str, layers)))
