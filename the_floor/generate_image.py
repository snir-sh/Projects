import io
import random
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont


def _cell_color(label: str):
    """Deterministic (stable) color per label."""
    if label == "X":
        return (245, 245, 245)
    # simple hash -> pastel-ish color
    h = sum(ord(c) for c in label)
    r = 120 + (h * 3) % 100
    g = 120 + (h * 7) % 100
    b = 120 + (h * 11) % 100
    return (
        random.randint(60, 220),
        random.randint(60, 220),
        random.randint(60, 220),
    )

def generate_grid_png(state: Dict[str, object]) -> io.BytesIO:
    width = int(state["width"])
    height = int(state["height"])
    grid = state["grid"]  # List[List[str]]

    cell = 90
    pad = 20
    header_h = 40
    left_w = 40

    img_w = left_w + width * cell + pad
    img_h = header_h + height * cell + pad

    img = Image.new("RGB", (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to load a nicer font; fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 28)
        small = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    # Column numbers
    for x in range(width):
        tx = left_w + x * cell + cell // 2
        draw.text((tx - 6, 10), str(x + 1), fill=(0, 0, 0), font=small)

    # Row numbers
    for y in range(height):
        ty = header_h + y * cell + cell // 2
        draw.text((10, ty - 8), str(y + 1), fill=(0, 0, 0), font=small)

    # Cells
    for y in range(height):
        for x in range(width):
            label = grid[y][x]
            x0 = left_w + x * cell
            y0 = header_h + y * cell
            x1 = x0 + cell
            y1 = y0 + cell

            draw.rectangle([x0, y0, x1, y1], outline=(0, 0, 0), width=2, fill=_cell_color(label))

            # Center label
            text = str(label)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((x0 + (cell - tw) / 2, y0 + (cell - th) / 2), text, fill=(0, 0, 0), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf