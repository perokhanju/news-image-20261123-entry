#!/usr/bin/env python3
"""Draw the newspaper infographic for make.fun competition news-image-20261123.

HYBRID POSTER layout:
- AI-generated background art (art_raw.png), bottom 60px watermark cropped off,
  center-cropped and resized to exactly 1024x1024.
- Dark vertical gradient overlay on top for headline readability.
- Serif masthead + date + main headline, bottom ticker banner.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Palette
OFF_WHITE = (245, 241, 232)   # #F5F1E8
AMBER = (255, 184, 77)        # #FFB84D
RED = (192, 0, 43)
SHADOW = (0, 0, 0)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
ART_PATH = "art_raw.png"
OUT_DIR = "app"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

W, H = 1024, 1024


def load_font(size, bold=False, serif=False):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_width(text, font):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def text_height(text, font):
    bbox = font.getbbox(text)
    return bbox[3] - bbox[1]


def load_background():
    """Load art_raw.png, drop bottom 60px (watermark), center-crop square, resize 1024x1024."""
    art = Image.open(ART_PATH).convert("RGB")
    aw, ah = art.size
    art = art.crop((0, 0, aw, ah - 60))          # remove pollinations.ai watermark
    aw, ah = art.size
    side = min(aw, ah)
    left = (aw - side) // 2
    top = (ah - side) // 2
    art = art.crop((left, top, left + side, top + side))   # center-crop to square
    return art.resize((W, H), Image.LANCZOS)


def add_top_gradient(img, height=380, max_alpha=200):
    """Dark vertical gradient: alpha max_alpha -> 0 over the top `height` px."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(height):
        alpha = int(max_alpha * (1.0 - y / height))
        od.line([(0, y), (W, y)], fill=(8, 6, 4, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def draw_centered(draw, y, text, font, fill):
    """Draw text horizontally centered at top coordinate y."""
    x = (W - text_width(text, font)) // 2
    draw.text((x + 2, y + 2), text, font=font, fill=SHADOW)
    draw.text((x, y), text, font=font, fill=fill)


def build_banner_lines(labels, font, sep, max_width):
    """Split labels into lines (joined by red-dot separators) that fit max_width."""
    one = sep.join(labels)
    if text_width(one, font) <= max_width:
        return [labels]
    best = None
    for i in range(1, len(labels)):
        l1 = sep.join(labels[:i])
        l2 = sep.join(labels[i:])
        w1, w2 = text_width(l1, font), text_width(l2, font)
        if w1 <= max_width and w2 <= max_width:
            spread = abs(w1 - w2)
            if best is None or spread < best[0]:
                best = (spread, [labels[:i], labels[i:]])
    return best[1] if best else [labels]


def draw_entry():
    img = load_background()
    img = add_top_gradient(img)
    draw = ImageDraw.Draw(img)

    # Fonts
    f_masthead = load_font(90, bold=True, serif=True)
    f_date = load_font(34, bold=True)
    f_headline = load_font(56, bold=True, serif=True)

    # ── MASTHEAD ──────────────────────────────────────────────────────────────
    draw_centered(draw, 26, "THE WORLD", f_masthead, OFF_WHITE)

    # ── DATE LINE ─────────────────────────────────────────────────────────────
    draw_centered(draw, 142, "MONDAY, NOVEMBER 23, 2026", f_date, AMBER)

    # ── MAIN HEADLINE (centered around y=260) + thin red underline ────────────
    headline = "CLIMATE TALKS COLLAPSE"
    hw = text_width(headline, f_headline)
    hh = text_height(headline, f_headline)
    hy = 260 - hh // 2
    draw_centered(draw, hy, headline, f_headline, OFF_WHITE)
    # thin red rule under the headline
    pad = 24
    rx0 = max(24, (W - (hw + 2 * pad)) // 2)
    rx1 = min(W - 24, (W + (hw + 2 * pad)) // 2)
    ry = 260 + hh // 2 + 26
    draw.rectangle([rx0, ry, rx1, ry + 4], fill=RED)

    # ── BOTTOM BANNER ─────────────────────────────────────────────────────────
    labels = [
        "COP31 ENDS IN DEADLOCK",
        "IRAN STRIKES GULF",
        "UKRAINE TALKS STALL",
        "CARTEL BOSS CAUGHT",
    ]
    strip_x0, strip_y0, strip_x1, strip_y1 = 20, 940, W - 20, 1010
    hard_max = 984

    font_size = 24
    f_banner = load_font(font_size, bold=True)
    sep = "  \u2022  "
    lines = build_banner_lines(labels, f_banner, sep, hard_max)
    total_w = text_width(sep.join(lines[0]), f_banner)
    # check widths; if still too wide shrink
    while total_w > hard_max and font_size >= 16:
        font_size -= 1
        f_banner = load_font(font_size, bold=True)
        lines = build_banner_lines(labels, f_banner, sep, hard_max)
        total_w = text_width(sep.join(lines[0]), f_banner)

    # semi-transparent black rounded strip
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    sd.rounded_rectangle([strip_x0, strip_y0, strip_x1, strip_y1],
                         radius=14, fill=(0, 0, 0, 175))
    img = Image.alpha_composite(img, strip)
    draw = ImageDraw.Draw(img)

    # draw labels on the strip
    n_lines = len(lines)
    if n_lines == 1:
        text_y = strip_y0 + (strip_y1 - strip_y0) // 2 - text_height(sep.join(labels), f_banner) // 2
        draw.text((strip_x0 + 24, text_y), sep.join(labels), font=f_banner, fill=OFF_WHITE)
    else:
        line_h = text_height("Ay", f_banner)
        total_h = n_lines * line_h + (n_lines - 1) * 6
        start_y = strip_y0 + (strip_y1 - strip_y0) // 2 - total_h // 2
        for i, line_labels in enumerate(lines):
            line_text = sep.join(line_labels)
            line_y = start_y + i * (line_h + 6)
            draw.text((strip_x0 + 24, line_y), line_text, font=f_banner, fill=OFF_WHITE)

    # Save
    os.makedirs(OUT_DIR, exist_ok=True)
    # Convert RGBA to RGB for PNG (white-ish background)
    rgb_out = Image.new("RGB", (W, H), (0, 0, 0))
    rgb_out.paste(img, mask=img.split()[3])
    rgb_out.save(OUT_PATH, "PNG")
    sz = os.path.getsize(OUT_PATH)
    print(f"Saved {OUT_PATH}  ({sz:,} bytes)  size={W}x{H}  ({sz/1024/1024:.2f} MiB)")
    return sz

if __name__ == "__main__":
    draw_entry()
