#!/usr/bin/env python3
"""Draw a one-page newspaper front page for Tuesday 24 November 2026.

Renders a 1024x1024 broadsheet-style image summarising the day's world
news and writes it to entry.png next to this script.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/noto"

# --- palette ----------------------------------------------------------------
PAPER = (246, 241, 231)      # warm newsprint
INK = (26, 26, 24)           # near-black
SOFT_INK = (74, 70, 64)      # secondary text
RED = (176, 42, 32)          # accent red
NAVY = (31, 58, 95)          # section tag navy
TEAL = (15, 106, 92)         # section tag teal
CHART_BG = (20, 38, 62)      # dark panel behind the oil chart
CHART_GRID = (62, 84, 118)
CHART_LINE = (240, 178, 74)  # amber line
RULE = (26, 26, 24)
HAIRLINE = (150, 142, 128)

W = H = 1024
MARGIN = 40
CONTENT_W = W - 2 * MARGIN


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "NotoSerif-Regular.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SERIF_ITALIC = "NotoSerif-Italic.ttf"
SANS = "NotoSans-Regular.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    """Draw wrapped lines starting at (x, y); return the y below the block."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def shrink_to_fit(draw, text, fnt_name, start_size, max_width):
    """Largest font size (<= start_size) at which text fits on one line."""
    size = start_size
    while size > 10:
        fnt = font(fnt_name, size)
        if draw.textlength(text, font=fnt) <= max_width:
            return fnt
        size -= 1
    return font(fnt_name, 10)


