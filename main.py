#!/usr/bin/env python3
"""World News in One Image - 26 November 2026.

Deterministic infographic generator for the make.fun competition
news-image-20261126. Fixed fonts, fixed geometry, fixed text.
No randomness, no current time, no network access.

Run:  python3 main.py
Output: /output/entry.png  (1200 x 1500)
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
CANVAS_W = 1200
CANVAS_H = 1500

BG_COLOR = (10, 25, 47)          # deep navy background
ACCENT_COLOR = (255, 196, 0)     # bright gold divider / badges
HEADER_TEXT = (255, 255, 255)
SUBTITLE_TEXT = (180, 200, 220)
CARD_COLOR = (255, 255, 255)
CARD_TEXT = (20, 30, 45)
CATEGORY_COLOR = (150, 40, 40)
SOURCE_COLOR = (110, 120, 135)
FOOTER_TEXT = (160, 180, 200)

MARGIN_X = 60
CARD_W = CANVAS_W - 2 * MARGIN_X
HEADER_H = 230            # header block height; first card starts below it
CARD_H = 205              # fixed card height keeps all five cards uniform
CARD_GAP = 22             # vertical gap between cards
CARD_RADIUS = 24
FOOTER_Y = 1435           # footer baseline; five cards end at 230+28+5*205+4*22 = 1371

# ---------------------------------------------------------------------------
# Fonts (system DejaVu, fixed paths)
# ---------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")

DATE_FONT = ImageFont.truetype(FONT_BOLD, 30)
TITLE_FONT = ImageFont.truetype(FONT_BOLD, 62)
SUBTITLE_FONT = ImageFont.truetype(FONT_REGULAR, 30)
CATEGORY_FONT = ImageFont.truetype(FONT_BOLD, 25)
HEADLINE_FONT = ImageFont.truetype(FONT_BOLD, 33)
SOURCE_FONT = ImageFont.truetype(FONT_REGULAR, 23)
BADGE_FONT = ImageFont.truetype(FONT_BOLD, 30)
FOOTER_FONT = ImageFont.truetype(FONT_REGULAR, 22)

# ---------------------------------------------------------------------------
# News of the day: (category, headline, source)
# ---------------------------------------------------------------------------
NEWS = [
    (
        "TRADE",
        "US proposes new tariffs aimed at factory overcapacity",
        "Reuters",
    ),
    (
        "UKRAINE WAR",
        "Ukraine says it struck a major Russian air base, damaging five planes",
        "Reuters",
    ),
    (
        "NORTH KOREA",
        "North Korea's Kim calls for wider use of tactical nuclear weapons",
        "Agence France-Presse",
    ),
    (
        "UNITED STATES",
        "New York postpones Thanksgiving Day parade over major storm",
        "Associated Press",
    ),
    (
        "MUSIC",
        "Duran Duran guitarist and songwriter Andy Taylor dies at 65",
        "Reuters",
    ),
]

OUTPUT_DIR = "/output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def wrap_text(draw, text, font, max_width, max_lines=2):
    """Wrap text into at most max_lines lines fitting max_width.

    Overflowing words on the last line are cut and replaced with an
    ellipsis so the headline never exceeds two lines.
    """
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and current and lines[-1] != current:
        # Trim the last line so the ellipsis fits.
        last = lines[-1]
        while last and draw.textlength(last + "...", font=font) > max_width:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "..."
    return lines


def draw_header(draw):
    """Top header: date, title, subtitle, bright divider line."""
    draw.text(
        (MARGIN_X, 52),
        "26 NOVEMBER 2026",
        font=DATE_FONT,
        fill=ACCENT_COLOR,
    )
    draw.text(
        (MARGIN_X, 92),
        "World News in One Image",
        font=TITLE_FONT,
        fill=HEADER_TEXT,
    )
    draw.text(
        (MARGIN_X, 168),
        "Five stories that defined the day",
        font=SUBTITLE_FONT,
        fill=SUBTITLE_TEXT,
    )
    draw.line(
        [(MARGIN_X, 214), (CANVAS_W - MARGIN_X, 214)],
        fill=ACCENT_COLOR,
        width=4,
    )


def draw_card(draw, index, category, headline, source, top):
    """One white rounded card with badge, category, headline, source."""
    left = MARGIN_X
    right = CANVAS_W - MARGIN_X
    bottom = top + CARD_H
    draw.rounded_rectangle(
        [left, top, right, bottom],
        radius=CARD_RADIUS,
        fill=CARD_COLOR,
    )

    # Number badge: gold circle at the left.
    badge_cx = left + 52
    badge_cy = top + 52
    badge_r = 30
    draw.ellipse(
        [
            badge_cx - badge_r,
            badge_cy - badge_r,
            badge_cx + badge_r,
            badge_cy + badge_r,
        ],
        fill=ACCENT_COLOR,
    )
    number = str(index + 1)
    num_w = draw.textlength(number, font=BADGE_FONT)
    num_h = BADGE_FONT.size
    draw.text(
        (badge_cx - num_w / 2, badge_cy - num_h / 2 - 2),
        number,
        font=BADGE_FONT,
        fill=CARD_TEXT,
    )

    text_x = left + 104
    text_w = right - text_x - 36

    # Category label.
    draw.text(
        (text_x, top + 26),
        category,
        font=CATEGORY_FONT,
        fill=CATEGORY_COLOR,
    )

    # Headline, wrapped to at most two lines.
    lines = wrap_text(draw, headline, HEADLINE_FONT, text_w, max_lines=2)
    line_y = top + 62
    for line in lines:
        draw.text((text_x, line_y), line, font=HEADLINE_FONT, fill=CARD_TEXT)
        line_y += 42

    # Source line pinned near the bottom of the card.
    draw.text(
        (text_x, bottom - 40),
        "Source: " + source,
        font=SOURCE_FONT,
        fill=SOURCE_COLOR,
    )


def draw_footer(draw):
    """Bottom footer with the source credits and date."""
    footer = "Sources: Reuters, Agence France-Presse, Associated Press | 26 Nov 2026"
    text_w = draw.textlength(footer, font=FOOTER_FONT)
    draw.text(
        ((CANVAS_W - text_w) / 2, FOOTER_Y),
        footer,
        font=FOOTER_FONT,
        fill=FOOTER_TEXT,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    image = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(image)

    draw_header(draw)

    top = HEADER_H + 28
    for i, (category, headline, source) in enumerate(NEWS):
        draw_card(draw, i, category, headline, source, top)
        top += CARD_H + CARD_GAP

    draw_footer(draw)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    image.save(OUTPUT_PATH, format="PNG")
    print("Saved {} ({}x{})".format(OUTPUT_PATH, CANVAS_W, CANVAS_H))


if __name__ == "__main__":
    main()
