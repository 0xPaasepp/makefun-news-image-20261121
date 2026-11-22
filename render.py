#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261121 v2 entry.

Draws entry.png (1024x1024): one clean, professional broadsheet page summing
up Saturday 21 November 2026 — 37 verified stories from 9 regions, ranked by
consequence, every story dated that Saturday (UTC) with its outlets named.
All maps, diagrams and icons are drawn in code (Pillow); no photographs.
Build-time only: the graded program (main.py) just copies the finished
entry.png. Pillow is used here, at build time; main.py is pure stdlib.
No network, no randomness: same input, same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24                       # page margin
CW = W - 2 * M               # 976 content width
PAPER = (248, 244, 233)      # cream broadsheet
INK = (26, 26, 26)
GREY = (110, 108, 100)
RED = (178, 34, 34)
NAVY = (22, 38, 63)
RULE = (165, 160, 148)
LIGHT = (238, 233, 220)
WHITE = (255, 255, 255)
GOLD = (255, 210, 63)
PANEL = (240, 234, 218)      # drawn-panel background
PANEL_LINE = (120, 112, 96)
SEA = (198, 214, 222)        # light sea on the small maps
LANDC = (232, 220, 192)      # land fill on the cream map

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines top-down; returns the y below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def pill(d, x, y, text, fnt, fill, fg, outline=None):
    """Small rounded badge; returns the width used."""
    w = int(d.textlength(text, font=fnt)) + 12
    h = fnt.size + 7
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2,
                        fill=fill, outline=outline, width=1)
    d.text((x + w // 2, y + 3), text, font=fnt, fill=fg, anchor="ma")
    return w


def num_disc(d, cx, cy, n, r, fill, fg=WHITE):
    """Numbered disc; n is str."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=WHITE,
              width=1)
    d.text((cx, cy), n, font=font(SANS_B, int(r * 1.05)), fill=fg,
           anchor="mm")


# Region colours (also the pin colours). Order is the region-bar order.
REGION_COLOURS = {
    "Europe": (46, 90, 136),
    "Middle East": (176, 58, 46),
    "Americas": (46, 125, 50),
    "Africa": (106, 61, 154),
    "South Asia": (0, 137, 123),
    "East Asia": (230, 81, 0),
    "South-East Asia": (121, 85, 72),
    "Oceania": (194, 24, 91),
    "Global": (97, 97, 97),
}

# Simplified continent outlines, hand-drawn (lon, lat). Recognisable, not
# precise. Reused from the v1 renderer (our own entry's geometry).
NORTH_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 57),
    (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
    (-105, 20), (-97, 16), (-92, 15), (-86, 12), (-83, 9), (-79, 9),
    (-81, 13), (-84, 16), (-87, 21), (-90, 21), (-91, 19), (-96, 19),
    (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25), (-80, 32),
    (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47),
    (-55, 52), (-60, 55), (-65, 58), (-68, 58), (-72, 62), (-78, 62),
    (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
    (-155, 71), (-165, 68)]
SOUTH_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
    (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
    (-70, -54), (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -38),
    (-57, -34), (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9),
    (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6),
    (-62, 9), (-68, 11), (-72, 12), (-75, 10)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
    (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5),
    (13, -10), (12, -17), (14, -22), (16, -28), (19, -34), (26, -34),
    (32, -28), (35, -24), (40, -16), (40, -10), (42, -4), (46, -1), (51, 2),
    (51, 11), (48, 11), (44, 11), (40, 15), (38, 18), (37, 22), (35, 28),
    (32, 31), (30, 32), (25, 32), (20, 32), (15, 32), (11, 34), (10, 37),
    (5, 37)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
    (-2, 49), (0, 51), (3, 53), (5, 53), (8, 57), (10, 59), (5, 60),
    (5, 62), (10, 64), (12, 66), (18, 69), (25, 71), (30, 70), (35, 68),
    (40, 68), (44, 66), (48, 66), (50, 64), (46, 60), (44, 58), (40, 56),
    (38, 54), (35, 52), (33, 50), (30, 48), (28, 46), (26, 44), (23, 40),
    (22, 38), (26, 38), (28, 41), (30, 43), (28, 45), (24, 45), (20, 44),
    (18, 42), (19, 41), (18, 40), (16, 39), (16, 38), (15, 40), (13, 41),
    (11, 42), (10, 44), (8, 44), (3, 43), (-2, 37), (-6, 36)]
ASIA = [(27, 37), (30, 36), (36, 36), (35, 31), (39, 29), (43, 27),
    (43, 22), (43, 17), (43, 12), (46, 12), (50, 14), (55, 17), (59, 22),
    (57, 25), (54, 26), (51, 28), (48, 30), (52, 28), (56, 27), (58, 25),
    (61, 25), (65, 25), (68, 23), (70, 21), (72, 19), (74, 15), (76, 10),
    (77, 8), (80, 9), (80, 14), (83, 18), (87, 21), (90, 22), (92, 21),
    (94, 17), (96, 15), (98, 11), (100, 8), (102, 5), (104, 2), (103, 6),
    (101, 10), (100, 13), (102, 12), (105, 10), (108, 12), (109, 15),
    (107, 18), (108, 21), (110, 20), (113, 22), (116, 23), (119, 25),
    (121, 28), (122, 31), (120, 34), (122, 37), (124, 39), (126, 38),
    (128, 38), (130, 42), (133, 43), (136, 44), (139, 46), (141, 49),
    (142, 53), (141, 56), (143, 59), (147, 59), (151, 59), (156, 57),
    (158, 54), (161, 56), (163, 58), (162, 61), (164, 64), (168, 65),
    (172, 65), (176, 64), (180, 65), (178, 63), (174, 63), (170, 66),
    (166, 68), (162, 69), (158, 69), (154, 70), (150, 70), (146, 71),
    (142, 72), (138, 72), (134, 71), (130, 71), (126, 72), (122, 72),
    (118, 73), (114, 73), (110, 73), (106, 74), (102, 74), (98, 74),
    (94, 74), (90, 74), (86, 73), (82, 72), (78, 71), (74, 72), (70, 72),
    (66, 71), (62, 70), (58, 68), (54, 68), (50, 68), (46, 68), (42, 67),
    (38, 66), (34, 66), (31, 65), (32, 62), (30, 60), (28, 57), (26, 55),
    (24, 54), (22, 53), (24, 51), (26, 49), (28, 47), (28, 44), (27, 41),
    (27, 38)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38),
    (150, -37), (153, -32), (153, -27), (150, -23), (146, -19), (142, -15),
    (142, -11), (137, -12), (135, -15), (132, -12), (130, -13), (126, -14),
    (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 52), (1, 51),
    (-3, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
    (141, 39), (142, 42), (144, 44), (142, 44), (140, 41), (139, 38),
    (137, 36), (135, 34), (133, 33), (131, 32)]
NEW_ZEALAND = [(167, -45), (169, -43), (171, -42), (173, -41), (175, -40),
    (177, -38), (178, -37), (176, -39), (174, -41), (172, -43), (170, -44),
    (168, -46)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
    (45, -25), (43, -22), (43, -18)]
CONTINENTS = [NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EUROPE, ASIA,
              AUSTRALIA, UK, JAPAN, NEW_ZEALAND, MADAGASCAR]


# ---------------------------------------------------------------- data
# 37 stories, all verified against reporting of Saturday 21 November 2026
# (UTC). 3 leads + 10 cards + 24 in the ALSO list. Region counts sum to 37.
# Badge: C = CONFIRMED (2+ major outlets), O = OFFICIAL (on the record),
# R = REPORTED (one major outlet). Sources are named under every story.

TIMELINE = [
    ("00:09", "M6.7 Jun\u00edn quake"),
    ("c.04:00", "Geneva talks end"),
    ("06:50", "Sparta II alarm"),
    ("09:42", "M6.8 Banda Sea"),
    ("12:12", "EU\u2013Indonesia signed"),
    ("18:24", "BepiColombo orbit"),
    ("c.22:00", "COP31 pause"),
]

STATS = [
    ("2", "tankers attacked off Khasab,\nStrait of Hormuz", "UKMTO"),
    ("130+", "countries want fossil fuels\nnamed at COP31", "AFP"),
    ("730m", "people in the new EU\u2013\nIndonesia trade area", "EU COMMISSION"),
    ("$55,100", "Bitcoin's low, its lowest\nsince September 2024", "COINBASE"),
    ("128", "states at the Geneva\nautonomous-weapons talks", "DW"),
    ("8 yrs", "BepiColombo's journey\nfrom Earth to Mercury", "ESA"),
]

# (region, count) — sums to 37.
REGIONS = [("Europe", 9), ("Middle East", 6), ("Americas", 6),
           ("Africa", 3), ("South Asia", 3), ("East Asia", 3),
           ("South-East Asia", 3), ("Oceania", 1), ("Global", 3)]

LEADS = [
    {"num": "1", "place": "BAHRAIN / HORMUZ", "field": "CONFLICT",
     "region": "Middle East", "badge": "CONFIRMED",
     "head": "Iran strikes Bahrain as tankers hit in Hormuz",
     "body": "Bahrain says an Iranian attack set a civilian industrial site "
             "ablaze; no one was hurt. The Revolutionary Guards say they hit "
             "US positions. UKMTO: two tankers attacked off Khasab.",
     "src": "AL JAZEERA \u00b7 REUTERS \u00b7 AFP",
     "panel": "hormuz"},
    {"num": "2", "place": "GULF OF FINLAND", "field": "CONFLICT",
     "region": "Europe", "badge": "CONFIRMED",
     "head": "Drones set Russian cargo ship ablaze off Finland",
     "body": "Sparta II, bound for Kaliningrad, was hit about 06:50 UTC and "
             "drifted into Finnish waters; the 16 crew were taken off. "
             "Finland: Ukraine likely behind it.",
     "src": "BBC \u00b7 FRANCE 24 \u00b7 MOSCOW TIMES",
     "panel": "sparta"},
    {"num": "3", "place": "COP31, ANTALYA", "field": "CLIMATE",
     "region": "Global", "badge": "CONFIRMED",
     "head": "COP31 deadlocked over fossil fuels in overtime",
     "body": "A day past deadline in Antalya, talks paused overnight. The EU "
             "and Pacific states reject a draft omitting fossil fuels; 130+ "
             "countries want them named.",
     "src": "BBC \u00b7 AFP \u00b7 FRANCE 24",
     "panel": "cop31"},
]

# Cards 4-13: (num, place, field, region, badge, head, big, biglabel,
#               body, src, icon)
CARDS = [
    ("4", "BRUSSELS", "TRADE", "Europe", "CONFIRMED",
     "EU and Indonesia sign trade pact after 10 years",
     "98.5%", "OF TARIFFS",
     "Lifts 98.5% of tariffs on EU goods; 730m people in the new trade area.",
     "DW \u00b7 AFP \u00b7 ANTARA", "flags"),
    ("5", "SINALOA", "SECURITY", "Americas", "CONFIRMED",
     "Mexico seizes \u2018El Chapo Isidro\u2019 in army raid",
     "11", "DEAD",
     "FBI most-wanted; 7 gunmen, 4 soldiers killed.",
     "GUARDIAN \u00b7 DW \u00b7 NYT", "cuffs"),
    ("6", "GENEVA", "AI WEAPONS", "Europe", "CONFIRMED",
     "UN \u2018killer robot\u2019 talks end with no binding treaty",
     "2028", "TARGET",
     "128 states agree to two more years of talks.",
     "DW \u00b7 GUARDIAN \u00b7 NPR", "drone"),
    ("7", "MERCURY", "SCIENCE", "Global", "OFFICIAL",
     "BepiColombo enters orbit around Mercury",
     "18:24", "UTC",
     "Europe\u2013Japan probe, 8 years out; 37-minute burn.",
     "ESA \u00b7 AP \u00b7 SPACE.COM", "planet"),
    ("8", "BAYELSA", "DISASTER", "Africa", "CONFIRMED",
     "Nigeria funeral boat toll reaches 24",
     "24", "DEAD",
     "Capsized Fri, Ayama\u2013Ukubie; toll given Sat (NEMA).",
     "DW \u00b7 AP \u00b7 SKY NEWS", "boat"),
    ("9", "BANDA SEA", "QUAKE", "South-East Asia", "CONFIRMED",
     "Deep quake shakes Timor-Leste and Darwin",
     "M6.8", "09:42 UTC",
     "132 km deep, 105 km NE of Lospalos; felt in Darwin.",
     "USGS \u00b7 ABC AUSTRALIA", "seismo"),
    ("10", "MANIPUR", "HEALTH", "South Asia", "CONFIRMED",
     "Tainted alcohol kills 11 in India\u2019s Manipur",
     "11", "DEAD",
     "More than 180 in hospital; inquiry ordered.",
     "REUTERS \u00b7 SCMP \u00b7 CNA", "bottle"),
    ("11", "TWICKENHAM", "RUGBY", "Europe", "CONFIRMED",
     "England beat All Blacks by record margin",
     "37\u201312", "FULL TIME",
     "25 points: their biggest win over New Zealand.",
     "BBC \u00b7 REUTERS \u00b7 STUFF", "posts"),
    ("12", "OSAKA", "MUSIC", "East Asia", "CONFIRMED",
     "BTS take five MAMA awards, two grand prizes",
     "5", "AWARDS",
     "Album of the Year for \u2018Arirang\u2019.",
     "YONHAP \u00b7 FINANCIAL EXPRESS", "trophy"),
    ("13", "FRANCE", "PROTEST", "Europe", "CONFIRMED",
     "Sixth Saturday of cost-of-living marches",
     "82,500", "MARCHERS",
     "Ministry count; organisers say 150,000.",
     "AFP \u00b7 FRANCE 24 \u00b7 LE MONDE", "placards"),
]

# ALSO list 14-37, in order of consequence:
# (num, place, text, src, badge)
ALSO = [
    ("14", "Bitcoin", "$55,100, lowest since Sep 2024",
     "COINBASE", "C"),
    ("15", "Basra", "power-station fire kills 4, 35 hurt",
     "INA \u00b7 REUTERS", "C"),
    ("16", "Las Vegas", "Verstappen takes pole on penalties",
     "F1 \u00b7 AP", "C"),
    ("17", "Rabat", "CAF\u2019s 54 nations back Infantino",
     "CAF \u00b7 VON", "C"),
    ("18", "Brazil", "mosquitoes cut dengue 69% in trial",
     "AP", "R"),
    ("19", "Jerusalem", "Esenkot invites Likud to talks",
     "AFP, TOI", "C"),
    ("20", "Kyiv", "bridge strike a \u2018fair response\u2019",
     "BBC, KI", "C"),
    ("21", "Gaza City", "food-vehicle strike kills three",
     "REUTERS, AFP", "C"),
    ("22", "Riyadh", "coalition downed 3 Houthi missiles",
     "AJ, REUTERS", "C"),
    ("23", "Beirut", "Aoun wants pull-out, end to meddling",
     "AJ, TOI", "C"),
    ("24", "Brussels", "EU budget: \u20ac204bn cut, tech tax",
     "DW, AFP", "C"),
    ("25", "Bras\u00edlia", "Bolsonaro moved to intensive care",
     "REUTERS, AJ", "C"),
    ("26", "Jun\u00edn", "M6.7 quake, 00:09 UTC, no deaths", "USGS, AP", "C"),
    ("27", "Washington", "FBI probes crime-database breach", "BBC, CBC", "C"),
    ("28", "Serang", "factory fire: 3 dead, 36 missing", "BBC, GUARDIAN",
     "C"),
    ("29", "Hanoi", "law to speed land expropriation passed",
     "REUTERS", "R"),
    ("30", "Mastung", "forces kill 15 militants", "DAWN, TRIBUNE", "C"),
    ("31", "Beijing", "Wong meets Li Qiang; 20+ deals", "ST, BT", "C"),
    ("32", "Qinghai", "M5.9 quake, 10:45 UTC, remote west", "USGS", "O"),
    ("33", "Savar", "80 garment factories shut", "TBS, D. STAR", "C"),
    ("34", "Dublin", "Ireland beat South Africa 20\u201317",
     "BBC, SUPERSPORT", "C"),
    ("35", "Turin", "Alcaraz beats Shelton; faces Zverev", "BBC, AFP", "C"),
    ("36", "Australia", "hosts beat England by 3 wickets", "BBC, AP", "C"),
    ("37", "Niger State", "gunmen kill village head in raid", "D. TRUST, PT",
     "C"),
]

# Regions for the ALSO list, in the same order (pin colours).
ALSO_REGIONS = ["Global", "Middle East", "Americas", "Africa",
                "Americas", "Middle East", "Europe", "Middle East",
                "Middle East", "Middle East", "Europe", "Americas",
                "Americas", "Americas", "South-East Asia", "South-East Asia",
                "South Asia", "East Asia", "East Asia", "South Asia",
                "Europe", "Europe", "Oceania", "Africa"]

# Map pins (lon, lat) for stories 1-13. 7 (Mercury) has no pin: it is in
# orbit, not on Earth; the key says so.
PINS = [
    (50.6, 26.2),    # 1 Bahrain
    (23.5, 59.8),    # 2 Sparta II, Gulf of Finland
    (30.7, 36.9),    # 3 Antalya
    (4.4, 50.8),     # 4 Brussels
    (-108.5, 25.6),  # 5 Guasave, Sinaloa
    (6.1, 46.2),     # 6 Geneva
    None,             # 7 Mercury — in orbit, no pin
    (6.3, 4.8),      # 8 Bayelsa, Nigeria
    (128.0, -7.9),   # 9 Banda Sea
    (94.0, 24.5),    # 10 Manipur
    (-0.3, 51.5),    # 11 Twickenham
    (135.5, 34.7),   # 12 Osaka
    (2.4, 48.9),     # 13 Paris
]
PIN_REGIONS = ["Middle East", "Europe", "Global", "Europe", "Americas",
               "Europe", "Global", "Africa", "South-East Asia",
               "South Asia", "Europe", "East Asia", "Europe"]


# ---------------------------------------------------------------- panels
# All three lead panels and the ten card icons are drawn in code.

def draw_hormuz_panel(d, x, y, w, h):
    """Schematic Strait of Hormuz: sea, shores, Bahrain, two tankers hit."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=PANEL_LINE, width=1)
    # Iran (top land), Arabia (bottom land), Oman (right).
    d.polygon([(x, y), (x + w, y), (x + w, y + 26), (x + int(w * 0.62), y + 30),
               (x + int(w * 0.55), y + 44), (x, y + 40)], fill=LANDC,
              outline=PANEL_LINE)
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + int(h * 0.62)),
               (x + int(w * 0.55), y + int(h * 0.58)), (x, y + int(h * 0.66))],
              fill=LANDC, outline=PANEL_LINE)
    d.polygon([(x + int(w * 0.82), y + int(h * 0.42)), (x + w, y + int(h * 0.38)),
               (x + w, y + h), (x + int(w * 0.86), y + h)], fill=LANDC,
              outline=PANEL_LINE)
    f = font(SANS_B, 10)
    f2 = font(SANS, 9)
    d.text((x + 8, y + 5), "IRAN", font=f, fill=INK)
    d.text((x + 8, y + h - 14), "SAUDI ARABIA", font=f2, fill=GREY)
    d.text((x + w - 34, y + h - 14), "OMAN", font=f2, fill=GREY)
    # Bahrain: small island with a star.
    bx, by = x + int(w * 0.30), y + int(h * 0.52)
    d.ellipse([bx - 7, by - 5, bx + 7, by + 5], fill=LANDC,
              outline=PANEL_LINE)
    d.text((bx, by - 16), "BAHRAIN", font=f, fill=RED, anchor="ma")
    for dx, dy in [(0, -4), (3, -1), (2, 3), (-2, 3), (-3, -1)]:
        d.line([(bx, by - 5), (bx + dx, by + dy)], fill=RED, width=1)
    d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=RED)
    # Strait: dashed red route with two tanker hits.
    d.line([(x + int(w * 0.42), y + int(h * 0.30)),
            (x + int(w * 0.78), y + int(h * 0.66))], fill=RED, width=1)
    for tx, ty in [(x + int(w * 0.55), y + int(h * 0.42)),
                   (x + int(w * 0.68), y + int(h * 0.55))]:
        d.rectangle([tx - 6, ty - 3, tx + 6, ty + 3], fill=INK)
        d.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], outline=RED, width=2)
        d.text((tx, ty - 13), "\u2726", font=font(SANS_B, 10), fill=RED,
               anchor="ma")
    d.text((x + int(w * 0.52), y + int(h * 0.72)),
           "STRAIT OF HORMUZ \u2014 2 tankers hit", font=f2, fill=INK,
           anchor="ma")
    d.text((x + w - 4, y + 4), "KHASAB", font=f2, fill=GREY, anchor="ra")


