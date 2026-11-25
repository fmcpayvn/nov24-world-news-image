#!/usr/bin/env python3
"""Render the 24 Nov 2026 world-news front page, 1024x1024 PNG."""
import json, os
from PIL import Image, ImageDraw, ImageFont

ENTRY = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (90, 86, 78)
RULE = (60, 58, 52)

def font(name, size):
    pats = {
        "serif_b": ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"],
        "serif": ["/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"],
        "serif_i": ["/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"],
        "sans_b": ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"],
        "sans": ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"],
    }
    for p in pats[name]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def main():
    d = json.load(open(f"{ENTRY}/stories.json"))
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)
    M = 30
    # --- masthead ---
    f_title = font("serif_b", 54)
    dr.text((W // 2, 22), d["masthead"], font=f_title, fill=INK, anchor="ma")
    f_date = font("sans_b", 16)
    dr.text((W // 2, 88), "TUESDAY, 24 NOVEMBER 2026  ·  THE WORLD, IN ONE PAGE",
            font=f_date, fill=GREY, anchor="ma")
    dr.line([(M, 116), (W - M, 116)], fill=RULE, width=3)
    dr.line([(M, 121), (W - M, 121)], fill=RULE, width=1)
    # --- lead ---
    y = 134
    f_kick = font("sans_b", 15)
    dr.text((M, y), d["lead"]["kicker"], font=f_kick, fill=RED)
    y += 22
    f_lead = font("serif_b", 40)
    for ln in wrap(dr, d["lead"]["headline"], f_lead, W - 2 * M):
        dr.text((M, y), ln, font=f_lead, fill=INK)
        y += 46
    y += 4
    f_sum = font("serif", 17)
    for ln in wrap(dr, d["lead"]["summary"], f_sum, W - 2 * M):
        dr.text((M, y), ln, font=f_sum, fill=INK)
        y += 22
    y += 8
    dr.line([(M, y), (W - M, y)], fill=RULE, width=2)
    y += 12
    # --- second leads, two columns ---
    col_w = (W - 2 * M - 24) // 2
    tops = []
    for i, s in enumerate(d["second_leads"]):
        x = M + i * (col_w + 24)
        yy = y
        dr.text((x, yy), s["kicker"], font=font("sans_b", 13), fill=RED)
        yy += 19
        for ln in wrap(dr, s["headline"], font("serif_b", 19), col_w):
            dr.text((x, yy), ln, font=font("serif_b", 19), fill=INK)
            yy += 24
        yy += 3
        for ln in wrap(dr, s["summary"], font("serif", 14), col_w):
            dr.text((x, yy), ln, font=font("serif", 14), fill=(45, 45, 45))
            yy += 19
        tops.append(yy)
    y = max(tops) + 10
    dr.line([(M, y), (W - M, y)], fill=RULE, width=2)
    y += 12
    # --- continent grid: 3 cols x 2 rows ---
    cols, rows = 3, 2
    gw, gh = (W - 2 * M - 2 * 20) // cols, (H - y - 44 - 12) // rows
    f_head = font("sans_b", 15)
    f_story = font("sans", 12)
    for idx, sec in enumerate(d["sections"]):
        cx = M + (idx % cols) * (gw + 20)
        cy = y + (idx // cols) * (gh + 12)
        dr.rectangle([(cx, cy), (cx + gw, cy + 21)], fill=INK)
        dr.text((cx + 8, cy + 3), sec["continent"], font=f_head, fill=PAPER)
        yy = cy + 28
        for st in sec["stories"]:
            for ln in wrap(dr, "•  " + st, f_story, gw - 4):
                if yy + 14 > cy + gh:
                    break
                dr.text((cx + 2, yy), ln, font=f_story, fill=INK)
                yy += 14
    # --- footer ---
    fy = H - 30
    dr.line([(M, fy - 8), (W - M, fy - 8)], fill=RULE, width=1)
    dr.text((W // 2, fy), d["footer"], font=font("sans", 12), fill=GREY, anchor="ma")
    img.save(f"{ENTRY}/entry.png")
    print("saved", f"{ENTRY}/entry.png", img.size)

if __name__ == "__main__":
    main()
