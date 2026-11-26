"""news-image-20261126 -- World News in One Image (2026-11-26).

Deterministic rendering: fixed fonts, fixed geometry, fixed text.
No randomness, no current time, no network.
Running `python3 main.py` writes /output/entry.png.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 1500
OUTPUT_DIR = "/output"
OUTPUT_PATH = "/output/entry.png"

# Colours.
BG_COLOR = (11, 30, 63)            # deep navy canvas
ACCENT_COLOR = (255, 183, 3)       # bright amber divider / badge accent
HEADER_TEXT = (255, 255, 255)      # white header text
HEADER_MUTED = (178, 198, 220)     # muted header text
CARD_COLOR = (255, 255, 255)       # white news cards
TITLE_COLOR = (18, 28, 48)         # dark navy card titles
CATEGORY_COLOR = (30, 90, 180)     # blue category labels
SOURCE_COLOR = (100, 110, 125)     # grey source lines
FOOTER_COLOR = (178, 198, 220)     # muted footer text

# Font files (system DejaVu, always present on this machine).
# Bold is used for date/title/category/headline/badge; regular for
# subtitle/source/footer. Paths are fixed so rendering is deterministic.
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Layout. Five cards stack from CARDS_TOP: 240 + 5*200 + 4*18 = 1312,
# leaving the footer at 1360 and a 140 px bottom margin inside 1500.
MARGIN = 60
HEADER_DATE_Y = 48
HEADER_TITLE_Y = 92
HEADER_SUBTITLE_Y = 152
DIVIDER_Y = 208
DIVIDER_HEIGHT = 4
CARDS_TOP = 240
CARD_HEIGHT = 200
CARD_GAP = 18
CARD_RADIUS = 20
BADGE_DIAMETER = 56
TEXT_X = 170
FOOTER_Y = 1360

# ------------------------------------------------------------- news content
# Each item: (category, headline, source).
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

FOOTER_TEXT = "Sources: Reuters, Agence France-Presse, Associated Press | 26 Nov 2026"


def load_fonts():
    """Load the fixed DejaVu fonts at fixed sizes."""
    return {
        "date": ImageFont.truetype(FONT_BOLD, 28),
        "title": ImageFont.truetype(FONT_BOLD, 46),
        "subtitle": ImageFont.truetype(FONT_REGULAR, 26),
        "category": ImageFont.truetype(FONT_BOLD, 22),
        "headline": ImageFont.truetype(FONT_BOLD, 32),
        "source": ImageFont.truetype(FONT_REGULAR, 22),
        "badge": ImageFont.truetype(FONT_BOLD, 26),
        "footer": ImageFont.truetype(FONT_REGULAR, 20),
    }


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap: split `text` into lines no wider than `max_width`.

    Returns a list of lines. Measured with the same font that will draw
    them, so wrapping is exact and deterministic.
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
    if current:
        lines.append(current)
    return lines


def fit_two_lines(draw, text, font, max_width):
    """Wrap `text` to at most two lines, truncating with an ellipsis."""
    lines = wrap_text(draw, text, font, max_width)
    if len(lines) <= 2:
        return lines
    lines = lines[:2]
    # Trim the second line word by word until it fits with "..." appended.
    while lines[1] and draw.textlength(lines[1] + "...", font=font) > max_width:
        words = lines[1].split()
        if len(words) <= 1:
            break
        lines[1] = " ".join(words[:-1])
    lines[1] = lines[1] + "..."
    return lines


def draw_header(draw, fonts):
    """Top header: date, title, subtitle, bright divider line."""
    draw.text(
        (MARGIN, HEADER_DATE_Y),
        "26 NOVEMBER 2026",
        font=fonts["date"],
        fill=ACCENT_COLOR,
    )
    draw.text(
        (MARGIN, HEADER_TITLE_Y),
        "World News in One Image",
        font=fonts["title"],
        fill=HEADER_TEXT,
    )
    draw.text(
        (MARGIN, HEADER_SUBTITLE_Y),
        "Five stories that defined the day",
        font=fonts["subtitle"],
        fill=HEADER_MUTED,
    )
    draw.rectangle(
        [MARGIN, DIVIDER_Y, CANVAS_WIDTH - MARGIN, DIVIDER_Y + DIVIDER_HEIGHT],
        fill=ACCENT_COLOR,
    )


def draw_card(draw, fonts, index, item, y):
    """One white rounded news card at vertical offset `y`."""
    category, headline, source = item
    x0 = MARGIN
    x1 = CANVAS_WIDTH - MARGIN
    y1 = y + CARD_HEIGHT
    draw.rounded_rectangle(
        [x0, y, x1, y1], radius=CARD_RADIUS, fill=CARD_COLOR
    )

    # Number badge: navy circle with a white number, left side.
    badge_x0 = x0 + 30
    badge_y0 = y + 32
    draw.ellipse(
        [badge_x0, badge_y0, badge_x0 + BADGE_DIAMETER, badge_y0 + BADGE_DIAMETER],
        fill=BG_COLOR,
    )
    number = str(index + 1)
    num_w = draw.textlength(number, font=fonts["badge"])
    num_h = fonts["badge"].size
    draw.text(
        (
            badge_x0 + (BADGE_DIAMETER - num_w) / 2,
            badge_y0 + (BADGE_DIAMETER - num_h) / 2 - 2,
        ),
        number,
        font=fonts["badge"],
        fill=HEADER_TEXT,
    )

    # Category label, top of the text block.
    draw.text(
        (TEXT_X, y + 30),
        category,
        font=fonts["category"],
        fill=CATEGORY_COLOR,
    )

    # Headline, wrapped to at most two lines.
    max_text_width = x1 - 30 - TEXT_X
    lines = fit_two_lines(draw, headline, fonts["headline"], max_text_width)
    line_y = y + 66
    for line in lines:
        draw.text(
            (TEXT_X, line_y),
            line,
            font=fonts["headline"],
            fill=TITLE_COLOR,
        )
        line_y += 40

    # Source line, bottom of the card.
    draw.text(
        (TEXT_X, y + CARD_HEIGHT - 38),
        "Source: " + source,
        font=fonts["source"],
        fill=SOURCE_COLOR,
    )


def draw_footer(draw, fonts):
    """Bottom footer: aggregated source list and date."""
    text_w = draw.textlength(FOOTER_TEXT, font=fonts["footer"])
    draw.text(
        ((CANVAS_WIDTH - text_w) / 2, FOOTER_Y),
        FOOTER_TEXT,
        font=fonts["footer"],
        fill=FOOTER_COLOR,
    )


def main():
    """Assemble the image and save it to /output/entry.png."""
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(image)
    fonts = load_fonts()

    draw_header(draw, fonts)

    y = CARDS_TOP
    for index, item in enumerate(NEWS):
        draw_card(draw, fonts, index, item, y)
        y += CARD_HEIGHT + CARD_GAP

    draw_footer(draw, fonts)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    image.save(OUTPUT_PATH, "PNG")
    print("Saved {} ({}x{})".format(OUTPUT_PATH, CANVAS_WIDTH, CANVAS_HEIGHT))


if __name__ == "__main__":
    main()
