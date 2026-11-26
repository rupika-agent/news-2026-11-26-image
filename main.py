"""Draw a one-image summary of 26 November 2026 world news.

Deterministic: fixed fonts, fixed geometry, fixed text.
No randomness, no current time, no network access.
Run: python3 main.py  ->  writes /output/entry.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 1500
BG = (13, 27, 62)
HEADER_BG = (10, 20, 46)
CARD_BG = (255, 255, 255)
ACCENT = (255, 176, 32)
TITLE_COLOR = (255, 255, 255)
SUB_COLOR = (176, 196, 230)
TEXT_COLOR = (18, 30, 54)
SOURCE_COLOR = (90, 106, 138)
FOOTER_COLOR = (150, 170, 205)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NEWS = [
    ("TRADE",
     "US proposes new tariffs aimed at factory overcapacity",
     "Reuters"),
    ("UKRAINE WAR",
     "Ukraine says it struck a major Russian air base, damaging five planes",
     "Reuters"),
    ("NORTH KOREA",
     "North Korea's Kim calls for wider use of tactical nuclear weapons",
     "Agence France-Presse"),
    ("UNITED STATES",
     "New York postpones Thanksgiving Day parade over major storm",
     "Associated Press"),
    ("MUSIC",
     "Duran Duran guitarist and songwriter Andy Taylor dies at 65",
     "Reuters"),
]


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap using the draw object's text length."""
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


def draw_header(draw, title_font, sub_font):
    draw.rectangle([0, 0, WIDTH, 210], fill=HEADER_BG)
    draw.rectangle([0, 210, WIDTH, 218], fill=ACCENT)
    draw.text((60, 48), "26 NOVEMBER 2026", font=title_font, fill=ACCENT)
    draw.text((60, 108), "World News in One Image", font=sub_font, fill=TITLE_COLOR)
    draw.text((60, 158), "Five stories that defined the day",
              font=load_font(FONT_REG, 26), fill=SUB_COLOR)


def draw_cards(draw, title_font, body_font, tag_font, source_font):
    y = 258
    card_h = 212
    gap = 20
    for index, (tag, headline, source) in enumerate(NEWS, start=1):
        draw.rounded_rectangle([60, y, WIDTH - 60, y + card_h],
                               radius=18, fill=CARD_BG)
        # Number badge
        draw.ellipse([84, y + 28, 144, y + 88], fill=BG)
        num = str(index)
        num_w = draw.textlength(num, font=title_font)
        draw.text((114 - num_w / 2, y + 36), num, font=title_font, fill=ACCENT)
        # Tag
        draw.text((168, y + 30), tag, font=tag_font, fill=(196, 120, 0))
        # Headline, wrapped to two lines max width
        lines = wrap_text(draw, headline, body_font, WIDTH - 60 - 168 - 40)
        line_y = y + 66
        for line in lines[:2]:
            draw.text((168, line_y), line, font=body_font, fill=TEXT_COLOR)
            line_y += 46
        # Source line
        draw.text((168, y + 168), "Source: " + source,
                  font=source_font, fill=SOURCE_COLOR)
        y += card_h + gap


def draw_footer(draw, footer_font):
    draw.text((60, HEIGHT - 58),
              "Sources: Reuters, Agence France-Presse, Associated Press  |  26 Nov 2026",
              font=footer_font, fill=FOOTER_COLOR)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    title_font = load_font(FONT_BOLD, 44)
    sub_font = load_font(FONT_BOLD, 52)
    tag_font = load_font(FONT_BOLD, 24)
    body_font = load_font(FONT_BOLD, 34)
    source_font = load_font(FONT_REG, 26)
    footer_font = load_font(FONT_REG, 24)

    draw_header(draw, title_font, sub_font)
    draw_cards(draw, title_font, body_font, tag_font, source_font)
    draw_footer(draw, footer_font)

    out_path = "/output/entry.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    image.save(out_path, format="PNG")
    print("Wrote " + out_path + " " + str(WIDTH) + "x" + str(HEIGHT))


if __name__ == "__main__":
    main()
