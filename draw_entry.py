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

# Design values
MASTHEAD_TEXT = "THE WORLD"
DATELINE_TEXT = "MONDAY, NOVEMBER 23, 2026"
HEADLINE_TEXT = "CLIMATE TALKS COLLAPSE"
BANNER_LABELS = [
    "COP31 ENDS IN DEADLOCK",
    "IRAN STRIKES GULF",
    "UKRAINE TALKS STALL",
    "CARTEL BOSS CAUGHT",
]
SOURCE_TEXT = "SOURCE: POLLINATIONS.AI  \u00b7  MAKE.FUN NEWS-IMAGE-20261123"

# Geometry
DATELINE_BAND = (118, 176, 170, 14)
HEADLINE_BAND = (222, 318, 150, 16)
HEADLINE_CENTER_Y = 260
MASTHEAD_Y = 26
DATELINE_Y = 142
BANNER_BOX = (20, 940, W - 20, 1000)
BANNER_HARD_MAX = 984
BANNER_RADIUS = 14
BANNER_FILL = (0, 0, 0, 175)
BANNER_FONT_START = 24
BANNER_FONT_MIN = 16
SOURCE_Y = H - 21
SOURCE_FONT_SIZE = 15


def load_font(size, bold=False, serif=False):
    """Return a DejaVu TrueType font of the given size/style."""
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_width(text, font):
    """Return the rendered width in pixels of text for a given font."""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def text_height(text, font):
    """Return the rendered height in pixels of text for a given font."""
    bbox = font.getbbox(text)
    return bbox[3] - bbox[1]


def load_art():
    """Load art_raw.png, drop bottom 60px watermark, center-crop square, resize 1024x1024."""
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


def add_bottom_gradient(img, height=56, max_alpha=110):
    """Subtle darkening at the bottom edge so the source line stays readable."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(height):
        alpha = int(max_alpha * (1.0 - y / height))
        od.line([(0, H - 1 - y), (W, H - 1 - y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, overlay)


def add_backing_band(img, y0, y1, alpha=150, radius=12):
    """Semi-transparent dark rounded band behind headline/dateline for contrast."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([24, y0, W - 24, y1], radius=radius, fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, overlay)


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


def compose_background():
    """Compose art with top gradient and both contrast backing bands."""
    img = load_art()
    img = add_top_gradient(img)
    img = add_backing_band(img, *DATELINE_BAND)
    img = add_backing_band(img, *HEADLINE_BAND)
    return img


def draw_masthead(draw):
    """Draw the centered serif masthead."""
    draw_centered(draw, MASTHEAD_Y, MASTHEAD_TEXT,
                  load_font(90, bold=True, serif=True), OFF_WHITE)


def draw_headline(draw):
    """Draw the dateline, main headline, and thin red underline."""
    f_date = load_font(34, bold=True)
    draw_centered(draw, DATELINE_Y, DATELINE_TEXT, f_date, AMBER)

    f_headline = load_font(56, bold=True, serif=True)
    hw = text_width(HEADLINE_TEXT, f_headline)
    hh = text_height(HEADLINE_TEXT, f_headline)
    hy = HEADLINE_CENTER_Y - hh // 2
    draw_centered(draw, hy, HEADLINE_TEXT, f_headline, OFF_WHITE)
    pad = 24
    rx0 = max(24, (W - (hw + 2 * pad)) // 2)
    rx1 = min(W - 24, (W + (hw + 2 * pad)) // 2)
    ry = HEADLINE_CENTER_Y + hh // 2 + 26
    draw.rectangle([rx0, ry, rx1, ry + 4], fill=RED)


def draw_banners(img):
    """Draw the bottom ticker strip with the four sub-headlines on a rounded band."""
    strip_x0, strip_y0, strip_x1, strip_y1 = BANNER_BOX
    sep = "  \u2022  "

    font_size = BANNER_FONT_START
    f_banner = load_font(font_size, bold=True)
    lines = build_banner_lines(BANNER_LABELS, f_banner, sep, BANNER_HARD_MAX)
    total_w = text_width(sep.join(lines[0]), f_banner)
    while total_w > BANNER_HARD_MAX and font_size >= BANNER_FONT_MIN:
        font_size -= 1
        f_banner = load_font(font_size, bold=True)
        lines = build_banner_lines(BANNER_LABELS, f_banner, sep, BANNER_HARD_MAX)
        total_w = text_width(sep.join(lines[0]), f_banner)

    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    sd.rounded_rectangle([strip_x0, strip_y0, strip_x1, strip_y1],
                         radius=BANNER_RADIUS, fill=BANNER_FILL)
    img = Image.alpha_composite(img, strip)
    draw = ImageDraw.Draw(img)

    n_lines = len(lines)
    if n_lines == 1:
        text_y = strip_y0 + (strip_y1 - strip_y0) // 2 - text_height(sep.join(BANNER_LABELS), f_banner) // 2
        draw.text((strip_x0 + 24, text_y), sep.join(BANNER_LABELS), font=f_banner, fill=OFF_WHITE)
    else:
        line_h = text_height("Ay", f_banner)
        total_h = n_lines * line_h + (n_lines - 1) * 6
        start_y = strip_y0 + (strip_y1 - strip_y0) // 2 - total_h // 2
        for i, line_labels in enumerate(lines):
            line_text = sep.join(line_labels)
            line_y = start_y + i * (line_h + 6)
            draw.text((strip_x0 + 24, line_y), line_text, font=f_banner, fill=OFF_WHITE)
    return img


def save_entry(img):
    """Flatten the RGBA image onto a black RGB canvas, save PNG, and report size."""
    os.makedirs(OUT_DIR, exist_ok=True)
    rgb_out = Image.new("RGB", (W, H), (0, 0, 0))
    rgb_out.paste(img, mask=img.split()[3])
    rgb_out.save(OUT_PATH, "PNG")
    sz = os.path.getsize(OUT_PATH)
    print(f"Saved {OUT_PATH}  ({sz:,} bytes)  size={W}x{H}  ({sz/1024/1024:.2f} MiB)")
    return sz


def draw_entry():
    """Generate the full poster: background, masthead, headline, banner, source."""
    img = compose_background()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_headline(draw)
    img = draw_banners(img)

    # bottom gradient + source line
    f_source = load_font(SOURCE_FONT_SIZE)
    sw = text_width(SOURCE_TEXT, f_source)
    source_x = (W - sw) // 2
    img = add_bottom_gradient(img)
    draw = ImageDraw.Draw(img)
    draw.text((source_x + 1, SOURCE_Y + 1), SOURCE_TEXT, font=f_source, fill=(0, 0, 0))
    draw.text((source_x, SOURCE_Y), SOURCE_TEXT, font=f_source, fill=(205, 195, 180))

    return save_entry(img)


if __name__ == "__main__":
    draw_entry()
