#!/usr/bin/env python3
"""Draw a one-page newspaper front page summing up the world news of
Saturday 21 November 2026, and write it as a PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Pure standard library only (zlib for PNG compression). The image is
drawn programmatically: a masthead with the date, six story panels with
simple vector pictograms and short legible labels, and a footer ticker
with more of the day's headlines. Fully deterministic: the same bytes
on every run.
"""
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

PAPER = (246, 241, 229)
INK = (26, 26, 26)
NAVY = (22, 50, 79)
NAVY_DARK = (14, 34, 56)
RED = (179, 38, 30)
GOLD = (201, 151, 0)
TEAL = (31, 111, 107)
GREY = (90, 90, 88)
LIGHT = (255, 255, 255)
BLUE = (47, 102, 168)
GREEN = (46, 125, 50)
ORANGE = (214, 106, 24)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 strings of 5 characters ('1' = ink).
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
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "00000", "01100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
}

CHAR_W = 6  # 5 px glyph + 1 px spacing, in font units
CHAR_H = 7
LINE_H = 9  # font units per line


def text_width(s, scale):
    return len(s) * CHAR_W * scale - scale


def wrap_text(s, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines = []
    for para in s.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.set(xx, yy, color)

    def polygon(self, points, color):
        """Scanline fill for a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cx + gx * scale, y + gy * scale,
                                       scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, y, s, scale, color, x0=0, x1=None):
        x1 = self.w if x1 is None else x1
        x = x0 + (x1 - x0 - text_width(s, scale)) // 2
        self.text(x, y, s, scale, color)
        return x

    def to_png(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter: none
            raw += self.px[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(typ, data):
            c = struct.pack(">I", len(data)) + typ + data
            return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- icons
def icon_missile(c, x, y, s):
    """Explosion burst over a skyline: Russia's strikes on Ukraine."""
    cx, cy = x + s // 2, y + s // 2 - 8
    # burst star
    pts = []
    import math
    for i in range(16):
        ang = math.pi * i / 8
        r = 34 if i % 2 == 0 else 15
        pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
    c.polygon(pts, ORANGE)
    c.circle(cx, cy, 12, RED)
    c.circle(cx, cy, 6, GOLD)
    # rocket streaking down
    c.line(cx + 26, cy - 26, cx + 44, cy - 44, INK, 3)
    c.polygon([(cx + 40, cy - 46), (cx + 52, cy - 34), (cx + 44, cy - 30)],
              INK)
    # skyline
    base = y + s - 14
    c.fill_rect(x + 6, base - 26, 18, 26, NAVY)
    c.fill_rect(x + 30, base - 38, 16, 38, NAVY)
    c.fill_rect(x + 52, base - 20, 20, 20, NAVY)
    c.fill_rect(x + 78, base - 30, 14, 30, NAVY)
    c.fill_rect(x, base, s, 4, INK)


def icon_chart(c, x, y, s):
    """Falling market chart: the AI stock sell-off."""
    ox, oy = x + 10, y + s - 16
    c.line(ox, y + 10, ox, oy, INK, 3)
    c.line(ox, oy, x + s - 8, oy, INK, 3)
    # bars
    heights = [18, 30, 24, 40, 34, 52]
    bw = 11
    for i, hh in enumerate(heights):
        bx = ox + 8 + i * 14
        c.fill_rect(bx, oy - hh, bw, hh, (170, 170, 168) if i < 4 else RED)
    # plunging line with arrow
    pts = [(ox + 6, y + 22), (ox + 26, y + 34), (ox + 46, y + 30),
           (ox + 66, y + 52), (ox + 84, y + 74)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], RED, 4)
    ex, ey = pts[-1]
    c.polygon([(ex, ey), (ex - 12, ey - 2), (ex - 4, ey - 12)], RED)
    c.text(x + 8, y + 2, "-5.3%", 2, RED)


