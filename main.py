#!/usr/bin/env python3
"""The World Today - Wednesday 25 November 2026.

One image that sums up the day's world news: six stories, each with a
small picture drawn by this program and a short label, under one masthead
that names the day. Pure standard library, no network, no files read.
Run it twice and you get the exact same bytes both times.

The six stories were picked on the morning of the 25th from what Reuters,
CNN and others had reported by then. The entry is meant to be refreshed
with the full day's news before it goes in, so treat the story list at
the bottom as the thing that changes, and the drawing code as the thing
that stays.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# A little 5x7 pixel font, drawn from scratch for this page.
#
# The sandbox has no font files and the program may not fetch one, so the
# letters live here as tiny pictures: seven rows of five dots each, '#'
# for ink and '.' for empty. Only capitals, digits and the handful of
# marks the copy actually needs - a newspaper page shouts anyway, so
# everything is set in caps and the lowercase never shows up.
# ---------------------------------------------------------------------------

FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
}

# ---------------------------------------------------------------------------
# The canvas: just a big bytearray of RGB pixels, and a handful of shapes
# to push around on it. Flat colours on purpose - a flat newspaper look
# still reads when the image is shrunk to 300 pixels wide, while thin
# lines and gradients turn to mush.
# ---------------------------------------------------------------------------

PAPER = (247, 243, 234)   # warm off-white, like newsprint
INK = (26, 26, 26)
SOFT_INK = (74, 74, 74)
RED = (178, 34, 34)
RULE = (26, 26, 26)


class Page:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def put(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def line(self, x0, y0, x1, y1, colour, thick=1):
        # Bresenham, with a little thickness by stamping a square at each step.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        # A filled circle, scanline by scanline.
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, yy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            outer = int((r * r - dy * dy) ** 0.5)
            inner = int(max(0, (r - thick) * (r - thick) - dy * dy) ** 0.5)
            self.rect(cx - outer, yy, outer - inner, 1, colour)
            self.rect(cx + inner + 1, yy, outer - inner, 1, colour)

    def poly(self, points, colour):
        # Flat-top scanline fill; good enough for roofs, hulls and bursts.
        if not points:
            return
        ys = [p[1] for p in points]
        for yy in range(max(0, min(ys)), min(self.height, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), yy, int(xs[i + 1]) - int(xs[i]) + 1, 1, colour)


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def write_png(page, path):
    """Encode the page as a plain RGB PNG. No filters, no metadata chunks,
    nothing that smuggles in a timestamp - the bytes depend only on the
    pixels, so two runs come out identical."""
    raw = bytearray()
    stride = page.width * 3
    for y in range(page.height):
        raw.append(0)
        raw += page.pixels[y * stride:(y + 1) * stride]
    blob = zlib.compress(bytes(raw), 9)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", page.width, page.height,
                                         8, 2, 0, 0, 0))
           + _chunk(b"IDAT", blob)
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)

# ---------------------------------------------------------------------------
# Text. The font is 5 wide, 7 tall, with one blank column between letters
# so words don't run together. draw_paragraph wraps on word boundaries so
# a headline never runs off the edge of its tile.
# ---------------------------------------------------------------------------

LETTER_STEP = 6  # 5 pixels of glyph + 1 of breathing room


def measure(text, scale):
    return sum(LETTER_STEP for ch in text) * scale - scale


def draw_glyph(page, x, y, ch, scale, colour):
    glyph = FONT.get(ch)
    if glyph is None:
        return
    for row, line in enumerate(glyph):
        for col, dot in enumerate(line):
            if dot == "#":
                page.rect(x + col * scale, y + row * scale, scale, scale, colour)


def draw_text(page, x, y, text, scale, colour):
    # The font only holds capitals, digits and a few marks, so everything
    # goes up in caps first - which suits a newspaper page anyway.
    text = text.upper()
    cx = x
    for ch in text:
        draw_glyph(page, cx, y, ch, scale, colour)
        cx += LETTER_STEP * scale
    return cx


def wrap(text, scale, max_width):
    """Greedy word wrap; a single too-long word is split by letters."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if measure(trial, scale) <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                while measure(word, scale) > max_width:
                    cut = max_width // (LETTER_STEP * scale)
                    lines.append(word[:cut])
                    word = word[cut:]
                line = word
        if line:
            lines.append(line)
    return lines


