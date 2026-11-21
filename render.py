#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261121 entry.

Draws entry.png (1024x1024): one clean, professional newspaper page summing
up Saturday 21 November 2026, with a real photo thumbnail above each of the
three lead stories (thumbs/*.jpg, Wikimedia Commons photographs prepared by
tools/prep_thumbs.py). Build-time only: the graded program (main.py) just
copies the finished entry.png. Pillow is used here, at build time; main.py
is pure stdlib. No network, no randomness: same input, same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28                       # page margin
CW = W - 2 * M               # 968 content width
PAPER = (253, 253, 248)
INK = (26, 26, 26)
GREY = (110, 110, 105)
RED = (185, 28, 28)
NAVY = (22, 38, 63)
LAND = (64, 98, 138)         # continent fill on the dark map
LAND2 = (38, 62, 92)         # second continent shade
RULE = (165, 165, 155)
LIGHT = (238, 238, 232)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
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


# ---------------------------------------------------------------- data
# 36 stories, all verified against reporting of 21 November 2026.
# 3 leads + 10 cards + 23 in the ALSO list. Region counts sum to 36.

STATS = [
    ("DAY 13", "of COP31 in Antalya"),
    ("5", "missiles downed"),
    ("6.7", "Peru quake magnitude"),
    ("146", "safe in Davao"),
    ("$58,136", "Bitcoin, Sat morning"),
    ("124*", "Rahul, Wellington"),
]

REGIONS = [("EUROPE", 6), ("ASIA", 6), ("MIDDLE EAST", 6), ("AFRICA", 1),
           ("AMERICAS", 9), ("OCEANIA", 7), ("GLOBAL", 1)]

LEADS = [
    {"kicker": "COP31 OVERTIME",
     "head": "Antalya talks slip into overtime with no deal",
     "body": "Third draft due Saturday morning. Text cut from 144 to 80 paragraphs, "
             "no mention of coal, oil or gas; the $120bn adaptation target is dropped. "
             "\u201cWe are close to the finish line but not there yet,\u201d says chair Kurum. "
             "Panama threatens to object; next summit: Addis Ababa, Nov 2027."},
    {"kicker": "SAUDI: MISSILES",
     "head": "Three Houthi missiles downed over Riyadh",
     "body": "Intercepted early Saturday, ~02:00 local, after a 01:53 alert; two more "
             "over Jazan on Friday. Third straight day of alerts; Thursday\u2019s strike "
             "damaged the PIF Tower. The coalition hit Hodeidah and Sanaa on Friday."},
    {"kicker": "PERU: QUAKE 6.7",
     "head": "M6.7 quake shakes Peru, felt in Lima",
     "body": "19:09 local Friday, 30 km NW of Jun\u00edn, 108 km deep. No deaths; ~34 houses "
             "damaged, rockfalls on the Carretera Central, power out in Pichanaqui and "
             "Satipo. Felt across Lima; residents took to the streets. No tsunami threat."},
]

CARDS = [
    ("KYIV", "Zelensky: the Crimea Bridge \u201cwill not stay\u201d",
     "Tells NBC Russia is stepping up double-tap strikes on cities."),
    ("HORMUZ", "Iran says it shot down a US drone",
     "Tehran claims its 58th MQ-9 over the strait; no US confirmation."),
    ("WASHINGTON", "Trump vows a \u201ctremendous tax\u201d abroad",
     "No rate, no details \u2014 and he had not told his own staff first."),
    ("CHINA\u2013JAPAN", "Beijing: Tokyo must \u201ccorrect\u201d its Taiwan words",
     "Xi snubbed Takaichi at APEC; she insists policy is unchanged."),
    ("DAVAO", "146 safe after jet\u2019s emergency landing",
     "767 diverted on an engine warning; all 146 out via slides."),
    ("BITCOIN", "Bitcoin dives to $55,130, then recovers",
     "Lowest since Sep 2024; fear at 12; liquidations near $2.4bn."),
    ("LAS VEGAS", "Russell fastest in final Vegas practice",
     "Mercedes 1\u20132; late clash with Verstappen goes to the stewards."),
    ("WELLINGTON", "Rahul 124* makes history",
     "First Indian opener with Test 100s in all four SENA countries."),
    ("CANBERRA", "Australia\u2013China agree AI talks",
     "Xi hails a \u201cturnaround\u201d; a new AI dialogue is agreed."),
    ("WHITE HOUSE", "Vance won\u2019t say he\u2019d order Iran strikes",
     "Sidesteps Trump; blames the Iran war for midterm losses."),
]

# Bullets, not numbers (the ALSO list is a round-up, the map carries numbers).
ALSO = [
    ("Copenhagen", "Denmark expels Russian attach\u00e9 over \u2018rapper plot\u2019"),
    ("Panama", "Panama threatens to block the COP31 deal"),
    ("Yemen", "Houthis threaten Jeddah and Red Sea ports"),
    ("SpaceX", "SPCX near $137, a $1.89T market cap"),
    ("Texas", "63-minute execution; staff hunted for a vein (Thu)"),
    ("LA", "Jury convicts the man who started the Palisades fire; 12 dead"),
    ("Crimea Bridge", "rail section hit 19 Nov; repairs may take 3 years"),
    ("Beijing", "2027 named the Year of Tourism with Canberra"),
    ("Sejong", "freight train derails, 5 of 21 cars; line halted"),
    ("IAEA", "440.9 kg of Iran\u2019s 60% uranium still unverified"),
    ("Cummins", "Cricket Australia backs its captain"),
    ("Thailand", "rivers at 28\u00d7 the arsenic limit; protest Sun"),
    ("India", "Cyclone Akvan\u2019s remnants bring heavy rain"),
    ("Antalya", "EU warns the COP31 deal is drifting"),
    ("Hodeidah", "coalition hits Hodeidah and Sanaa after alerts"),
    ("Riyadh", "Thursday\u2019s strike damaged the PIF Tower"),
    ("Shenzhen", "APEC leaders wrap up their summit"),
    ("Addis Ababa", "next climate summit goes there, Nov 2027"),
    ("Kryvyi Rih", "missile kills a boy, 7, and a paramedic, 20"),
    ("Washington", "Trump praises Rubio, hints at a 2028 run"),
    ("Lyon", "a doubt for Boxing Day with a hamstring injury"),
    ("T20", "England open their series in Melbourne on Saturday"),
    ("Marsh", "ducks media duties as \u2018Sandpapergate\u2019 pressure builds"),
]

# Map pins: (lon, lat) for the 13 lead+card stories. 9 (Bitcoin) has no pin.
PINS = [
    (30.7, 36.9),    # 1 Antalya
    (46.7, 24.7),    # 2 Riyadh
    (-75.2, -11.2),  # 3 Junin, Peru
    (30.5, 50.5),    # 4 Kyiv
    (56.5, 26.6),    # 5 Strait of Hormuz
    (-77.0, 38.9),   # 6 Washington
    (139.7, 35.7),   # 7 Tokyo
    (125.6, 7.1),    # 8 Davao
    None,             # 9 Bitcoin - global markets, no pin
    (-115.1, 36.2),  # 10 Las Vegas
    (174.8, -41.3),  # 11 Wellington
    (116.4, 39.9),   # 12 Beijing
    (-79.5, 38.9),   # 13 White House (nudged so it does not sit on 6)
]

MAP_KEY = [
    "1 ANTALYA \u00b7 COP31 overtime",
    "2 RIYADH \u00b7 Missiles downed",
    "3 JUN\u00cdN \u00b7 Quake 6.7",
    "4 KYIV \u00b7 Crimea Bridge warning",
    "5 HORMUZ \u00b7 US drone claim",
    "6 WASHINGTON \u00b7 Trump AI tax",
    "7 TOKYO \u00b7 China\u2013Japan words",
    "8 DAVAO \u00b7 146 safe",
    "9 BITCOIN \u00b7 Global markets",
    "10 LAS VEGAS \u00b7 Russell P1",
    "11 WELLINGTON \u00b7 Rahul 124*",
    "12 BEIJING \u00b7 Australia\u2013China AI talks",
    "13 WHITE HOUSE \u00b7 Vance on Iran",
]

# Simplified continent outlines, hand-drawn (lon, lat). Recognisable, not precise.
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


# Lead thumbnails: real photographs (Wikimedia Commons, freely licensed).
# Resized from the verified downloads by tools/prep_thumbs.py into
# thumbs/*.jpg (314x88, JPEG q82). One thumb per lead column, directly above
# its headline; the caption names the place (and date for Riyadh), so no
# photo is ever presented as the event itself.
THUMBS = [
    ("thumbs/antalya.jpg", "Antalya coast"),
    ("thumbs/riyadh.jpg", "Kingdom Centre, Riyadh (Oct 2024)"),
    ("thumbs/junin.jpg", "Lake Junín, Peru"),
]
THUMB_H = 88


# ---------------------------------------------------------------- sections
def draw_masthead(d):
    y = 18
    d.text((W // 2, y), "ONE DAY", font=font(SERIF_B, 46), fill=INK, anchor="ma")
    y += 54
    d.text((W // 2, y), "THE WORLD\u2019S NEWS IN ONE IMAGE",
           font=font(SANS_B, 12), fill=GREY, anchor="ma")
    y += 20
    d.text((W // 2, y), "Saturday 21 November 2026",
           font=font(SERIF_B, 34), fill=INK, anchor="ma")
    y += 44
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    return y + 8


def draw_stats(d, y):
    n = len(STATS)
    gap = 8
    bw = (CW - gap * (n - 1)) // n
    f_num = font(SERIF_B, 26)
    f_lab = font(SANS, 10)
    for i, (num, lab) in enumerate(STATS):
        x0 = M + i * (bw + gap)
        d.rectangle([x0, y, x0 + bw, y + 40], outline=RULE, width=1)
        d.text((x0 + bw // 2, y + 2), num, font=f_num, fill=INK, anchor="ma")
        d.text((x0 + bw // 2, y + 28), lab, font=f_lab, fill=GREY, anchor="ma")
    return y + 44


def draw_regions(d, y):
    parts = []
    for name, cnt in REGIONS:
        parts.append("%s %d" % (name, cnt))
    line = "  \u00b7  ".join(parts) + "  =  36 STORIES"
    f = font(SANS_B, 12)
    d.text((W // 2, y), line, font=f, fill=INK, anchor="ma")
    d.line([(M, y + 16), (W - M, y + 16)], fill=RULE, width=1)
    return y + 22


def draw_thumbs(img, d, y):
    """One real photo per lead column, directly above its headline."""
    col_w = (CW - 2 * 12) // 3
    f_cap = font(SANS, 11)
    base = os.path.dirname(os.path.abspath(__file__))
    for i, (path, cap) in enumerate(THUMBS):
        x = M + i * (col_w + 12)
        th = Image.open(os.path.join(base, path)).convert("RGB")
        img.paste(th, (x, y))
        d.rectangle([x, y, x + col_w - 1, y + THUMB_H - 1],
                    outline=RULE, width=1)
        d.text((x, y + THUMB_H + 3), cap, font=f_cap, fill=GREY)
    return y + THUMB_H + 3 + 12 + 4


def draw_leads(d, y):
    col_w = (CW - 2 * 12) // 3
    f_kick = font(SANS_B, 13)
    f_head = font(SERIF_B, 21)
    f_body = font(SERIF, 13)
    top = y
    bottom = top
    for i, lead in enumerate(LEADS):
        x = M + i * (col_w + 12)
        yy = top
        d.text((x, yy), lead["kicker"], font=f_kick, fill=RED)
        yy += 20
        yy = block(d, x, yy, wrap(d, lead["head"], f_head, col_w),
                   f_head, leading=23)
        yy += 4
        yy = block(d, x, yy, wrap(d, lead["body"], f_body, col_w),
                   f_body, leading=16)
        bottom = max(bottom, yy)
    for i in range(2):
        x = M + (i + 1) * col_w + i * 12 + 6
        d.line([(x, top), (x, bottom)], fill=RULE, width=1)
    return bottom + 6


def draw_cards(d, y):
    cols, rows = 5, 2
    gap_x, gap_y = 8, 6
    cw = (CW - gap_x * (cols - 1)) // cols
    rh = 80
    f_lab = font(SANS_B, 11)
    f_head = font(SERIF_B, 14)
    f_body = font(SERIF, 11)
    for i, (lab, head, body) in enumerate(CARDS):
        r, c = divmod(i, cols)
        x = M + c * (cw + gap_x)
        yy = y + r * (rh + gap_y)
        d.line([(x, yy - 3), (x + cw, yy - 3)], fill=RULE, width=1)
        d.text((x, yy), lab, font=f_lab, fill=RED)
        yy += 16
        yy = block(d, x, yy, wrap(d, head, f_head, cw), f_head, leading=16)
        yy += 2
        block(d, x, yy, wrap(d, body, f_body, cw), f_body, leading=13)
    return y + rows * rh + gap_y


def draw_map(d, y):
    map_w, map_h = 640, 144
    key_x = M + map_w + 14
    d.rectangle([M, y, M + map_w, y + map_h], fill=NAVY)
    for lon in range(-180, 181, 30):
        x = M + (lon + 168) / 360.0 * map_w
        d.line([(x, y), (x, y + map_h)], fill=(35, 55, 85), width=1)
    for lat in range(-60, 91, 30):
        yy = y + (83 - lat) / 138.0 * map_h
        d.line([(M, yy), (M + map_w, yy)], fill=(35, 55, 85), width=1)

    def proj(lon, lat):
        return (M + (lon + 168) / 360.0 * map_w,
                y + (83 - lat) / 138.0 * map_h)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    f_pin = font(SANS_B, 10)
    for i, pin in enumerate(PINS):
        if pin is None:
            continue
        x, yy = proj(*pin)
        if i == 12:
            # 13 (White House) shares Washington with 6: call it out.
            tx, ty = x + 18, yy - 14
            d.line([(x, yy), (tx, ty)], fill=WHITE, width=1)
            x, yy = tx, ty
        r = 9
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=WHITE,
                  outline=RED, width=2)
        d.text((x, yy), str(i + 1), font=f_pin, fill=RED, anchor="mm")
    f_key = font(SANS, 10)
    f_keyb = font(SANS_B, 10)
    yy = y + 2
    d.text((key_x, yy), "ON THE MAP", font=f_keyb, fill=RED)
    yy += 14
    for line in MAP_KEY:
        num, rest = line.split(" ", 1)
        d.text((key_x, yy), num, font=f_keyb, fill=RED)
        d.text((key_x + 22, yy), rest, font=f_key, fill=INK)
        yy += 10
    key_bottom = yy - 10 + 10  # top of last line + its text height
    return max(y + map_h + 6, key_bottom + 4)


def draw_also(d, y):
    f_place = font(SANS_B, 11)
    f_text = font(SANS, 11)
    col_w = (CW - 16) // 2
    left, right = ALSO[:12], ALSO[12:]
    for ci, col in enumerate((left, right)):
        x = M + ci * (col_w + 16)
        yy = y
        for place, text in col:
            d.text((x, yy), "\u2022", font=f_text, fill=RED)
            d.text((x + 12, yy), place, font=f_place, fill=INK)
            pw = d.textlength(place, font=f_place)
            d.text((x + 12 + pw + 4, yy), "\u2014 " + text,
                   font=f_text, fill=INK)
            yy += 13
    return y + 12 * 13


def draw_datecheck(d, y):
    d.rectangle([M, y, W - M, y + 36], fill=NAVY)
    f = font(SANS, 11)
    fb = font(SANS_B, 11)
    gold = (255, 210, 63)
    d.text((M + 10, y + 4), "DATE CHECK \u2014 ", font=fb, fill=gold)
    w0 = d.textlength("DATE CHECK \u2014 ", font=fb)
    d.text((M + 10 + w0, y + 4),
           "Broke Fri, reported Sat: Trump AI tax \u00b7 China\u2013Japan words \u00b7 "
           "Vance on Iran \u00b7 Copenhagen expulsion \u00b7 Palisades verdict \u00b7 Vegas FP3.",
           font=f, fill=WHITE)
    d.text((M + 10, y + 20),
           "Left out: Wall Street\u2019s tech rout (Fri, Nasdaq \u22125.3%). Unconfirmed: "
           "the final COP31 text. Every story here happened, or was first reported, "
           "on Sat 21 Nov 2026.",
           font=f, fill=WHITE)
    return y + 36


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = draw_masthead(d)
    y = draw_stats(d, y + 3)
    y = draw_regions(d, y + 3)
    y = draw_thumbs(img, d, y + 3)
    y = draw_leads(d, y + 3)
    y = draw_cards(d, y + 3)
    y = draw_map(d, y + 3)
    y = draw_also(d, y + 3)
    y = draw_datecheck(d, y + 3)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes; final y =", y)


if __name__ == "__main__":
    main()
