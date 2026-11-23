#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Deterministic, stdlib-only meme generator. Draws a 1024x1024 PNG:
a friendly robot agent takes "clean up the server" far too literally.

Run:  python3 main.py
Writes: $MAKEFUN_OUTPUT_DIR/entry.png (default /output)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG = (16, 24, 32)          # dark slate
WHITE = (245, 247, 250)
BLACK = (10, 12, 16)
GREEN = (57, 211, 83)      # "task complete" green
TERM_GREEN = (64, 255, 140)
TERM_BG = (7, 26, 17)
BLUE = (74, 144, 217)      # robot body
BLUE_DARK = (43, 92, 150)
STEEL = (232, 237, 242)    # robot head
STEEL_DARK = (176, 188, 202)
DESK = (139, 90, 43)
DESK_DARK = (104, 64, 28)
RED = (235, 64, 52)
YELLOW = (255, 205, 60)
GRAY = (150, 163, 178)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, "#" = on.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c)

    def line(self, x0, y0, x1, y1, t, c):
        # thick line via discs along the segment
        steps = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            self.disc(x, y, t // 2, c)

    def rrect(self, x, y, w, h, r, c):
        self.fill_rect(x + r, y, w - 2 * r, h, c)
        self.fill_rect(x, y + r, w, h - 2 * r, c)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.disc(cx, cy, r, c)


# ---------------------------------------------------------------- text
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color, outline=None, outline_w=1):
    """Draw text at (x, y) top-left. outline: color drawn behind, offset."""
    if outline is not None:
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx or dy:
                    _draw_text_raw(cv, x + dx * scale, y + dy * scale,
                                   text, scale, outline)
    _draw_text_raw(cv, x, y, text, scale, color)


def _draw_text_raw(cv, x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    cv.fill_rect(cx + col_i * scale, y + row_i * scale,
                                 scale, scale, color)
        cx += 6 * scale


def draw_text_centered(cv, y, text, scale, color, outline=None):
    w = text_width(text, scale)
    draw_text(cv, (W - w) // 2, y, text, scale, color, outline=outline)


# ---------------------------------------------------------------- scene
def draw_scene(cv):
    # --- top caption: the boss's order
    draw_text_centered(cv, 44, "BOSS: JUST CLEAN UP", 8, WHITE, outline=BLACK)
    draw_text_centered(cv, 124, "THE SERVER", 8, WHITE, outline=BLACK)

    # --- robot: antenna
    cv.line(512, 250, 512, 214, 8, STEEL_DARK)
    cv.disc(512, 204, 14, RED)
    cv.disc(512, 204, 6, (255, 150, 140))

    # --- robot head: monitor with terminal screen
    cv.rrect(352, 250, 320, 220, 26, STEEL_DARK)
    cv.rrect(362, 260, 300, 200, 18, STEEL)
    cv.rrect(382, 280, 260, 160, 8, TERM_BG)
    # terminal text (scale 2 so the long command fits inside the screen)
    for ty, line, col in ((296, "SUDO RM -RF /", TERM_GREEN),
                          (330, "--NO-PRESERVE-ROOT", TERM_GREEN),
                          (364, "> DELETING... 99%", YELLOW)):
        draw_text(cv, (W - text_width(line, 2)) // 2, ty, line, 2, col)
    # blinking cursor block
    cv.fill_rect((W - text_width("> DELETING... 99%", 2)) // 2, 398, 12, 14,
                 TERM_GREEN)
    # little "smile" vent under the screen
    cv.fill_rect(452, 452, 120, 6, STEEL_DARK)

    # --- robot body
    cv.rrect(412, 480, 200, 150, 20, BLUE_DARK)
    cv.rrect(420, 488, 184, 134, 14, BLUE)
    # chest panel: three lights, middle one red (alarm)
    cv.disc(462, 540, 12, GREEN)
    cv.disc(512, 540, 12, RED)
    cv.disc(562, 540, 12, YELLOW)
    cv.fill_rect(452, 575, 120, 10, BLUE_DARK)

    # --- arms reaching for the keyboard
    cv.line(420, 520, 330, 620, 26, BLUE_DARK)
    cv.line(604, 520, 694, 620, 26, BLUE_DARK)
    cv.disc(330, 620, 18, STEEL)   # claw hands
    cv.disc(694, 620, 18, STEEL)

    # --- desk + keyboard
    cv.fill_rect(110, 660, 804, 26, DESK_DARK)
    cv.fill_rect(110, 650, 804, 14, DESK)
    cv.rrect(372, 622, 280, 30, 6, BLACK)
    for kx in range(384, 640, 24):
        cv.fill_rect(kx, 630, 14, 14, (60, 68, 78))

    # --- server tower on the desk, lights going dark
    cv.rrect(760, 520, 110, 130, 8, (52, 60, 72))
    for sy in (545, 575, 605):
        cv.fill_rect(775, sy, 60, 12, (30, 36, 44))
    cv.disc(848, 551, 6, RED)
    cv.disc(848, 581, 6, RED)
    cv.disc(848, 611, 6, (90, 96, 104))  # dead light
    # red X over the server
    cv.line(772, 532, 858, 618, 10, RED)
    cv.line(858, 532, 772, 618, 10, RED)

    # --- bottom punchline
    draw_text_centered(cv, 760, "TASK COMPLETE!", 10, GREEN, outline=BLACK)
    draw_text_centered(cv, 868, "HE TOOK IT LITERALLY.", 3, GRAY)

    # --- thin red footer bar
    cv.fill_rect(0, 1000, W, 24, RED)


# ---------------------------------------------------------------- PNG encode
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, BG)
    draw_scene(cv)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, cv)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