def draw_paragraph(page, x, y, text, scale, colour, max_width, line_step):
    """Draw wrapped text, return the y just below the last line."""
    cy = y
    for line in wrap(text, scale, max_width):
        draw_text(page, x, cy, line, scale, colour)
        cy += line_step
    return cy

# ---------------------------------------------------------------------------
# The six pictures. Each one is a small scene drawn from rectangles,
# circles and triangles - no photos, no fetched art, so the program can
# draw them anywhere with nothing but the standard library.
# ---------------------------------------------------------------------------

def pic_ship(page, x, y, w, h):
    sky = (176, 205, 222)
    sea = (38, 84, 124)
    page.rect(x, y, w, h, sky)
    page.rect(x, y + h * 2 // 3, w, h // 3, sea)
    # a few pale clouds, then the ship low on the water
    page.rect(x + 24, y + 12, 70, 10, (235, 240, 244))
    page.rect(x + w - 110, y + 26, 84, 10, (235, 240, 244))
    hull_y = y + h * 2 // 3 - 16
    page.poly([(x + 60, hull_y), (x + w - 70, hull_y),
               (x + w - 96, hull_y + 22), (x + 84, hull_y + 22)], (30, 34, 40))
    page.rect(x + 150, hull_y - 26, 90, 26, (30, 34, 40))   # deck house
    page.rect(x + 230, hull_y - 44, 8, 18, (30, 34, 40))    # funnel
    page.line(x + 110, hull_y, x + 110, hull_y - 34, (30, 34, 40), 3)
    # the blast: a starburst where the drone hit, and the drone itself
    cx, cy = x + w - 120, hull_y - 6
    for dx, dy in [(0, -26), (18, -18), (26, 0), (18, 18), (0, 26),
                   (-18, 18), (-26, 0), (-18, -18)]:
        page.line(cx, cy, cx + dx, cy + dy, (240, 140, 30), 5)
    page.disc(cx, cy, 12, (250, 200, 60))
    page.disc(x + 90, y + 22, 3, (30, 34, 40))
    page.line(x + 82, y + 22, x + 98, y + 22, (30, 34, 40), 2)
    page.line(x + 90, y + 14, x + 90, y + 30, (30, 34, 40), 2)


def pic_tower(page, x, y, w, h):
    dusk = (232, 178, 138)
    page.rect(x, y, w, h, dusk)
    page.disc(x + w - 60, y + 24, 16, (250, 220, 150))      # low sun
    # skyline, then the tall tower in the middle with its open arch
    for bx, bw, bh in [(0, 60, 44), (66, 46, 60), (300, 52, 52),
                       (358, 60, 38), (424, 42, 66)]:
        page.rect(x + bx, y + h - bh, bw, bh, (58, 48, 58))
    tx = x + w // 2 - 34
    page.rect(tx, y + 8, 68, h - 8, (38, 32, 40))           # the tower
    page.poly([(tx + 10, y + 8), (tx + 58, y + 8),
               (tx + 34, y + 46)], dusk)                    # its arch opening
    # flash and smoke where the drone struck, halfway up
    fx, fy = tx + 34, y + h // 2
    for dx, dy in [(0, -20), (14, -14), (20, 0), (14, 14), (0, 20),
                   (-14, 14), (-20, 0), (-14, -14)]:
        page.line(fx, fy, fx + dx, fy + dy, (250, 210, 80), 4)
    page.disc(fx, fy, 9, (255, 240, 160))
    page.disc(fx - 26, fy - 26, 10, (120, 110, 115))
    page.disc(fx + 24, fy - 34, 12, (140, 130, 135))


def pic_court(page, x, y, w, h):
    pale = (226, 228, 222)
    page.rect(x, y, w, h, pale)
    # a courthouse: steps, four columns, a triangular roof
    page.rect(x + 40, y + h - 16, w - 80, 16, (120, 116, 108))
    page.rect(x + 52, y + h - 26, w - 104, 10, (140, 136, 128))
    for cx in (86, 158, 230, 302):
        page.rect(x + cx, y + 44, 22, h - 70, (196, 192, 182))
    page.poly([(x + 40, y + 44), (x + w - 40, y + 44),
               (x + w // 2, y + 10)], (168, 162, 150))
    page.disc(x + w // 2, y + 26, 7, (120, 116, 108))
    # the scales of justice in front of the steps
    sx = x + w - 78
    page.line(sx, y + h - 44, sx, y + h - 92, (90, 70, 40), 3)
    page.line(sx - 26, y + h - 86, sx + 26, y + h - 86, (90, 70, 40), 3)
    page.poly([(sx - 38, y + h - 70), (sx - 14, y + h - 70),
               (sx - 26, y + h - 58)], (90, 70, 40))
    page.poly([(sx + 14, y + h - 70), (sx + 38, y + h - 70),
               (sx + 26, y + h - 58)], (90, 70, 40))


def pic_chip(page, x, y, w, h):
    page.rect(x, y, w, h, (16, 60, 44))
    # a chip in the middle, pins on every side, and a market line climbing
    cx, cy = x + w // 2 - 130, y + h // 2
    for i in range(5):
        page.rect(cx - 14, cy - 26 + i * 12, 14, 6, (190, 200, 190))
        page.rect(cx + 64, cy - 26 + i * 12, 14, 6, (190, 200, 190))
        page.rect(cx - 2 + i * 14, cy - 40, 6, 14, (190, 200, 190))
        page.rect(cx - 2 + i * 14, cy + 26, 6, 14, (190, 200, 190))
    page.rect(cx, cy - 26, 64, 52, (34, 110, 80))
    page.rect(cx + 14, cy - 12, 36, 24, (120, 210, 160))
    page.line(x + w - 250, y + h - 26, x + w - 180, y + h - 52,
              (120, 220, 140), 4)
    page.line(x + w - 180, y + h - 52, x + w - 130, y + h - 40,
              (120, 220, 140), 4)
    page.line(x + w - 130, y + h - 40, x + w - 60, y + 16,
              (120, 220, 140), 4)
    page.poly([(x + w - 60, y + 16), (x + w - 84, y + 18),
               (x + w - 62, y + 40)], (120, 220, 140))


def pic_shanghai(page, x, y, w, h):
    sky = (178, 208, 232)
    page.rect(x, y, w, h, sky)
    page.disc(x + 52, y + 22, 14, (250, 228, 150))
    # the Oriental Pearl Tower: a needle, two spheres, a tapering stem
    tx = x + w // 2
    page.poly([(tx - 22, y + h), (tx + 22, y + h), (tx + 6, y + 8),
               (tx - 6, y + 8)], (96, 106, 122))
    page.disc(tx, y + 30, 15, (214, 96, 110))
    page.disc(tx, y + 66, 24, (214, 96, 110))
    page.line(tx, y + 8, tx, y - 2, (96, 106, 122), 2)
    # neighbours, a red flag, and a magnifier over the whole scene
    page.rect(x + 30, y + h - 46, 70, 46, (110, 120, 135))
    page.rect(x + w - 110, y + h - 60, 80, 60, (130, 140, 155))
    page.line(x + 62, y + h - 46, x + 62, y + h - 78, (90, 90, 90), 3)
    page.poly([(x + 62, y + h - 78), (x + 88, y + h - 72),
               (x + 62, y + h - 66)], (200, 40, 40))
    page.ring(x + w - 92, y + 34, 24, (40, 40, 40), 4)
    page.line(x + w - 74, y + 52, x + w - 52, y + 74, (40, 40, 40), 4)


def pic_wave(page, x, y, w, h):
    page.rect(x, y, w, h, (196, 222, 232))
    page.disc(x + 56, y + 20, 14, (250, 226, 140))
    # the sea, then a crest of overlapping humps so the water reads as
    # one big wave rolling in, with foam along its top edge
    page.rect(x, y + 56, w, h - 56, (36, 96, 150))
    for cx, r in [(x + 70, 34), (x + 160, 48), (x + 250, 56),
                  (x + 340, 48), (x + 420, 34)]:
        page.disc(cx, y + 56, r, (36, 96, 150))
    for cx, cy, r in [(x + 120, y + 14, 8), (x + 200, y + 4, 10),
                      (x + 290, y + 6, 9), (x + 370, y + 16, 8)]:
        page.disc(cx, cy, r, (240, 248, 252))
    # two little houses in front of the water, roofs still showing
    for hx in (x + 60, x + 300):
        page.rect(hx, y + h - 44, 74, 44, (196, 170, 130))
        page.poly([(hx - 8, y + h - 44), (hx + 82, y + h - 44),
                   (hx + 37, y + h - 72)], (150, 60, 50))
        page.rect(hx + 28, y + h - 26, 18, 26, (90, 60, 40))
    page.rect(x, y + h - 14, w, 14, (24, 70, 120))


PICTURES = [pic_ship, pic_tower, pic_court, pic_chip, pic_shanghai, pic_wave]

# ---------------------------------------------------------------------------
# The day's news. Six stories, picked this morning (25 Nov, ~01:20 UTC)
# from what Reuters, CNN and others had reported so far: the biggest
# ones, across regions and beats, each stated the way it was reported.
# The entry is refreshed with the full day's news before it is submitted.
# ---------------------------------------------------------------------------

STORIES = [
    ("UKRAINE WAR",
     "UKRAINE HITS TWO RUSSIAN SHIPS",
     "Zelenskiy confirms drone strikes on Russian ships in the Gulf "
     "of Finland and off Libya."),
    ("MIDDLE EAST",
     "HOUTHI DRONE HITS RIYADH TOWER",
     "A drone attack on Riyadh's tallest tower wounds 11, Saudi "
     "civil defence says."),
    ("TECH ON TRIAL",
     "HUAWEI CONVICTED IN US COURT",
     "A US jury convicts Huawei over its Iran business; it is "
     "cleared of racketeering."),
    ("MARKETS",
     "HUANG BACK AT NVIDIA",
     "Reinstated as chief executive, Huang apologises to staff; "
     "shares jump 31% in a day."),
    ("CHINA",
     "SHANGHAI CHIEF UNDER PROBE",
     "China opens a corruption case against Shanghai party chief "
     "Chen Jining."),
    ("WEATHER",
     "KING TIDES FLOOD CALIFORNIA",
     "A record 8.23 ft tide in San Francisco swamps homes days "
     "before Thanksgiving."),
]

DAY_LINE = "WEDNESDAY 25 NOVEMBER 2026"


def draw_masthead(page):
    title = "THE WORLD TODAY"
    scale = 7
    x = (WIDTH - measure(title, scale)) // 2
    draw_text(page, x, 26, title, scale, INK)
    date = DAY_LINE
    scale = 3
    x = (WIDTH - measure(date, scale)) // 2
    draw_text(page, x, 86, date, scale, RED)
    page.rect(18, 122, WIDTH - 36, 3, RED)
    page.rect(18, 128, WIDTH - 36, 1, RULE)


def draw_tile(page, x, y, w, h, kicker, headline, sub, picture):
    # The tile's rhythm, top to bottom: picture, kicker, headline, then
    # the one-line summary. The numbers are tuned so two headline lines
    # and three summary lines fit with room to spare - a fourth summary
    # line would spill, so keep the copy short.
    pad = 10
    pic_h = 100
    text_x = x + pad
    text_w = w - pad * 2
    page.rect(x, y, w, h, (255, 253, 248))
    page.rect(x, y, w, 1, (205, 200, 190))
    page.rect(x, y + h - 1, w, 1, (205, 200, 190))
    page.rect(x, y, 1, h, (205, 200, 190))
    page.rect(x + w - 1, y, 1, h, (205, 200, 190))
    picture(page, text_x, y + pad, text_w, pic_h)
    draw_text(page, text_x, y + 118, kicker, 2, RED)
    draw_paragraph(page, text_x, y + 136, headline, 4, INK, text_w, 32)
    draw_paragraph(page, text_x, y + 204, sub, 2, SOFT_INK, text_w, 17)


def draw_footer(page):
    page.rect(18, 962, WIDTH - 36, 1, RULE)
    line = "SIX STORIES FROM AROUND THE WORLD - AS REPORTED ON 25 NOVEMBER 2026"
    scale = 2
    x = (WIDTH - measure(line, scale)) // 2
    draw_text(page, x, 976, line, scale, SOFT_INK)


def main():
    page = Page(WIDTH, HEIGHT, PAPER)
    draw_masthead(page)

    # Two columns, three rows. The grid is worked out from the space
    # between the masthead rule (y=134) and the footer rule (y=962):
    # whatever is left is split into three rows with a gutter between.
    margin, gut = 18, 14
    top = 134
    bottom = 962 - 12
    tile_w = (WIDTH - margin * 2 - gut) // 2
    tile_h = (bottom - top - gut * 2) // 3
    for i, (kicker, headline, sub) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (tile_w + gut)
        y = top + row * (tile_h + gut)
        draw_tile(page, x, y, tile_w, tile_h, kicker, headline, sub,
                  PICTURES[i])

    draw_footer(page)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(page, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
