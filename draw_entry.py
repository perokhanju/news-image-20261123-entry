import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BAND_ALPHA = 150
HEADLINE_ALPHA = 160
TOP_GRAD_HEIGHT = 400
TOP_GRAD_ALPHA = 180
BOTTOM_GRAD_HEIGHT = 160
BOTTOM_GRAD_ALPHA = 150
WATERMARK_CROP = 60

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "art_raw.png")
OUT = os.path.join(ROOT, "app", "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(path, size, default):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return default


def letterspaced_text(draw, pos, text, font, fill, spacing):
    x, y = pos
    total = sum(draw.textlength(c, font=font) + spacing for c in text)
    x -= total / 2
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + spacing


def vertical_gradient_overlay(img, top_height, top_alpha, bottom_height, bottom_alpha):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    for y in range(top_height):
        a = int(top_alpha * (top_height - y) / top_height)
        od.line((0, y, W, y), fill=(0, 0, 0, a))
    for y in range(H - bottom_height, H):
        a = int(bottom_alpha * (y - (H - bottom_height)) / bottom_height)
        od.line((0, y, W, y), fill=(0, 0, 0, a))

    return Image.alpha_composite(img.convert("RGBA"), overlay)


def text_band(draw, text, font, cy, fill=(255, 255, 255, BAND_ALPHA), pad_x=20, pad_y=8, left_bar=(255, 255, 255), bar_width=8):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    band_h = th + 2 * pad_y
    x0 = (W - tw) / 2 - pad_x
    x1 = (W + tw) / 2 + pad_x
    y0 = cy - band_h / 2
    y1 = cy + band_h / 2
    draw.rectangle([x0, y0, x1, y1], fill=fill)
    draw.rectangle([x0, y0, x0 + bar_width, y1], fill=left_bar)
    draw.text((x0 + pad_x + bar_width, y0 + pad_y), text, font=font, fill="white")


def main():
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    img = img.crop((0, 0, w, h - WATERMARK_CROP))

    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale + 0.5), int(img.height * scale + 0.5)), Image.LANCZOS)
    x = (img.width - W) // 2
    y = (img.height - H) // 2
    img = img.crop((x, y, x + W, y + H))

    img = vertical_gradient_overlay(img, TOP_GRAD_HEIGHT, TOP_GRAD_ALPHA, BOTTOM_GRAD_HEIGHT, BOTTOM_GRAD_ALPHA)

    draw = ImageDraw.Draw(img)

    f_mast = font(BOLD, 84, ImageFont.load_default())
    mast_y = 60

    mast_bbox = draw.textbbox((0, 0), "THE WORLD", font=f_mast)
    mast_w = mast_bbox[2] - mast_bbox[0]
    draw.text(((W - mast_w) / 2 - mast_bbox[0], mast_y - mast_bbox[1]), "THE WORLD", font=f_mast, fill="white")

    rule_y = mast_y - mast_bbox[1] + (mast_bbox[3] - mast_bbox[1]) + 6
    draw.line([(W / 2 - 140, rule_y), (W / 2 + 140, rule_y)], fill="white", width=2)

    f_date = font(REGULAR, 24, ImageFont.load_default())
    letterspaced_text(draw, (W / 2, rule_y + 22), "MONDAY, NOVEMBER 23, 2026", f_date, (255, 255, 255), spacing=4)

    headline = "CLIMATE TALKS COLLAPSE"
    head_cy = 430
    head_pad_x = 30
    head_pad_y = 16
    head_margin = 60
    max_band_w = W - 2 * head_margin

    f_head = font(BOLD, 108, ImageFont.load_default())
    htw = draw.textbbox((0, 0), headline, font=f_head)[2]
    while htw + 2 * head_pad_x > max_band_w:
        f_head = font(BOLD, f_head.size - 1, ImageFont.load_default())
        htw = draw.textbbox((0, 0), headline, font=f_head)[2]

    hb = draw.textbbox((0, 0), headline, font=f_head)
    htw = hb[2] - hb[0]
    hth = hb[3] - hb[1]
    band_h = hth + 2 * head_pad_y
    band_w = htw + 2 * head_pad_x
    x0 = (W - band_w) / 2
    x1 = (W + band_w) / 2
    y0 = head_cy - band_h / 2
    y1 = head_cy + band_h / 2
    draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, HEADLINE_ALPHA))
    draw.text((x0 + head_pad_x, y0 + head_pad_y), headline, font=f_head, fill="white")

    banners = [
        ("COP31 ENDS IN DEADLOCK", (0, 128, 255)),
        ("IRAN STRIKES GULF TANKERS", (255, 60, 60)),
        ("UKRAINE TALKS STALL", (60, 220, 120)),
        ("CARTEL BOSS CAUGHT", (255, 180, 40)),
    ]

    f_ban = font(BOLD, 44, ImageFont.load_default())
    row_h = 64
    start_y = H - BOTTOM_GRAD_HEIGHT - 220
    for i, (txt, bar_color) in enumerate(banners):
        cy = start_y + i * row_h
        text_band(draw, txt, f_ban, cy, fill=(0, 0, 0, BAND_ALPHA), left_bar=bar_color)

    f_src = font(REGULAR, 18, ImageFont.load_default())
    src = "SOURCE: POLLINATIONS.AI / MAKE.FUN NEWS-IMAGE-20261123"
    sb = draw.textbbox((0, 0), src, font=f_src)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) / 2 - sb[0], H - 32 - sb[1]), src, font=f_src, fill=(235, 235, 235))

    img = img.convert("RGB")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
