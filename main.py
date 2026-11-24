"""The World in One Page - Tuesday 24 November 2026.

A pure standard-library program that draws one newspaper front page
summarising the world news of 24 November 2026 and writes it as a
deterministic PNG to MAKEFUN_OUTPUT_DIR/entry.png.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 238, 218)
INK = (22, 20, 18)
RED = (168, 32, 28)
BLUE = (28, 74, 128)
GREEN = (38, 110, 62)
ORANGE = (222, 116, 28)
YELLOW = (240, 188, 44)
GREY = (96, 92, 84)
WHITE = (250, 248, 240)
DARK = (26, 26, 30)
SKY = (120, 178, 216)

# ---------------------------------------------------------------- font
# A hand-drawn 5x7 bitmap font. Each glyph is seven rows of five pixels.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
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
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    ":": (".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."),
    ";": (".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": (".##..", "..#..", "...#.", "...#.", "...#.", "..#..", ".##.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}


def glyph(ch):
    ch = ch.upper()
    if ch in FONT:
        return FONT[ch]
    if ch in "—–":
        return FONT["-"]
    return FONT[" "]


# ---------------------------------------------------------------- canvas
class Page:
    def __init__(self):
        self.px = bytearray(W * H * 3)
        self.fill(PAPER)

    def set(self, x, y, colour):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = colour[0]
            self.px[i + 1] = colour[1]
            self.px[i + 2] = colour[2]

    def fill(self, colour):
        row = bytes(colour) * W
        for y in range(H):
            self.px[y * W * 3:(y + 1) * W * 3] = row

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, colour)

    def frame(self, x, y, w, h, colour, t=3):
        self.rect(x, y, w, t, colour)
        self.rect(x, y + h - t, w, t, colour)
        self.rect(x, y, t, h, colour)
        self.rect(x + w - t, y, t, h, colour)

    def circle(self, cx, cy, r, colour, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled and d2 <= r * r:
                    self.set(xx, yy, colour)
                if not filled and r * r - 2 * r <= d2 <= r * r:
                    self.set(xx, yy, colour)

    def triangle(self, x, y, w, h, colour):
        # point at the top, wide base at the bottom
        for row in range(h):
            half = (row + 1) * w // (2 * h)
            for xx in range(x + w // 2 - half, x + w // 2 + half):
                self.set(xx, y + row, colour)

    def text(self, x, y, s, scale, colour, spacing=1):
        cx = x
        for ch in s:
            rows = glyph(ch)
            for ry, line in enumerate(rows):
                for rx, mark in enumerate(line):
                    if mark == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, colour)
            cx += (5 + spacing) * scale
        return cx

    def text_w(self, s, scale, spacing=1):
        return max(0, len(s) * (5 + spacing) * scale - spacing * scale)

    def centred(self, y, s, scale, colour):
        x = (W - self.text_w(s, scale)) // 2
        self.text(x, y, s, scale, colour)
        return x

    def wrapped(self, x, y, s, scale, colour, max_chars, leading=None):
        if leading is None:
            leading = 9 * scale
        words = s.split()
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if len(trial) > max_chars and line:
                self.text(x, y, line, scale, colour)
                y += leading
                line = word
            else:
                line = trial
        if line:
            self.text(x, y, line, scale, colour)
            y += leading
        return y


def chunk(tag, data):
    body = tag + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def save_png(page, path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += page.px[y * stride:(y + 1) * stride]
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# ---------------------------------------------------------------- drawing
def masthead(p):
    p.frame(10, 10, W - 20, H - 20, INK, 4)
    p.centred(26, "TUESDAY 24 NOVEMBER 2026", 3, INK)
    p.rect(36, 58, W - 72, 3, INK)
    p.rect(36, 65, W - 72, 1, INK)
    p.centred(78, "THE WORLD IN ONE PAGE", 7, INK)
    p.centred(136, "CLIMATE - WAR - ASIA - SCIENCE - SPORT", 2, RED)
    p.rect(36, 158, W - 72, 5, INK)
    p.rect(36, 167, W - 72, 2, INK)


def globe(p, cx, cy, r):
    p.circle(cx, cy, r, SKY)
    p.circle(cx, cy, r, BLUE, filled=False)
    # simple continents
    for dx, dy, rr in ((-28, -22, 15), (-8, -34, 11), (18, -12, 17),
                       (30, 16, 13), (-16, 14, 12), (4, 34, 10)):
        p.circle(cx + dx, cy + dy, rr, GREEN)
    # latitude lines suggest a spinning planet
    for dy in (-30, 0, 30):
        for i in range(-r + 8, r - 7):
            if i * i + dy * dy < r * r:
                p.set(cx + i, cy + dy, BLUE)


def lead_story(p):
    y = 182
    p.text(36, y, "CLIMATE - ANTALYA, TURKIYE", 3, RED)
    p.text(36, y + 30, "COP31 TALKS", 6, INK)
    p.text(36, y + 82, "COLLAPSE OVER", 6, INK)
    p.text(36, y + 134, "FOSSIL FUELS", 6, RED)
    body = ("AFTER TWO WEEKS OF TALKS, 194 NATIONS END THE COP31 "
            "SUMMIT IN ANTALYA WITH NO AGREEMENT ON PHASING OUT "
            "FOSSIL FUELS. ROWS OVER FINANCE DEEPEN, AND CAMPAIGNERS "
            "CALL IT A SETBACK FOR THE PARIS GOALS.")
    p.wrapped(36, y + 186, body, 2, INK, 46)
    # picture box on the right
    p.frame(676, y, 312, 218, INK, 3)
    globe(p, 832, y + 88, 62)
    cap = "NO DEAL IN ANTALYA"
    p.text(832 - p.text_w(cap, 2) // 2, y + 168, cap, 2, INK)
    stat = "194 NATIONS - 0 DEAL"
    p.text(832 - p.text_w(stat, 2) // 2, y + 190, stat, 2, RED)
    p.rect(36, y + 280, W - 72, 2, INK)


def flames(p, x, y):
    for dx, h, c in ((0, 44, ORANGE), (18, 58, RED), (38, 48, ORANGE),
                     (56, 36, YELLOW)):
        p.triangle(x + dx, y, 26, h, c)
    p.rect(x - 4, y + 46, 92, 8, INK)


def second_row(p):
    y = 478
    # left: Indonesia
    p.text(36, y, "INDONESIA - BANTEN", 3, RED)
    p.text(36, y + 28, "FACTORY FIRE", 4, INK)
    p.text(36, y + 62, "KILLS 24 AS", 4, INK)
    p.text(36, y + 96, "SEARCH GOES ON", 4, INK)
    body = ("RESCUERS SEARCH THE RUINS OF A CANDY FACTORY FOR "
            "ABOUT 30 MISSING WORKERS AFTER A BLAZE KILLED AT "
            "LEAST 24. FAMILIES WAIT FOR NEWS.")
    p.wrapped(36, y + 132, body, 2, INK, 36)
    flames(p, 386, y + 58)
    # divider
    p.rect(506, y, 2, 196, GREY)
    # right: Ukraine and the seas
    x = 530
    p.text(x, y, "UKRAINE - KYIV REGION", 3, RED)
    p.text(x, y + 28, "DRONES HIT KYIV", 4, INK)
    p.text(x, y + 62, "HOMES, SHIPS BURN", 4, INK)
    body2 = ("RUSSIAN STRIKES DAMAGE HOMES IN DYMER AND LEAVE "
             "PEOPLE MISSING. THE CARGO SHIP SPARTA II CATCHES "
             "FIRE IN THE GULF OF FINLAND, AND THE CORVETTE "
             "MERKURY SINKS AT BENGHAZI AFTER A SEA-DRONE HIT.")
    p.wrapped(x, y + 104, body2, 2, INK, 38)
    p.rect(36, y + 226, W - 72, 2, INK)


def third_row(p):
    y = 716
    # column 1: India - Nepal
    p.text(36, y, "ASIA - INDIA + NEPAL", 2, RED)
    p.text(36, y + 22, "NEW EXPRESS TO", 3, INK)
    p.text(36, y + 46, "JANAKPUR, NEPAL", 3, INK)
    body = ("MODI AND NEPAL PM SHAH FLAG OFF THE SARYU-KAMALA "
            "EXPRESS. 8 MOUS SEAL CLOSER TIES.")
    p.wrapped(36, y + 74, body, 2, INK, 23)
    p.rect(322, y, 2, 160, GREY)
    # column 2: space and the Moon
    x = 344
    p.text(x, y, "SCIENCE - DEEP SPACE", 2, RED)
    p.text(x, y + 22, "PROBE REACHES", 3, INK)
    p.text(x, y + 46, "MERCURY ORBIT", 3, INK)
    body2 = ("ESA-JAXA BEPICOLOMBO ENTERS ORBIT AROUND "
             "MERCURY, A FIRST OF ITS KIND.")
    p.wrapped(x, y + 74, body2, 2, INK, 23)
    p.circle(362, y + 158, 12, YELLOW)
    p.text(386, y + 150, "SUPERMOON TONIGHT", 2, RED)
    p.rect(640, y, 2, 160, GREY)
    # column 3: around the world in brief
    x = 662
    p.text(x, y, "AROUND THE WORLD", 2, RED)
    briefs = (
        "LISBON MARCH OVER LIVING COSTS",
        "GAZA: TOXIC CONTAMINATION ALERT",
        "DHAKA VOWS ARREST IF HASINA RETURNS",
        "ARMENIA DRAFTS PEACE CONSTITUTION",
    )
    yy = y + 24
    for item in briefs:
        p.rect(x, yy + 4, 8, 8, RED)
        yy = p.wrapped(x + 18, yy, item, 2, INK, 25, leading=16) + 3
    p.rect(36, y + 170, W - 72, 2, INK)


def business_line(p):
    y = 894
    p.rect(36, y, W - 72, 26, DARK)
    line = "BUSINESS: FERRARI UNVEILS 296 CHALLENGE TWINS - INDIA OIL BILL UP 60%"
    p.text((W - p.text_w(line, 2)) // 2, y + 6, line, 2, WHITE)


def sports_bar(p):
    y = 928
    p.text(36, y, "SPORT", 3, RED)
    lines = (
        "PANT HITS 128 AS INDIA DRAW THE WELLINGTON TEST WITH NEW ZEALAND",
        "ALCARAZ BEATS ZVEREV FOR A FIRST ATP FINALS TITLE IN TURIN",
        "VERSTAPPEN WINS LAS VEGAS GP - GUKESH DEFENDS CHESS CROWN IN GENEVA",
    )
    yy = y + 2
    for line in lines:
        p.text(150, yy, line, 2, INK)
        yy += 19
    p.centred(990, "REPORTED 24 NOV 2026 - GUARDIAN - BBC - AP - AL JAZEERA - NYT", 2, GREY)


def build():
    p = Page()
    masthead(p)
    lead_story(p)
    second_row(p)
    third_row(p)
    business_line(p)
    sports_bar(p)
    return p


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    page = build()
    try:
        os.makedirs(out_dir, exist_ok=True)
        save_png(page, os.path.join(out_dir, "entry.png"))
    except OSError:
        if out_dir != "/output":
            os.makedirs("/output", exist_ok=True)
            save_png(page, "/output/entry.png")


if __name__ == "__main__":
    main()
