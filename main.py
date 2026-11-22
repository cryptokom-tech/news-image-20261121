#!/usr/bin/env python3
"""news-image-20261121 — full-day front page, rebuilt from scratch.

One 1024x1024 PNG: masthead + dotted world map with numbered pins +
3 columns of 36 numbered stories + markets footer. PIL only, no network.
Deterministic: fixed seed, sorted iteration, no timestamps.
"""
import hashlib
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 28
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
SEED = 20261121
MIN_PIN_GAP = 18

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

# Colours
INK = (18, 18, 18)
PAPER = (252, 250, 244)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
GREY = (110, 110, 110)
LIGHTGREY = (200, 200, 200)
MAPDOT = (150, 165, 180)
RULE = (60, 60, 60)

# (number, headline, detail, lat, lon) — lat/lon None means no map pin.
STORIES = [
    (1, "IRAN STRIKES US BASES IN BAHRAIN",
     "Tehran says it hit two US positions; Bahrain reports a fire at an industrial site, no injuries.",
     26.23, 50.59),
    (2, "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
     "FBI top-10 fugitive Fausto Isidro Meza Flores seized in Guasave; at least 11 dead in the violence.",
     25.57, -108.47),
    (3, "WALL ST SLIDES INTO CORRECTION",
     "S&P 500 -3.7%, Nasdaq -5.3% erases its 2026 gains as the AI sell-off spreads; worst week since 2020.",
     40.71, -74.00),
    (4, "RIEMANN 'PROVED' WITH AI",
     "Anthropic mathematician Levent Alpoege says Claude helped prove the 160-year-old hypothesis in six weeks.",
     37.77, -122.42),
    (5, "KRYVYI RIH HIT OVERNIGHT",
     "Russian missile kills 2 and wounds 60, among them a 7-year-old boy; a strike on Lviv kills 2.",
     48.02, 33.42),
    (6, "DRONES HIT RUSSIAN SHIP OFF FINLAND",
     "Sanctioned cargo ship Sparta II ablaze, drifts into Finnish waters; Finland says Ukraine likely behind it.",
     59.90, 25.00),
    (7, "FBI CRIME DATABASE HACKED",
     "National Crime Information Center breached, the second FBI hack in months; Trump calls it 'not good'.",
     38.90, -77.04),
    (8, "COP31 IN OVERTIME, NO DEAL",
     "Talks pass the deadline with no deal; draft drops fossil fuels and the $120bn adaptation figure.",
     36.90, 30.71),
    (9, "TRUMP DEFENDS PUTIN TIES",
     "After the Shenzhen summit with Xi, Trump defends calling Putin 'my friend'; leaders agree nuclear talks.",
     22.54, 114.06),
    (10, "ISRAELI STRIKE KILLS THREE IN GAZA",
     "Air strike hits a food vehicle in Gaza City's Tel al-Hawa; Israel says the dead were Islamic Jihad.",
     31.50, 34.47),
    (11, "HOUTHIS & SAUDI TRADE STRIKES",
     "Coalition carries out 71 strikes in 24 hours; Houthi missiles intercepted over Riyadh.",
     14.80, 42.95),
    (12, "DENMARK EXPELS RUSSIAN DIPLOMAT",
     "Defence attache expelled over the alleged plot to kill US-Ukrainian rapper Kyivstoner.",
     55.68, 12.57),
    (13, "TRUMP: TAX ON DATA CENTRES ABROAD",
     "President threatens a 'tremendous tax' on US tech firms building AI centres overseas.",
     38.90, -77.04),
    (14, "NVIDIA CHIEF OUSTED",
     "Jensen Huang out amid an SEC probe, Trump says he discussed it with Xi; chip export rules unchanged.",
     37.35, -121.96),
    (15, "BITCOIN BACK ABOVE $60,000",
     "Touched $55,326, a two-year low, then rose 9%; crypto liquidations top $2bn.",
     None, None),
    (16, "EU-INDONESIA SIGN TRADE DEAL",
     "Removes 98.5% of tariffs on EU goods; covers about 730 million people.",
     50.85, 4.35),
    (17, "PAKISTAN CLINCH TEST SERIES",
     "Beat Sri Lanka by eight wickets in Rawalpindi for a first series win in two years.",
     33.60, 73.05),
    (18, "EU PAYS UKRAINE NEARLY €8BN",
     "Largest-ever reforms disbursement to Kyiv.",
     50.85, 4.35),
    (19, "US APPROVED 900K AI CHIPS FOR CHINA",
     "House committee says the approvals came in six months.",
     38.90, -77.04),
    (20, "JAPAN TROOPS TO TRAIN IN INDIA",
     "First live-fire drills on Indian soil: anti-ship missiles and small attack drones.",
     28.61, 77.21),
    (21, "NSE NOW WORLD'S 5TH EXCHANGE",
     "Overtakes Nasdaq and HKEX; market cap $59.65bn.",
     19.08, 72.88),
    (22, "UN AGREES KILLER-ROBOT TEXT",
     "Geneva talks agree a non-binding text on autonomous weapons; binding rules still out of reach.",
     46.20, 6.14),
    (23, "INDONESIA FIRES MAY COST $30BN",
     "Copernicus: fire emissions third highest on record.",
     -6.21, 106.85),
    (24, "BRAZIL SHIELDS INDIGENOUS LAND",
     "Lula acts with Kayapo leader Raoni to protect native territory.",
     -15.79, -47.88),
    (25, "BANKS HIT IN EXTORTION HACK",
     "JPMorgan, Visa and Mastercard breached via third-party vendors in the n0n extortion attack.",
     40.71, -74.00),
    (26, "BOLSONARO IN INTENSIVE CARE",
     "Ex-president stable with a bowel obstruction; doctors weigh surgery.",
     -15.79, -47.88),
    (27, "MAGNITUDE 6.9 QUAKE SHAKES PERU",
     "Strong quake hits the Peruvian Andes; no major damage reported.",
     -10.50, -76.00),
    (28, "DENGUE BREAKTHROUGH IN BRAZIL",
     "Wolbachia mosquitoes cut dengue cases 69% among children.",
     -22.91, -43.17),
    (29, "BEPICOLOMBO REACHES MERCURY",
     "ESA-JAXA craft enters orbit after an eight-year, 10-billion-km journey.",
     49.87, 8.65),
    (30, "HARDEN PASSES KOBE",
     "51 points as Cleveland beat Indiana 128-119; his 26th 50-point game, third all-time.",
     41.50, -81.69),
    (31, "VERSTAPPEN ON POLE IN LAS VEGAS",
     "Antonelli fastest in qualifying but penalised.",
     36.17, -115.14),
    (32, "ENGLAND BEAT ALL BLACKS 37-12",
     "Record winning margin over New Zealand at Twickenham.",
     51.51, -0.13),
    (33, "ALCARAZ INTO ATP FINALS FINAL",
     "Beats Shelton in three sets; faces world No. 1 Zverev on Sunday.",
     45.07, 7.69),
    (34, "HARRY KANE OUT FOR MONTHS",
     "Ankle ligament torn in Bayern's 1-1 draw with Cologne.",
     48.14, 11.58),
    (35, "TANKERS HIT IN STRAIT OF HORMUZ",
     "Two tankers struck by projectiles as Gulf tensions rise; UKMTO reports crews safe.",
     26.50, 56.30),
    (36, "COST-OF-LIVING PROTESTS IN EUROPE",
     "Thousands march in France, sixth Saturday, 144 arrests; students march in Berlin.",
     48.86, 2.35),
]

