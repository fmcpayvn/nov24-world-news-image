#!/usr/bin/env python3
"""Draw the 24 November 2026 world-news front page from stories.json.

Reads the verified story list (lead story, two second leads, six continent
sections, 45 stories in total) and renders a 1024x1024 newspaper front
page with Pillow. No network access, no external assets: DejaVu fonts only.

Usage:
    python3 render.py [output.png]     # default output is entry.png
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "stories.json"
DEFAULT_OUTPUT = HERE / "entry.png"

PAGE = 1024
MARGIN = 42
GUTTER = 26

PAPER = (247, 243, 234)      # warm newsprint
INK = (20, 20, 20)           # near-black
FAINT = (90, 85, 75)         # muted grey for the dateline
ACCENT = (140, 29, 24)       # dark red for kickers and section heads
RULE = (60, 58, 52)          # hairline grey

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF = FONT_DIR / "DejaVuSerif.ttf"
SERIF_BOLD = FONT_DIR / "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR / "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"


def load_font(path, size):
    """Load a TrueType font, falling back to Pillow's built-in bitmap font."""
    try:
        return ImageFont.truetype(str(path), size)
    except (OSError, IOError):
        return ImageFont.load_default()


def greedy_wrap(draw, text, font, max_width):
    """Wrap text into lines that fit max_width, measuring real glyph widths."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def wrapped_height(draw, text, font, max_width, leading):
    """Height in pixels that wrapped text would occupy at this leading."""
    lines = greedy_wrap(draw, text, font, max_width)
    return len(lines) * leading


def draw_wrapped(draw, x, y, text, font, max_width, leading, fill=INK):
    """Draw wrapped text starting at (x, y); return the y after the block."""
    for line in greedy_wrap(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def draw_rule(draw, x0, x1, y, width=2):
    """A horizontal hairline rule."""
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def draw_centered(draw, y, text, font, fill=INK):
    """Draw one line centred on the page; return the y after the line."""
    width = draw.textlength(text, font=font)
    draw.text(((PAGE - width) / 2, y), text, font=font, fill=fill)
    return y + font.size


def fit_font(draw, text, path, start_size, max_width, min_size=20):
    """Largest font size at which the text fits on one line within max_width."""
    size = start_size
    while size > min_size:
        font = load_font(path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return load_font(path, min_size)


def section_block_height(draw, section, width, body_font, body_leading):
    """Height of one continent section: header plus every story headline."""
    header_font = load_font(SANS_BOLD, 15)
    height = header_font.size + 5  # header text + gap to the rule
    height += 5                    # rule + gap to the first story
    for story in section["stories"]:
        height += wrapped_height(draw, "\u2022  " + story, body_font,
                                 width, body_leading)
        height += 2                # gap between stories
    return height


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT

    with open(DATA_FILE, encoding="utf-8") as handle:
        data = json.load(handle)

    for key in ("date", "masthead", "footer", "lead", "second_leads",
                "sections"):
        if key not in data:
            raise SystemExit(f"stories.json is missing required key: {key}")
    if len(data["sections"]) != 6:
        raise SystemExit(
            f"expected 6 continent sections, found {len(data['sections'])}")
    total = sum(len(section["stories"]) for section in data["sections"])
    if total + 1 + len(data["second_leads"]) != 45:
        print(f"warning: story count is {total + 3}, expected 45",
              file=sys.stderr)

    lead = data["lead"]
    second_leads = data["second_leads"]
    sections = data["sections"]

    day = datetime.strptime(data["date"], "%d %B %Y")
    dateline = day.strftime("%A").upper() + ", " + data["date"].upper()

    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)
    left = MARGIN
    right = PAGE - MARGIN
    content_width = right - left

    # ---- Masthead -------------------------------------------------------
    y = 26
    masthead_font = fit_font(draw, data["masthead"], SERIF_BOLD, 58,
                             content_width)
    y = draw_centered(draw, y, data["masthead"], masthead_font)
    y += 8
    draw_rule(draw, left, right, y, width=3)
    y += 6
    y = draw_centered(draw, y, dateline, load_font(SANS_BOLD, 18), fill=FAINT)
    y += 6
    draw_rule(draw, left, right, y, width=1)
    y += 12

    # ---- Lead story -----------------------------------------------------
    kicker_font = load_font(SANS_BOLD, 17)
    draw.text((left, y), lead["kicker"], font=kicker_font, fill=ACCENT)
    y += 25
    headline_font = load_font(SERIF_BOLD, 38)
    headline_lines = greedy_wrap(draw, lead["headline"], headline_font,
                                 content_width)
    for line in headline_lines:
        draw.text((left, y), line, font=headline_font, fill=INK)
        y += 45
    y += 3
    y = draw_wrapped(draw, left, y, lead["summary"],
                     load_font(SANS, 17), content_width, 23)
    y += 10
    draw_rule(draw, left, right, y, width=1)
    y += 12

    # ---- Second leads, side by side -------------------------------------
    column_width = (content_width - GUTTER) // 2
    second_top = y
    second_bottom = second_top
    for index, story in enumerate(second_leads):
        x = left + index * (column_width + GUTTER)
        block_y = second_top
        draw.text((x, block_y), story["kicker"], font=kicker_font, fill=ACCENT)
        block_y += 24
        block_y = draw_wrapped(draw, x, block_y, story["headline"],
                               load_font(SERIF_BOLD, 21), column_width, 26)
        block_y += 2
        block_y = draw_wrapped(draw, x, block_y, story["summary"],
                               load_font(SANS, 14), column_width, 18)
        second_bottom = max(second_bottom, block_y)
    y = second_bottom + 10
    draw_rule(draw, left, right, y, width=1)
    y += 12

    # ---- Continent sections, 3 columns x 2 rows -------------------------
    # Pick the largest body size whose grid still fits above the footer.
    footer_top = PAGE - 40
    grid_bottom_limit = footer_top - 10
    column_width = (content_width - 2 * GUTTER) // 3
    chosen_size = None
    for body_size in (13, 12, 11, 10, 9):
        body_font = load_font(SANS, body_size)
        body_leading = body_size + 3
        row_heights = []
        for row in range(2):
            row_height = 0
            for col in range(3):
                section = sections[row * 3 + col]
                height = section_block_height(draw, section, column_width,
                                              body_font, body_leading)
                row_height = max(row_height, height)
            row_heights.append(row_height)
        grid_height = row_heights[0] + 12 + row_heights[1]
        if y + grid_height <= grid_bottom_limit:
            chosen_size = body_size
            break
    if chosen_size is None:
        chosen_size = 9
        print("warning: sections do not fit even at 9pt; drawing anyway",
              file=sys.stderr)
    body_font = load_font(SANS, chosen_size)
    body_leading = chosen_size + 3

    header_font = load_font(SANS_BOLD, 15)
    for row in range(2):
        row_top = y
        row_bottom = row_top
        for col in range(3):
            section = sections[row * 3 + col]
            x = left + col * (column_width + GUTTER)
            block_y = row_top
            draw.text((x, block_y), section["continent"], font=header_font,
                      fill=ACCENT)
            block_y += header_font.size + 5
            draw_rule(draw, x, x + column_width, block_y, width=1)
            block_y += 5
            for story in section["stories"]:
                block_y = draw_wrapped(draw, x, block_y, "\u2022  " + story,
                                       body_font, column_width, body_leading)
                block_y += 2
            row_bottom = max(row_bottom, block_y)
        y = row_bottom + 12

    # ---- Footer ---------------------------------------------------------
    draw_rule(draw, left, right, footer_top - 10, width=1)
    footer_font = load_font(SANS_BOLD, 16)
    draw_centered(draw, footer_top, "45 stories \u00b7 6 continents",
                  footer_font, fill=FAINT)

    page.save(output)
    print(f"Wrote {output} ({PAGE}x{PAGE})")


if __name__ == "__main__":
    main()