def icon_scales(c, x, y, s):
    """Scales of justice: the ICJ genocide ruling."""
    cx = x + s // 2
    top = y + 12
    c.fill_rect(cx - 3, top, 6, 62, INK)
    c.line(x + 12, top + 8, x + s - 12, top + 8, INK, 4)
    c.circle(cx, top + 4, 5, GOLD)
    for px in (x + 16, x + s - 16):
        c.line(px, top + 8, px, top + 34, INK, 2)
        c.polygon([(px - 16, top + 34), (px + 16, top + 34), (px, top + 50)],
                  GOLD)
    c.fill_rect(cx - 22, y + s - 18, 44, 6, INK)
    c.fill_rect(cx - 14, y + s - 12, 28, 4, INK)


def icon_flags(c, x, y, s):
    """Union Jack and EU flag side by side: the UK-EU deal."""
    # UK flag (simplified)
    fx, fy, fw, fh = x + 4, y + 22, 44, 30
    c.fill_rect(fx, fy, fw, fh, (0, 36, 125))
    c.line(fx, fy, fx + fw, fy + fh, LIGHT, 3)
    c.line(fx + fw, fy, fx, fy + fh, LIGHT, 3)
    c.fill_rect(fx + fw // 2 - 4, fy, 8, fh, RED)
    c.fill_rect(fx, fy + fh // 2 - 4, fw, 8, RED)
    # EU flag
    ex, ey = x + s - 48, y + 22
    c.fill_rect(ex, ey, 44, 30, (0, 51, 153))
    import math
    for i in range(12):
        ang = 2 * math.pi * i / 12
        c.circle(int(ex + 22 + 11 * math.cos(ang)),
                 int(ey + 15 + 9 * math.sin(ang)), 2, GOLD)
    # handshake star between
    c.circle(x + s // 2, y + 66, 5, GOLD)


def icon_globe(c, x, y, s):
    """Globe and thermometer: COP31 climate talks in Antalya."""
    cx, cy = x + s // 2 - 6, y + s // 2 - 4
    c.circle(cx, cy, 36, BLUE)
    c.ellipse(cx - 12, cy - 10, 14, 9, GREEN)
    c.ellipse(cx + 12, cy + 8, 12, 8, GREEN)
    c.ellipse(cx + 4, cy - 20, 8, 6, GREEN)
    c.circle(cx, cy, 36, INK, fill=False)
    # thermometer
    tx = x + s - 18
    c.fill_rect(tx - 3, y + 18, 6, 44, LIGHT)
    c.rect(tx - 3, y + 18, 6, 44, INK, 2)
    c.circle(tx, y + 66, 9, RED)
    c.fill_rect(tx - 1, y + 34, 2, 28, RED)
    # sun
    c.circle(x + 14, y + 14, 8, GOLD)


def icon_quake(c, x, y, s):
    """Cracked ground and shaking buildings: the Peru earthquake."""
    base = y + s - 16
    # buildings, tilted
    c.polygon([(x + 14, base - 44), (x + 34, base - 40), (x + 34, base),
               (x + 14, base)], NAVY)
    c.polygon([(x + 44, base - 58), (x + 66, base - 62), (x + 66, base),
               (x + 44, base)], (90, 60, 40))
    c.polygon([(x + 72, base - 30), (x + 90, base - 34), (x + 90, base),
               (x + 72, base)], TEAL)
    # windows
    for bx, by in ((20, base - 34), (50, base - 48), (76, base - 24)):
        c.fill_rect(bx, by, 5, 5, GOLD)
    # zigzag cracks
    pts = [(x + 8, base), (x + 26, base - 8), (x + 40, base + 2),
           (x + 58, base - 10), (x + 74, base), (x + 92, base - 6)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], RED, 3)
    c.line(x + 30, base + 2, x + 22, base + 12, RED, 2)
    c.line(x + 62, base - 2, x + 70, base + 10, RED, 2)
    # debris dots
    for dx, dy in ((x + 20, y + 12), (x + 48, y + 8)):
        c.circle(dx, dy, 2, INK)
    c.text(x + 8, y + 2, "6.9", 3, RED)


# ---------------------------------------------------------------- layout
STORIES = [
    ("WAR", "RUSSIA'S BIGGEST STRIKE HITS UKRAINE - AND POLAND",
     "400+ drones and 110 missiles strike overnight; 8 killed in Kyiv. "
     "Two land in Poland; Tusk calls it provocation.", icon_missile),
    ("MARKETS", "AI SELL-OFF SENDS STOCKS INTO CORRECTION",
     "The S&P 500 falls 3.7% and the Nasdaq drops 5.3%, wiping out its "
     "2026 gains, as doubts grow over AI spending.", icon_chart),
    ("JUSTICE", "COURT: MYANMAR GUILTY OF GENOCIDE",
     "The International Court of Justice finds Myanmar responsible for "
     "genocide against the Rohingya people.", icon_scales),
    ("EUROPE", "UK AND EU SIGN BIGGEST POST-BREXIT DEAL",
     "Three agreements on food trade, carbon markets and youth mobility "
     "for 100,000 young Britons.", icon_flags),
    ("CLIMATE", "COP31 TALKS RUN PAST DEADLINE",
     "Nearly 200 nations in Antalya fail to agree on fossil fuels as the "
     "UN climate summit goes into overtime.", icon_globe),
    ("DISASTER", "6.9 QUAKE SHAKES PERU'S ANDES",
     "A magnitude 6.9 earthquake strikes the Peruvian Andes.", icon_quake),
]

TICKER = ("ALSO TODAY: Houthi missiles fired at Riyadh are intercepted for "
          "a third night - FBI investigates a hack of the US crime database "
          "- a trial pill makes pancreatic tumours undetectable in 1 in 12 "
          "patients - Gen Z protests spread across 25 European countries")


def draw_panel(c, x, y, w, h, tag, headline, body, icon_fn):
    c.fill_rect(x, y, w, h, LIGHT)
    c.rect(x, y, w, h, INK, 2)
    c.fill_rect(x, y, w, 4, RED)
    icon_fn(c, x + 12, y + 34, 96)
    tx = x + 116
    tw = w - 116 - 16
    c.text(tx, y + 16, tag, 2, RED)
    c.line(tx, y + 34, tx + text_width(tag, 2), y + 34, RED, 2)
    lines = wrap_text(headline, 3, tw)
    ly = y + 44
    for ln in lines[:3]:
        c.text(tx, ly, ln, 3, INK)
        ly += 3 * LINE_H
    by = ly + 6
    for ln in wrap_text(body, 2, tw)[:4]:
        c.text(tx, by, ln, 2, (52, 52, 50))
        by += 2 * LINE_H


def draw():
    c = Canvas(W, H, PAPER)
    # outer frame
    c.rect(10, 10, W - 20, H - 20, INK, 3)

    # masthead
    c.fill_rect(20, 20, W - 40, 148, NAVY)
    c.fill_rect(20, 20, W - 40, 6, RED)
    c.text_center(36, "THE WORLD IN ONE DAY", 3, GOLD)
    c.text_center(66, "SATURDAY 21 NOVEMBER 2026", 5, LIGHT)
    c.fill_rect(120, 122, W - 240, 2, GOLD)
    c.text_center(132, "SIX STORIES THAT DEFINED THE DAY", 2, (200, 210, 225))

    # story panels: 2 columns x 3 rows
    gx, gy = 20, 182
    pw, ph = 484, 226
    gap = 12
    for i, (tag, head, body, icon_fn) in enumerate(STORIES):
        px = gx + (i % 2) * (pw + gap)
        py = gy + (i // 2) * (ph + gap)
        draw_panel(c, px, py, pw, ph, tag, head, body, icon_fn)

    # footer ticker
    ty = 182 + 3 * ph + 2 * gap + 12
    th = H - 20 - ty
    c.fill_rect(20, ty, W - 40, th, NAVY_DARK)
    c.fill_rect(20, ty, W - 40, 3, RED)
    lines = wrap_text(TICKER, 2, W - 40 - 32)
    ly = ty + 12
    for ln in lines[:4]:
        c.text(36, ly, ln, 2, LIGHT)
        ly += 2 * LINE_H
    return c


def run():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    png = draw().to_png()
    (out_dir / "entry.png").write_bytes(png)


if __name__ == "__main__":
    run()