def rule(draw, y, x0=MARGIN, x1=W - MARGIN, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag(draw, x, y, label, colour):
    """Small caps section label; returns the y below it."""
    fnt = font(SANS_BOLD, 15)
    draw.text((x, y), label, font=fnt, fill=colour)
    return y + 22


def headline_block(draw, x, y, max_w, text, size, leading):
    """Serif bold headline, wrapped; returns the y below it."""
    fnt = font(SERIF_BOLD, size)
    lines = wrap(draw, text, fnt, max_w)
    return draw_lines(draw, lines, x, y, fnt, INK, leading)


def body_block(draw, x, y, max_w, text, size, leading):
    """Serif body copy, wrapped; returns the y below it."""
    fnt = font(SERIF, size)
    lines = wrap(draw, text, fnt, max_w)
    return draw_lines(draw, lines, x, y, fnt, INK, leading)


def draw_chart(draw, x0, y0, x1, y1):
    """Dark Brent-crude panel with a jagged rising price line."""
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CHART_BG)
    px0, py0 = x0 + 26, y0 + 52
    px1, py1 = x1 - 26, y1 - 46
    title = font(SANS_BOLD, 17)
    draw.text((x0 + 26, y0 + 16), "BRENT CRUDE — TUESDAY", font=title,
              fill=(240, 236, 226))
    # horizontal gridlines with price labels
    grid_font = font(SANS, 13)
    for frac, label in ((0.0, "$91"), (0.5, "$87"), (1.0, "$83")):
        gy = py0 + frac * (py1 - py0)
        draw.line([(px0, gy), (px1, gy)], fill=CHART_GRID, width=1)
        draw.text((px0 + 2, gy - 17), label, font=grid_font,
                  fill=(150, 168, 190))
    # jagged line: whipsawing upward through the day
    points = [(0.00, 0.78), (0.08, 0.62), (0.15, 0.70), (0.24, 0.48),
              (0.32, 0.58), (0.40, 0.36), (0.48, 0.52), (0.56, 0.30),
              (0.64, 0.44), (0.72, 0.22), (0.80, 0.34), (0.88, 0.12),
              (0.96, 0.18), (1.00, 0.08)]
    coords = [(px0 + fx * (px1 - px0), py0 + fy * (py1 - py0))
              for fx, fy in points]
    draw.line(coords, fill=CHART_LINE, width=3, joint="curve")
    for cx, cy in coords:
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=CHART_LINE)
    caption = font(SANS, 14)
    draw.text((x0 + 26, y1 - 34),
              "Oil whipsawed near $91 a barrel after the attacks.",
              font=caption, fill=(214, 210, 200))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- masthead ------------------------------------------------------------
    mast = shrink_to_fit(draw, "THE WORLD IN ONE PICTURE",
                         SERIF_BOLD, 44, 640)
    draw.text((MARGIN, 34), "THE WORLD IN ONE PICTURE", font=mast, fill=INK)
    date_font = font(SANS_BOLD, 19)
    date_text = "TUESDAY • 24 NOVEMBER 2026"
    dw = draw.textlength(date_text, font=date_font)
    draw.text((W - MARGIN - dw, 48), date_text, font=date_font, fill=RED)
    rule(draw, 112, width=3)
    rule(draw, 118, width=1)

    # --- lead story + oil chart ----------------------------------------------
    lead_x = MARGIN
    lead_w = 560
    chart_x0 = 624
    chart_x1 = W - MARGIN
    top = 140

    y = tag(draw, lead_x, top, "THE DAY'S BIG STORY — STRAIT OF HORMUZ", RED)
    y = headline_block(draw, lead_x, y + 6, lead_w,
                       "Tankers Hit by Mines in the Strait of Hormuz",
                       42, 50)
    y = body_block(draw, lead_x, y + 10, lead_w,
                   "Iran's Revolutionary Guard says tankers struck mines "
                   "late Monday despite a US naval escort. Washington has "
                   "not confirmed the attacks, and oil prices surged as "
                   "traders weighed the risk to the world's busiest oil "
                   "chokepoint.",
                   19, 26)
    draw_chart(draw, chart_x0, top, chart_x1, 436)

    rule(draw, 452, width=1)

    # --- two middle stories ----------------------------------------------------
    mid_top = 470
    left_w = 448
    right_x = 536
    right_w = W - MARGIN - right_x
    draw.line([(512, mid_top), (512, 640)], fill=HAIRLINE, width=1)

    y = tag(draw, MARGIN, mid_top, "RIYADH", TEAL)
    y = headline_block(draw, MARGIN, y + 4, left_w,
                       "Houthis Hit Riyadh Tower Again", 27, 33)
    body_block(draw, MARGIN, y + 8, left_w,
               "A strike on the PIF Tower in the capital's financial "
               "district injured 11 people — the second attack on Riyadh "
               "in under a week.",
               17, 23)

    y = tag(draw, right_x, mid_top, "ZAPORIZHZHIA", NAVY)
    y = headline_block(draw, right_x, y + 4, right_w,
                       "Russian Strike Kills 2, Wounds 40 in Zaporizhzhia",
                       27, 33)
    body_block(draw, right_x, y + 8, right_w,
               "An overnight attack partly destroyed an apartment block. "
               "Children were among the wounded as rescuers dug through "
               "the rubble.",
               17, 23)

    rule(draw, 656, width=1)

    # --- three briefs ----------------------------------------------------------
    brief_top = 674
    cols = [(MARGIN, 288), (MARGIN + 340, 288), (MARGIN + 668, 276)]
    draw.line([(368, brief_top), (368, 830)], fill=HAIRLINE, width=1)
    draw.line([(696, brief_top), (696, 830)], fill=HAIRLINE, width=1)

    briefs = [
        ("SPACE", TEAL, "Shenzhou-24 Carries Pakistan's First Astronaut",
         "China launched two taikonauts and Muhammad Zishan Ali to the "
         "Tiangong station for about a week in orbit."),
        ("US POLITICS", NAVY, "Democrats Clinch 259 House Seats",
         "The largest House majority since 1990 as states finish "
         "certifying results."),
        ("COURTS", RED, "Huawei Guilty of Trade-Secret Theft",
         "A US jury convicted the Chinese tech giant of conspiracy to "
         "steal trade secrets."),
    ]
    for (label, colour, head, body), (cx, col_w) in zip(briefs, cols):
        y = tag(draw, cx, brief_top, label, colour)
        y = headline_block(draw, cx, y + 4, col_w, head, 19, 24)
        body_block(draw, cx, y + 6, col_w, body, 15, 20)

    rule(draw, 846, width=1)

    # --- also-today ticker -----------------------------------------------------
    tick_font = font(SANS, 15)
    tick_bold = font(SANS_BOLD, 15)
    items = [
        "Nvidia gives back 5.9 percent after Monday's surge",
        "Bangladesh garment workers block roads",
        "NATO vows to defend space",
        "Hasina plans a Dec 16 return",
        "FIFA names 2031 Women's World Cup hosts",
        "Iowa to detonate its lead-azide stockpile Wednesday",
        "Taiwan votes Saturday",
        "an unclassified CIA system was breached",
    ]
    ticker = "  •  ".join(items)
    y = 862
    draw.text((MARGIN, y), "ALSO TODAY", font=tick_bold, fill=RED)
    label_w = draw.textlength("ALSO TODAY   ", font=tick_bold)
    lines = wrap(draw, ticker, tick_font, CONTENT_W - label_w)
    draw_lines(draw, lines, MARGIN + label_w, y, tick_font, SOFT_INK, 21)

    rule(draw, 940, width=1)

    # --- footer ----------------------------------------------------------------
    foot = font(SERIF_ITALIC, 16)
    foot_text = "The day's world news, summed up in one image — Tuesday 24 November 2026."
    fw = draw.textlength(foot_text, font=foot)
    draw.text(((W - fw) / 2, 954), foot_text, font=foot, fill=SOFT_INK)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