def draw_sparta_panel(d, x, y, w, h):
    """Cargo ship ablaze at night + small Gulf of Finland locator."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 42, 58), outline=PANEL_LINE,
                width=1)
    # Sea.
    d.rectangle([x, y + int(h * 0.66), x + w, y + h], fill=(52, 84, 110))
    d.line([(x, y + int(h * 0.66)), (x + w, y + int(h * 0.66))],
           fill=(120, 160, 190), width=1)
    f = font(SANS_B, 10)
    f2 = font(SANS, 9)
    d.text((x + 8, y + 5), "SPARTA II", font=f, fill=WHITE)
    # Ship: long hull with slanted bow, containers in a neat row, stern
    # superstructure. Hull sits on the waterline.
    hx, hy = x + int(w * 0.08), y + int(h * 0.58)
    hw = int(w * 0.60)
    d.polygon([(hx, hy), (hx + hw, hy), (hx + hw - 10, hy + 12),
               (hx + 4, hy + 12)], fill=(178, 44, 36))
    d.line([(hx, hy), (hx + hw, hy)], fill=WHITE, width=2)
    for i in range(5):
        cx = hx + 10 + i * 20
        d.rectangle([cx, hy - 14, cx + 17, hy - 2],
                    fill=(220, 180, 60) if i % 2 == 0 else (200, 120, 50),
                    outline=INK, width=1)
    d.rectangle([hx + 4, hy - 26, hx + 22, hy - 14], fill=WHITE,
                outline=INK, width=1)
    # Fire amidships, layered; smoke rises up-right, kept inside the panel.
    fx, fy = hx + int(hw * 0.52), hy - 12
    d.polygon([(fx - 14, fy), (fx - 5, fy - 20), (fx + 1, fy - 8),
               (fx + 7, fy - 22), (fx + 15, fy)], fill=(255, 150, 0))
    d.polygon([(fx - 6, fy), (fx - 1, fy - 11), (fx + 6, fy)],
              fill=(255, 220, 80))
    for sx, sy, sr in [(fx + 20, fy - 14, 5), (fx + 28, fy - 20, 6),
                       (fx + 37, fy - 26, 7)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(110, 110, 110))
    d.text((x + 8, y + h - 14), "06:50 UTC \u00b7 two drones \u00b7 crew taken off",
           font=f2, fill=WHITE)
    # Locator: Finland / Gulf of Finland, red dot where she was hit.
    lx, ly, lw, lh = x + w - 62, y + 6, 56, 40
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=LANDC,
                outline=PANEL_LINE, width=1)
    d.polygon([(lx + 8, ly + 4), (lx + 30, ly + 4), (lx + 34, ly + 18),
               (lx + 12, ly + 20)], fill=(180, 200, 220))
    d.text((lx + 4, ly + lh - 10), "FINLAND", font=font(SANS, 7), fill=GREY)
    d.ellipse([lx + 38 - 3, ly + 26 - 3, lx + 38 + 3, ly + 26 + 3], fill=RED)


def draw_cop31_panel(d, x, y, w, h):
    """Draft text with fossil fuels missing + overtime clock."""
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_LINE, width=1)
    # Draft document, left.
    dx, dy, dw, dh = x + 8, y + 8, int(w * 0.56), h - 16
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=WHITE, outline=RULE, width=1)
    f = font(SANS_B, 9)
    f2 = font(SANS, 8)
    d.text((dx + 6, dy + 4), "DRAFT TEXT", font=f, fill=INK)
    yy = dy + 18
    for ln in ["A day past the deadline,",
               "the draft still has",
               "no mention of",
               "coal, oil or gas."]:
        d.text((dx + 6, yy), ln, font=f2, fill=GREY)
        yy += 10
    d.text((dx + 6, dy + dh - 14), "fossil fuels", font=font(SANS_B, 11),
           fill=RED)
    d.line([(dx + 6, dy + dh - 8), (dx + 62, dy + dh - 8)], fill=RED, width=2)
    # Clock, right.
    cx, cy, r = x + int(w * 0.78), y + int(h * 0.42), 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=INK,
              width=2)
    d.line([(cx, cy), (cx, cy - 14)], fill=INK, width=2)
    d.line([(cx, cy), (cx + 10, cy + 4)], fill=INK, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=INK)
    d.text((cx, cy + r + 4), "OVERTIME", font=font(SANS_B, 10), fill=RED,
           anchor="ma")
    d.text((cx, y + h - 12), "day 13 of 12", font=font(SANS, 9), fill=GREY,
           anchor="ma")


def draw_icon(d, kind, x, y, w, h):
    """Small drawn pictogram for a numbered card."""
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_LINE, width=1)
    cx, cy = x + w // 2, y + h // 2
    if kind == "flags":
        d.rectangle([x + 8, y + 8, x + 24, y + 20], fill=(0, 51, 153))
        for i in range(5):
            d.ellipse([x + 12 + i * 2, y + 12, x + 14 + i * 2, y + 14],
                      fill=GOLD)
        d.rectangle([x + 30, y + 8, x + 46, y + 20], fill=RED)
        d.rectangle([x + 30, y + 14, x + 46, y + 20], fill=WHITE)
        d.text((cx, y + h - 12), "EU \u00b7 IDN", font=font(SANS_B, 8),
               fill=INK, anchor="ma")
    elif kind == "cuffs":
        d.ellipse([x + 10, y + 8, x + 24, y + 22], outline=INK, width=2)
        d.ellipse([x + 30, y + 8, x + 44, y + 22], outline=INK, width=2)
        d.line([(x + 24, y + 15), (x + 30, y + 15)], fill=INK, width=2)
        d.text((cx, y + h - 12), "FBI TOP 10", font=font(SANS_B, 8),
               fill=INK, anchor="ma")
    elif kind == "drone":
        for px, py in [(x + 12, y + 10), (x + 42, y + 10), (x + 12, y + 26),
                       (x + 42, y + 26)]:
            d.ellipse([px - 5, py - 5, px + 5, py + 5], outline=INK, width=1)
        d.rectangle([x + 22, y + 13, x + 32, y + 23], fill=INK)
        d.text((cx, y + h - 12), "LAWS", font=font(SANS_B, 8), fill=INK,
               anchor="ma")
    elif kind == "planet":
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(150, 150, 150),
                  outline=INK, width=1)
        d.ellipse([cx - 18, cy - 6, cx + 18, cy + 6], outline=INK, width=1)
        d.ellipse([cx + 12 - 3, cy - 12 - 3, cx + 12 + 3, cy - 12 + 3],
                  fill=RED)
        d.text((cx, y + h - 12), "8 YRS OUT", font=font(SANS_B, 8), fill=INK,
               anchor="ma")
    elif kind == "boat":
        d.polygon([(x + 10, y + 22), (x + 44, y + 14), (x + 44, y + 20),
                   (x + 14, y + 28)], fill=(120, 70, 40))
        for wy in (y + 30, y + 34):
            d.line([(x + 8, wy), (x + 46, wy)], fill=(60, 120, 160), width=1)
        d.text((cx, y + h - 12), "BAYELSA", font=font(SANS_B, 8), fill=INK,
               anchor="ma")
    elif kind == "seismo":
        pts = [(x + 8, cy + 4), (x + 16, cy + 4), (x + 20, cy - 10),
               (x + 24, cy + 10), (x + 28, cy - 6), (x + 32, cy + 4),
               (x + 46, cy + 4)]
        d.line(pts, fill=RED, width=2)
        d.text((cx, y + h - 12), "132 KM DEEP", font=font(SANS_B, 8),
               fill=INK, anchor="ma")
    elif kind == "bottle":
        d.rectangle([x + 22, y + 8, x + 32, y + 30], fill=(60, 90, 60))
        d.rectangle([x + 24, y + 4, x + 30, y + 8], fill=INK)
        d.polygon([(x + 38, y + 10), (x + 48, y + 26), (x + 28, y + 26)],
                  outline=RED, width=2)
        d.text((cx + 38, y + 16), "!", font=font(SANS_B, 10), fill=RED,
               anchor="ma")
        d.text((cx, y + h - 12), "CHANDEL", font=font(SANS_B, 8), fill=INK,
               anchor="ma")
    elif kind == "posts":
        d.line([(x + 14, y + 8), (x + 14, y + 30)], fill=INK, width=2)
        d.line([(x + 40, y + 8), (x + 40, y + 30)], fill=INK, width=2)
        d.line([(x + 14, y + 16), (x + 40, y + 16)], fill=INK, width=2)
        d.ellipse([x + 24, y + 18, x + 30, y + 26], fill=(120, 70, 40))
        d.text((cx, y + h - 12), "TWICKENHAM", font=font(SANS_B, 8),
               fill=INK, anchor="ma")
    elif kind == "trophy":
        d.polygon([(x + 22, y + 8), (x + 32, y + 8), (x + 30, y + 22),
                   (x + 24, y + 22)], fill=GOLD, outline=INK, width=1)
        d.line([(x + 22, y + 12), (x + 16, y + 12)], fill=INK, width=2)
        d.line([(x + 32, y + 12), (x + 38, y + 12)], fill=INK, width=2)
        d.rectangle([x + 20, y + 26, x + 34, y + 30], fill=INK)
        d.text((cx, y + h - 12), "MAMA", font=font(SANS_B, 8), fill=INK,
               anchor="ma")
    elif kind == "placards":
        for i, px in enumerate((x + 12, x + 24, x + 36)):
            d.line([(px, y + 18), (px, y + 32)], fill=INK, width=2)
            d.rectangle([px - 6, y + 8, px + 6, y + 18],
                        fill=(200, 60, 40) if i != 1 else (46, 90, 136))
        d.text((cx, y + h - 12), "PARIS", font=font(SANS_B, 8), fill=INK,
               anchor="ma")


# ---------------------------------------------------------------- sections
def draw_kicker(d):
    f = font(SANS_B, 11)
    d.text((M, 8), "THE WORLD IN ONE DAY", font=f, fill=INK)
    d.text((W // 2, 8), "DAY 325 OF 2026", font=f, fill=RED, anchor="ma")
    d.text((W - M, 8), "ALL TIMES UTC \u00b7 RANKED BY CONSEQUENCE", font=f,
           fill=INK, anchor="ra")
    d.line([(M, 26), (W - M, 26)], fill=INK, width=2)
    return 32


def draw_masthead(d, y):
    d.text((W // 2, y), "Saturday 21 November 2026",
           font=font(SERIF_B, 54), fill=INK, anchor="ma")
    y += 62
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    d.line([(M, y + 3), (W - M, y + 3)], fill=INK, width=1)
    y += 10
    f = font(SANS_B, 13)
    black = "37 STORIES, 9 REGIONS, EVERY ONE DATED "
    red = "SATURDAY 21 NOVEMBER 2026"
    full_w = d.textlength(black + red, font=f)
    x0 = W // 2 - full_w // 2
    d.text((x0, y), black, font=f, fill=INK)
    d.text((x0 + d.textlength(black, font=f), y), red, font=f, fill=RED)
    y += 20
    d.text((W // 2, y),
           "Iran strikes Bahrain as tankers hit in Hormuz  \u25c6  Drones set "
           "Russian cargo ship ablaze off Finland  \u25c6  COP31 deadlocked "
           "over fossil fuels in overtime",
           font=font(SERIF_I, 15), fill=INK, anchor="ma")
    return y + 22


def draw_timeline(d, y):
    f_lab = font(SANS_B, 11)
    d.rectangle([M, y, M + 108, y + 18], fill=INK)
    d.text((M + 54, y + 2), "THE DAY IN UTC", font=f_lab, fill=WHITE,
           anchor="ma")
    x0, x1 = M + 118, W - M
    f_t = font(SANS_B, 10)
    f_x = font(SANS, 8)
    n = len(TIMELINE)
    ym = y + 26
    d.line([(x0, ym), (x1, ym)], fill=INK, width=2)
    for i, (t, label) in enumerate(TIMELINE):
        cx = x0 + (i + 0.5) * (x1 - x0) / n
        d.ellipse([cx - 3, ym - 3, cx + 3, ym + 3], fill=RED, outline=WHITE,
                  width=1)
        above = (i % 2 == 0)
        ty = y + 2 if above else ym + 6
        d.text((cx, ty), t, font=f_t, fill=RED, anchor="ma")
        d.text((cx, ty + 11), label, font=f_x, fill=INK, anchor="ma")
    return y + 54


def draw_stats(d, y):
    n = len(STATS)
    gap = 6
    bw = (CW - gap * (n - 1)) // n
    f_num = font(SERIF_B, 23)
    f_lab = font(SANS, 9)
    f_src = font(SANS_B, 8)
    for i, (num, lab, src) in enumerate(STATS):
        x0 = M + i * (bw + gap)
        d.rectangle([x0, y, x0 + bw, y + 46], outline=RULE, width=1)
        nw = d.textlength(num, font=f_num)
        d.text((x0 + 7, y + 11), num, font=f_num, fill=INK)
        lx = x0 + 7 + nw + 6
        lab_w = x0 + bw - 6 - lx
        lines = []
        for raw in lab.split("\n"):
            lines.extend(wrap(d, raw, f_lab, lab_w))
        yy = y + 5
        for ln in lines[:3]:
            d.text((lx, yy), ln, font=f_lab, fill=INK)
            yy += 11
        d.text((lx, yy + 1), src, font=f_src, fill=GREY)
    return y + 50


def draw_regions(d, y):
    n = len(REGIONS)
    bw = CW // n
    f = font(SANS_B, 9)
    for i, (name, cnt) in enumerate(REGIONS):
        x0 = M + i * bw
        w = bw if i < n - 1 else CW - i * bw
        d.rectangle([x0, y, x0 + w, y + 16], fill=REGION_COLOURS[name])
    for i, (name, cnt) in enumerate(REGIONS):
        x0 = M + i * bw
        w = bw if i < n - 1 else CW - i * bw
        d.text((x0 + w // 2, y + 3), "%s %d" % (name, cnt), font=f,
               fill=WHITE, anchor="ma")
    return y + 20


def draw_leads(d, y):
    col_w = (CW - 2 * 12) // 3
    panel_h = 84
    f_kick = font(SANS_B, 10)
    f_head = font(SERIF_B, 20)
    f_body = font(SERIF, 12)
    f_src = font(SANS, 9)
    top = y
    bottom = top
    for i, lead in enumerate(LEADS):
        x = M + i * (col_w + 12)
        if lead["panel"] == "hormuz":
            draw_hormuz_panel(d, x, y, col_w, panel_h)
        elif lead["panel"] == "sparta":
            draw_sparta_panel(d, x, y, col_w, panel_h)
        else:
            draw_cop31_panel(d, x, y, col_w, panel_h)
        yy = y + panel_h + 6
        num_disc(d, x + 8, yy + 8, lead["num"], 8,
                 REGION_COLOURS[lead["region"]])
        d.text((x + 20, yy), "%s \u00b7 %s" % (lead["place"], lead["field"]),
               font=f_kick, fill=RED)
        bw = pill(d, x + col_w - 74, yy - 1, lead["badge"],
                  font(SANS_B, 8), INK, WHITE)
        yy += 20
        yy = block(d, x, yy, wrap(d, lead["head"], f_head, col_w), f_head,
                   leading=22)
        yy += 3
        yy = block(d, x, yy, wrap(d, lead["body"], f_body, col_w), f_body,
                   leading=14)
        yy += 3
        d.text((x, yy), lead["src"], font=f_src, fill=GREY)
        bottom = max(bottom, yy + 12)
    for i in range(2):
        x = M + (i + 1) * col_w + i * 12 + 6
        d.line([(x, top), (x, bottom)], fill=RULE, width=1)
    return bottom + 4


def draw_cards(d, y):
    cols, rows = 5, 2
    gap_x, gap_y = 8, 10
    cw = (CW - gap_x * (cols - 1)) // cols
    f_lab = font(SANS_B, 9)
    f_head = font(SERIF_B, 13)
    f_body = font(SERIF, 10)
    f_big = font(SERIF_B, 20)
    f_biglab = font(SANS, 8)
    f_src = font(SANS, 8)
    row_h = 104
    for i, (num, place, field, region, badge, head, big, biglab, body,
            src, icon) in enumerate(CARDS):
        r, c = divmod(i, cols)
        x = M + c * (cw + gap_x)
        yy = y + r * (row_h + gap_y)
        d.line([(x, yy - 3), (x + cw, yy - 3)], fill=REGION_COLOURS[region],
               width=2)
        num_disc(d, x + 7, yy + 7, num, 7, REGION_COLOURS[region])
        d.text((x + 17, yy), "%s \u00b7 %s" % (place, field), font=f_lab,
               fill=INK)
        pill(d, x + cw - 62, yy - 1, badge, font(SANS_B, 7), INK, WHITE)
        yy += 17
        # Left: icon panel + big number. Right: headline + body + source.
        iw = 56
        draw_icon(d, icon, x, yy, iw, 42)
        d.text((x + iw // 2, yy + 46), big, font=f_big, fill=INK,
               anchor="ma")
        d.text((x + iw // 2, yy + 68), biglab, font=f_biglab, fill=GREY,
               anchor="ma")
        tx = x + iw + 6
        tw = cw - iw - 6
        ty = yy
        ty = block(d, tx, ty, wrap(d, head, f_head, tw), f_head, leading=15)
        ty += 2
        ty = block(d, tx, ty, wrap(d, body, f_body, tw), f_body, leading=12)
        ty += 2
        d.text((tx, ty), src, font=f_src, fill=GREY)
    return y + rows * row_h + gap_y


def draw_bottom(d, y):
    # Left: world map with numbered pins. Right: ALSO list 14-37.
    map_w, map_h = 400, 188
    d.text((M, y), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=INK)
    d.text((M, y + 13),
           "pin numbers match the stories; pin colour is the region",
           font=font(SANS, 9), fill=GREY)
    my = y + 26
    d.rectangle([M, my, M + map_w, my + map_h - 26], fill=(245, 240, 226),
                outline=RULE, width=1)
    mh = map_h - 26

    def proj(lon, lat):
        return (M + (lon + 168) / 360.0 * map_w,
                my + (83 - lat) / 138.0 * mh)

    for lon in range(-180, 181, 30):
        xx = M + (lon + 168) / 360.0 * map_w
        d.line([(xx, my), (xx, my + mh)], fill=(225, 218, 200), width=1)
    for lat in range(-60, 91, 30):
        yy = my + (83 - lat) / 138.0 * mh
        d.line([(M, yy), (M + map_w, yy)], fill=(225, 218, 200), width=1)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LANDC,
                  outline=(200, 190, 160))
    for i, pin in enumerate(PINS):
        if pin is None:
            continue
        px, py = proj(*pin)
        col = REGION_COLOURS[PIN_REGIONS[i]]
        num_disc(d, px, py, str(i + 1), 8, col)
    d.text((M, my + mh + 4), "7 Mercury is in orbit, not on Earth \u2014 no pin.",
           font=font(SANS, 9), fill=GREY)
    # ALSO list.
    ax = M + map_w + 14
    aw = W - M - ax
    d.text((ax, y), "ALSO ON SATURDAY 21 NOVEMBER 2026",
           font=font(SANS_B, 11), fill=INK)
    d.text((ax, y + 13), "24 more stories, in order of consequence",
           font=font(SANS, 9), fill=GREY)
    ay = y + 26
    col_w = (aw - 10) // 2
    f_place = font(SANS_B, 9)
    f_text = font(SANS, 9)
    f_text_s = font(SANS, 8)
    f_src = font(SANS, 7)
    f_badge = font(SANS_B, 8)
    row_h = 14
    for ci in range(2):
        col = ALSO[ci * 12:(ci + 1) * 12]
        x = ax + ci * (col_w + 10)
        yy = ay
        for j, (num, place, text, src, badge) in enumerate(col):
            num_disc(d, x + 7, yy + 7, num, 7,
                     REGION_COLOURS[ALSO_REGIONS[ci * 12 + j]])
            # Badge letter disc at the row's right end.
            bx = x + col_w - 7
            d.ellipse([bx - 6, yy + 1, bx + 6, yy + 13],
                      outline=INK, width=1)
            d.text((bx, yy + 7), badge, font=f_badge, fill=INK, anchor="mm")
            # Place + text, then source right-aligned before the badge.
            sw = d.textlength(src, font=f_src)
            sx = bx - 10 - sw
            d.text((sx, yy + 3), src, font=f_src, fill=GREY)
            tx = x + 16
            avail = sx - 4 - tx
            # Place in bold, then the headline; truncate the headline
            # (word by word) so the row never overflows its column.
            d.text((tx, yy + 2), place, font=f_place, fill=INK)
            pw = d.textlength(place, font=f_place)
            rest = "\u2014 " + text
            rest_avail = avail - pw - 3
            fnt = f_text
            while d.textlength(rest, font=fnt) > rest_avail:
                base = rest[:-2] if rest.endswith(" \u2026") else rest
                cut = base.rsplit(" ", 1)[0] if " " in base else ""
                if not cut or cut == base:
                    break
                rest = cut + " \u2026"
            if d.textlength(rest, font=fnt) > rest_avail:
                fnt = f_text_s
                while d.textlength(rest, font=fnt) > rest_avail:
                    base = rest[:-2] if rest.endswith(" \u2026") else rest
                    cut = base.rsplit(" ", 1)[0] if " " in base else ""
                    if not cut or cut == base:
                        break
                    rest = cut + " \u2026"
            d.text((tx + pw + 3, yy + 2), rest, font=fnt, fill=INK)
            yy += row_h
    return max(my + map_h + 4, ay + 12 * row_h)


def draw_datecheck(d, y):
    d.rectangle([M, y, W - M, y + 44], fill=NAVY)
    f = font(SANS, 10)
    fb = font(SANS_B, 10)
    d.text((M + 10, y + 4), "DATE CHECK \u2014 ", font=fb, fill=GOLD)
    w0 = d.textlength("DATE CHECK \u2014 ", font=fb)
    d.text((M + 10 + w0, y + 4),
           "Well-known stories left out: they belong to another day (UTC).",
           font=f, fill=WHITE)
    d.text((M + 10, y + 18),
           "Fri 20 Nov: Russian missiles land in Poland \u00b7 Denmark expels "
           "Russian attach\u00e9 \u00b7 Wall Street tech sell-off \u00b7 GTA VI "
           "sales record.",
           font=f, fill=WHITE)
    d.text((M + 10, y + 31),
           "Sun 22 Nov: Verstappen wins Las Vegas GP \u00b7 new COP31 draft "
           "\u00b7 India declare at 720-9.",
           font=f, fill=WHITE)
    return y + 44


def draw_legend_footer(d, y):
    f = font(SANS, 9)
    fb = font(SANS_B, 9)
    x = M
    d.rectangle([x, y, x + 64, y + 13], fill=INK)
    d.text((x + 32, y + 1), "HOW SURE", font=fb, fill=WHITE, anchor="ma")
    x += 72
    for tag, desc in [("CONFIRMED", "2+ major outlets"),
                      ("OFFICIAL", "on the record: agency, ministry, federation"),
                      ("REPORTED", "one major outlet")]:
        w = pill(d, x, y, "\u25cf " + tag, font(SANS_B, 8), INK, WHITE)
        x += w + 4
        d.text((x, y + 1), desc, font=f, fill=GREY)
        x += d.textlength(desc, font=f) + 12
    d.text((W - M, y + 1), "Outlets named under every story \u00b7 times in "
           "UTC, c. = about", font=f, fill=GREY, anchor="ra")
    y += 18
    d.text((W // 2, y),
           "Every story here happened or was first reported on Saturday "
           "21 November 2026 (UTC), told as the named outlets reported it. "
           "All maps and drawings are original vector work.",
           font=font(SERIF_I, 11), fill=INK, anchor="ma")
    return y + 14


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = draw_kicker(d)
    y = draw_masthead(d, y + 2)
    y = draw_timeline(d, y + 2)
    y = draw_stats(d, y + 2)
    y = draw_regions(d, y + 2)
    y = draw_leads(d, y + 2)
    y = draw_cards(d, y + 2)
    y = draw_bottom(d, y + 2)
    y = draw_datecheck(d, y + 2)
    y = draw_legend_footer(d, y + 2)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes; final y =", y)


if __name__ == "__main__":
    main()