MARKETS = ("S&P 500 -3.7%  |  Nasdaq -5.3%  |  Nikkei -5.06%  |  Sensex +2.3%  |  "
           "Gold -4.6%  |  Brent ~$90  |  Bitcoin back above $60,000")

# Coarse land mask: row -> list of (col_start, col_end) inclusive.
# Grid is 72 cols (5 deg lon each, -180..180) x 30 rows (lat 75..-55).
# Hand-drawn approximation of the continents, good enough for a dotted map.
LAND_ROWS = {
    0: [(4, 9), (45, 70)],
    1: [(2, 22), (25, 29), (38, 70)],
    2: [(2, 21), (26, 30), (35, 71)],
    3: [(3, 20), (27, 29), (34, 34), (37, 42), (44, 71)],
    4: [(4, 19), (34, 35), (37, 44), (46, 70)],
    5: [(5, 20), (35, 44), (45, 69)],
    6: [(6, 21), (35, 43), (46, 68)],
    7: [(7, 21), (36, 43), (47, 66), (66, 67)],
    8: [(8, 21), (36, 42), (48, 65), (65, 66)],
    9: [(9, 21), (34, 42), (44, 64)],
    10: [(10, 18), (34, 45), (46, 63)],
    11: [(12, 17), (33, 46), (48, 62)],
    12: [(14, 17), (34, 46), (50, 61)],
    13: [(15, 17), (35, 46), (51, 60)],
    14: [(20, 24), (36, 45), (52, 59)],
    15: [(20, 25), (37, 44), (55, 62)],
    16: [(20, 26), (38, 43), (56, 63)],
    17: [(20, 26), (38, 43), (57, 64)],
    18: [(21, 26), (38, 42), (58, 63)],
    19: [(21, 26), (39, 42), (59, 62)],
    20: [(21, 26), (39, 41), (59, 65)],
    21: [(22, 26), (39, 41), (58, 66)],
    22: [(22, 26), (39, 41), (58, 66)],
    23: [(22, 25), (39, 40), (59, 65)],
    24: [(22, 25), (39, 40), (60, 64)],
    25: [(23, 24), (61, 64), (69, 70)],
    26: [(23, 24), (69, 70)],
    27: [(23, 24)],
    28: [(23, 24)],
    29: [(23, 23)],
}

