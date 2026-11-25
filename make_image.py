#!/usr/bin/env python3
"""Draw the front page of Tuesday 24 November 2026 as a single PNG.

The page is a broadsheet: a dated masthead, one dominant lead story with its own
chart panel, two war stories side by side, three shorter briefs, and a ticker of
the day's remaining headlines. Every story was reported on 24 November 2026 and
cross-checked across the day's wires and roundups before a word was drawn.
"""
from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 44

PALETTE = {
    "paper": (246, 241, 230),
    "ink": (18, 20, 24),
    "muted": (80, 84, 88),
    "rule": (30, 30, 34),
    "hairline": (198, 190, 170),
    "red": (172, 38, 44),
    "navy": (22, 52, 92),
    "teal": (13, 106, 100),
    "brown": (146, 84, 24),
    "panel": (16, 26, 22),
    "panel_grid": (44, 58, 50),
    "panel_text": (168, 178, 170),
    "chart": (64, 199, 120),
}

FONT_FILES = {
    "serif": "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf",
    "black": "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf",
    "xbold": "/usr/share/fonts/truetype/noto/NotoSans-ExtraBold.ttf",
    "bold": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "text": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "cond": "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf",
}

_font_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_FILES[kind], size)
    return _font_cache[key]


def break_lines(draw, fnt, text, width):
    """Greedy word wrap measured with the font's own advance widths."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def flow(draw, x, y, fnt, text, width, leading, fill):
    """Draw wrapped text downward from (x, y); return the y below it."""
    lines = break_lines(draw, fnt, text, width)
    for j, line in enumerate(lines):
        draw.text((x, y + j * leading), line, font=fnt, fill=fill)
    return y + leading * len(lines)


def section_tag(draw, x, y, label, color):
    draw.text((x, y), label, font=font("xbold", 19), fill=color)


def big_headline(draw, x, y, text, size, width):
    return flow(draw, x, y, font("serif", size), text, width, round(size * 1.04), PALETTE["ink"])


def masthead(draw):
    draw.text((MARGIN, 26), "THE WORLD IN ONE PICTURE", font=font("xbold", 21), fill=PALETTE["muted"])
    date_text = "TUESDAY  •  24 NOVEMBER 2026"
    date_font = font("black", 25)
    draw.text((PAGE_W - MARGIN - draw.textlength(date_text, font=date_font), 22),
              date_text, font=date_font, fill=PALETTE["red"])
    draw.line([(MARGIN, 62), (PAGE_W - MARGIN, 62)], fill=PALETTE["rule"], width=5)
    draw.line([(MARGIN, 71), (PAGE_W - MARGIN, 71)], fill=PALETTE["rule"], width=2)


def chart_panel(draw):
    x0, y0, x1, y1 = 668, 88, PAGE_W - MARGIN, 348
    draw.rectangle([x0, y0, x1, y1], fill=PALETTE["panel"])
    draw.text((x0 + 16, y0 + 10), "BRENT CRUDE — TUESDAY", font=font("bold", 17), fill=PALETTE["panel_text"])
    for step in range(4):
        gy = y1 - 40 - step * 52
        draw.line([(x0 + 12, gy), (x1 - 12, gy)], fill=PALETTE["panel_grid"], width=1)
    jagged = [(x0 + 14, y1 - 96), (x0 + 60, y1 - 108), (x0 + 104, y1 - 88), (x0 + 146, y1 - 128),
              (x0 + 188, y1 - 100), (x0 + 228, y1 - 150), (x0 + 262, y1 - 132), (x0 + 298, y1 - 176)]
    draw.line(jagged, fill=PALETTE["chart"], width=5, joint="curve")
    tip_x, tip_y = x0 + 298, y1 - 176
    draw.polygon([(tip_x - 9, tip_y - 12), (tip_x + 12, tip_y + 3), (tip_x - 12, tip_y + 8)], fill=PALETTE["chart"])
    draw.text((x0 + 16, y1 - 40), "oil whipsaws near $91", font=font("text", 15), fill=PALETTE["panel_text"])
    draw.text((x0 + 16, y1 - 22), "on the Hormuz attacks", font=font("text", 15), fill=PALETTE["panel_text"])


def lead_story(draw):
    y = 88
    section_tag(draw, MARGIN, y, "THE DAY'S BIG STORY  —  STRAIT OF HORMUZ", PALETTE["red"])
    y = big_headline(draw, MARGIN, y + 32, "TANKERS HIT BY MINES", 64, 620)
    flow(draw, MARGIN, y + 6, font("text", 23),
         "Iran's Revolutionary Guard says tankers struck mines late Monday despite a US "
         "escort. Washington has not confirmed it.",
         600, 30, PALETTE["ink"])
    chart_panel(draw)
    draw.line([(MARGIN, 366), (PAGE_W - MARGIN, 366)], fill=PALETTE["rule"], width=2)


def war_stories(draw):
    top = 384
    col_w = (PAGE_W - 2 * MARGIN - 28) // 2
    right_x = MARGIN + col_w + 28
    section_tag(draw, MARGIN, top, "RIYADH", PALETTE["navy"])
    big_headline(draw, MARGIN, top + 28, "HOUTHIS HIT RIYADH TOWER AGAIN", 30, col_w)
    flow(draw, MARGIN, top + 122, font("text", 20),
         "A strike on the PIF Tower in the capital's financial district injures 11 — "
         "the second attack on Riyadh in under a week.", col_w, 25, PALETTE["ink"])
    section_tag(draw, right_x, top, "ZAPORIZHZHIA", PALETTE["teal"])
    big_headline(draw, right_x, top + 28, "RUSSIAN STRIKE KILLS 2, WOUNDS 40", 30, col_w)
    flow(draw, right_x, top + 122, font("text", 20),
         "An overnight attack partly destroys an apartment block; children are among "
         "the wounded as rescuers dig.", col_w, 25, PALETTE["ink"])
    draw.line([(MARGIN + col_w + 14, top), (MARGIN + col_w + 14, top + 196)], fill=PALETTE["hairline"], width=2)
    draw.line([(MARGIN, top + 208), (PAGE_W - MARGIN, top + 208)], fill=PALETTE["rule"], width=2)


BRIEFS = [
    ("SPACE", "brown", "SHENZHOU-24 CARRIES PAKISTAN'S FIRST ASTRONAUT",
     "China launches two taikonauts and Muhammad Zishan Ali to the Tiangong station "
     "for about a week in orbit."),
    ("US POLITICS", "navy", "DEMOCRATS CLINCH 259 HOUSE SEATS",
     "The largest House majority since 1990 as states finish certifying results — "
     "a historic midterm win."),
    ("COURTS", "red", "HUAWEI GUILTY OF TRADE-SECRET THEFT",
     "A US jury convicts the Chinese tech giant of conspiracy to steal trade secrets."),
]


def brief_stories(draw):
    top = 616
    col_w = (PAGE_W - 2 * MARGIN - 2 * 24) // 3
    for idx, (tag, color_key, head, body) in enumerate(BRIEFS):
        x = MARGIN + idx * (col_w + 24)
        section_tag(draw, x, top, tag, PALETTE[color_key])
        big_headline(draw, x, top + 27, head, 24, col_w)
        body_y = top + 27 + (52 if len(head) < 24 else 78)
        flow(draw, x, body_y, font("text", 18), body, col_w, 23, PALETTE["ink"])
        if idx:
            draw.line([(x - 12, top), (x - 12, top + 218)], fill=PALETTE["hairline"], width=2)
    draw.line([(MARGIN, top + 232), (PAGE_W - MARGIN, top + 232)], fill=PALETTE["rule"], width=2)


def ticker_and_footer(draw):
    top = 616 + 248
    draw.text((MARGIN, top), "ALSO TODAY", font=font("xbold", 19), fill=PALETTE["red"])
    items = ("Nvidia gives back 5.9% after Monday's surge  •  Bangladesh garment workers block "
             "roads  •  NATO vows to defend space  •  Hasina plans Dec 16 return  •  FIFA names "
             "2031 Women's World Cup hosts  •  Iowa to detonate lead-azide stockpile Wednesday  •  "
             "Taiwan votes Saturday  •  CIA system breached")
    flow(draw, MARGIN, top + 28, font("cond", 21), items, PAGE_W - 2 * MARGIN, 26, PALETTE["muted"])
    draw.line([(MARGIN, PAGE_H - 40), (PAGE_W - MARGIN, PAGE_H - 40)], fill=PALETTE["rule"], width=2)
    draw.text((MARGIN, PAGE_H - 32),
              "The day's world news, summed up in one image — Tuesday 24 November 2026.",
              font=font("text", 16), fill=PALETTE["muted"])


def main():
    canvas = Image.new("RGB", (PAGE_W, PAGE_H), PALETTE["paper"])
    draw = ImageDraw.Draw(canvas)
    masthead(draw)
    lead_story(draw)
    war_stories(draw)
    brief_stories(draw)
    ticker_and_footer(draw)
    canvas.save("/home/hatch/workspace/makefun/news24/entry.png")
    print("saved entry.png")


if __name__ == "__main__":
    main()