# --- layout geometry -------------------------------------------------------
MASTHEAD_Y = 16
NAME_SIZE = 40
DATE_BAR_Y = 96
DATE_BAR_H = 28
MAP_X0, MAP_Y0 = MARGIN, 134
MAP_W, MAP_H = W - 2 * MARGIN, 262
SECTION_Y = 408
COL_Y0 = 434
FOOTER_Y = 962
COL_GAP = 18
COL_W = (W - 2 * MARGIN - 2 * COL_GAP) // 3
COL_X = [MARGIN + i * (COL_W + COL_GAP) for i in range(3)]

LAT_TOP, LAT_BOT = 75.0, -55.0


def project(lat, lon):
    """Equirectangular projection into the map rectangle."""
    x = MAP_X0 + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * MAP_H
    return x, y


def place_pins():
    """Deterministic pin positions with jitter + repulsion (>= MIN_PIN_GAP)."""
    rng = random.Random(SEED)
    pts = {}
    for num, _h, _d, lat, lon in STORIES:
        if lat is None:
            continue
        x, y = project(lat, lon)
        x += rng.uniform(-6, 6)
        y += rng.uniform(-6, 6)
        pts[num] = [x, y]
    order = sorted(pts)
    for _ in range(600):
        moved = False
        for i in range(len(order)):
            for j in range(i + 1, len(order)):
                a, b = pts[order[i]], pts[order[j]]
                dx, dy = b[0] - a[0], b[1] - a[1]
                dist = math.hypot(dx, dy)
                if dist < MIN_PIN_GAP and dist > 0.001:
                    push = (MIN_PIN_GAP - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    a[0] -= ux * push
                    a[1] -= uy * push
                    b[0] += ux * push
                    b[1] += uy * push
                    moved = True
                elif dist <= 0.001:
                    a[0] -= MIN_PIN_GAP / 2.0
                    b[0] += MIN_PIN_GAP / 2.0
                    moved = True
        # clamp inside the map
        for p in pts.values():
            p[0] = min(max(p[0], MAP_X0 + 11), MAP_X0 + MAP_W - 11)
            p[1] = min(max(p[1], MAP_Y0 + 11), MAP_Y0 + MAP_H - 11)
        if not moved:
            break
    return pts


def min_pin_gap(pts):
    order = sorted(pts)
    worst = 1e9
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            d = math.hypot(pts[order[i]][0] - pts[order[j]][0],
                           pts[order[i]][1] - pts[order[j]][1])
            worst = min(worst, d)
    return worst


def wrap(text, font, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_h(lines, leading):
    return len(lines) * leading


def draw_frontpage():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_name = ImageFont.truetype(SERIF_B, NAME_SIZE)
    f_date = ImageFont.truetype(SANS_B, 15)
    f_section = ImageFont.truetype(SANS_B, 13)
    f_head = ImageFont.truetype(SANS_B, 13)
    f_det = ImageFont.truetype(SANS, 11)
    f_pin = ImageFont.truetype(SANS_B, 10)
    f_foot = ImageFont.truetype(SANS, 11)
    f_foot_b = ImageFont.truetype(SANS_B, 11)

    # --- masthead ---
    name = "THE WORLD IN ONE PAGE"
    tw = d.textlength(name, font=f_name)
    d.text(((W - tw) / 2, MASTHEAD_Y), name, font=f_name, fill=INK)
    # thin rules under the name
    d.line([(MARGIN, 66), (W - MARGIN, 66)], fill=INK, width=2)
    d.line([(MARGIN, 70), (W - MARGIN, 70)], fill=INK, width=1)
    tagline = "Thirty-six stories from every corner of the planet  •  One image"
    tw = d.textlength(tagline, font=f_foot)
    d.text(((W - tw) / 2, 76), tagline, font=f_foot, fill=GREY)

    # --- red date banner ---
    d.rectangle([MARGIN, DATE_BAR_Y, W - MARGIN, DATE_BAR_Y + DATE_BAR_H],
                fill=RED)
    date_txt = "SATURDAY, 21 NOVEMBER 2026"
    tw = d.textlength(date_txt, font=f_date)
    d.text(((W - tw) / 2, DATE_BAR_Y + 6), date_txt, font=f_date,
           fill=(255, 255, 255))

    # --- dotted world map ---
    cell_w = MAP_W / 72.0
    cell_h = MAP_H / 30.0
    for row in sorted(LAND_ROWS):
        for c0, c1 in LAND_ROWS[row]:
            for c in range(c0, c1 + 1):
                cx = MAP_X0 + (c + 0.5) * cell_w
                cy = MAP_Y0 + (row + 0.5) * cell_h
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=MAPDOT)

    pins = place_pins()
    for num in sorted(pins):
        x, y = pins[num]
        r = 10
        d.ellipse([x - r, y - r, x + r, y + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        lw = d.textlength(label, font=f_pin)
        d.text((x - lw / 2, y - 7), label, font=f_pin, fill=(255, 255, 255))

    # --- section header ---
    d.line([(MARGIN, SECTION_Y), (W - MARGIN, SECTION_Y)], fill=RULE, width=2)
    sec = "THE DAY IN 36 STORIES"
    d.text((MARGIN, SECTION_Y + 6), sec, font=f_section, fill=INK)
    sec_r = "Numbers on the map match the stories below"
    tw = d.textlength(sec_r, font=f_foot)
    d.text((W - MARGIN - tw, SECTION_Y + 7), sec_r, font=f_foot, fill=GREY)

    # --- story columns ---
    col_bottoms = []
    for ci in range(3):
        x = COL_X[ci]
        y = COL_Y0
        for num, headline, detail, _lat, _lon in STORIES[ci::3]:
            head_lines = wrap(f"{num}. {headline}", f_head, COL_W)
            det_lines = wrap(detail, f_det, COL_W)
            for k, line in enumerate(head_lines):
                d.text((x, y), line, font=f_head,
                       fill=RED if k == 0 else INK)
                y += 15
            for line in det_lines:
                d.text((x, y), line, font=f_det, fill=INK)
                y += 12
            y += 3  # gap between stories
        col_bottoms.append(y - 5)

    # --- footer ---
    d.line([(MARGIN, FOOTER_Y), (W - MARGIN, FOOTER_Y)], fill=RULE, width=2)
    d.text((MARGIN, FOOTER_Y + 8), "MARKETS", font=f_foot_b, fill=RED)
    d.text((MARGIN + 66, FOOTER_Y + 8), MARKETS, font=f_foot, fill=INK)
    credit = ("Sources: AP, Reuters, BBC, CNN, Al Jazeera, The Guardian, "
              "France 24, Xinhua  •  Generated 21 November 2026")
    tw = d.textlength(credit, font=f_foot)
    d.text((W - MARGIN - tw, FOOTER_Y + 30), credit, font=f_foot, fill=GREY)
    d.text((MARGIN, FOOTER_Y + 30), "THE WORLD IN ONE PAGE — 21 NOV 2026",
           font=f_foot_b, fill=INK)

    return img, pins, col_bottoms


def main():
    img, pins, col_bottoms = draw_frontpage()

    # --- self-checks ---
    gap = min_pin_gap(pins)
    assert gap >= MIN_PIN_GAP - 0.01, f"pin collision: min gap {gap:.1f}px"
    for i, bottom in enumerate(col_bottoms):
        assert bottom <= FOOTER_Y - 4, \
            f"column {i} overflows footer: bottom {bottom} > {FOOTER_Y - 4}"
    assert len(STORIES) == 36, "need exactly 36 stories"
    assert len(pins) == 35, f"expected 35 pins, got {len(pins)}"

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "entry.png")
    img.save(path, format="PNG", optimize=True)
    size = os.path.getsize(path)
    assert img.size == (1024, 1024), f"bad size {img.size}"
    assert size < 1024 * 1024, f"entry.png too big: {size} bytes"
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print(f"OK {path} {size} bytes sha256={digest}")
    print(f"pins={len(pins)} min_pin_gap={gap:.1f}px "
          f"col_bottoms={col_bottoms} footer_y={FOOTER_Y}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
