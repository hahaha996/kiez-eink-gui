from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Optional, Union
import os

# --- Return codes ---
OK = 0          # fully inside the box (no clipping)
CLIPPED = 1     # text exceeded box; was clipped

Color = Union[Tuple[int, int, int], Tuple[int, int, int, int], str]

def _parse_color(c: Color) -> Tuple[int, int, int, int]:
    """Accepts (R,G,B), (R,G,B,A) or '#RRGGBB'/'#RRGGBBAA' and returns RGBA."""
    if isinstance(c, tuple):
        if len(c) == 3:
            return (c[0], c[1], c[2], 255)
        if len(c) == 4:
            return c
        raise ValueError("Color tuple must be length 3 or 4.")
    if isinstance(c, str):
        s = c.lstrip("#")
        if len(s) == 6:
            r = int(s[0:2], 16); g = int(s[2:4], 16); b = int(s[4:6], 16)
            return (r, g, b, 255)
        if len(s) == 8:
            r = int(s[0:2], 16); g = int(s[2:4], 16); b = int(s[4:6], 16); a = int(s[6:8], 16)
            return (r, g, b, a)
        raise ValueError("Hex color must be #RRGGBB or #RRGGBBAA.")
    raise ValueError("Unsupported color type.")

def _load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(font_path, size=size)
    except Exception as e:
        raise RuntimeError(f"Failed to load font '{font_path}' at size {size}: {e}")

def _text_bbox(font: ImageFont.FreeTypeFont, text: str) -> Tuple[int, int, int, int]:
    """
    Returns (x0, y0, x1, y1) for the string at (0,0) baseline using font.getbbox().
    Works better than getsize for precise vertical metrics.
    """
    return font.getbbox(text)  # requires Pillow ≥ 8.0

def draw_text_boxes_fixed(
    image_path: str,
    items: List[Dict],
    *,
    output_path: Optional[str] = None,
    default_align: str = "left",     # "left" | "center" | "right"
    default_valign: str = "top"      # "top" | "center" | "bottom"
) -> Dict[int, int]:
    """
    Draws text into (x1,y1,x2,y2) boxes WITHOUT wrapping or resizing.
    Text is clipped to its box. Returns {index: OK|CLIPPED}.

    items: list of dicts, each with:
      {
        "text": str,
        "box": (x1, y1, x2, y2),
        "font_path": str,
        "size": int,
        "color": Color,               # e.g., (0,0,0) or "#FF0000"
        # optional per-item overrides:
        "align": "left"|"center"|"right",
        "valign": "top"|"center"|"bottom"
      }
    """
    base_img = Image.open(image_path).convert("RGBA")
    canvas = base_img.copy()  # where we’ll paste text layers
    statuses: Dict[int, int] = {}

    for idx, it in enumerate(items):
        text: str = it["text"]
        x1, y1, x2, y2 = map(int, it["box"])
        font_path: str = it["font_path"]
        size: int = int(it["size"])
        color = _parse_color(it["color"])
        align = it.get("align", default_align)
        valign = it.get("valign", default_valign)

        box_w = max(0, x2 - x1)
        box_h = max(0, y2 - y1)
        if box_w == 0 or box_h == 0:
            statuses[idx] = CLIPPED
            continue

        font = _load_font(font_path, size)
        # Measure text using font bbox
        tx0, ty0, tx1, ty1 = _text_bbox(font, text)
        text_w = tx1 - tx0
        text_h = ty1 - ty0

        # Create a transparent layer exactly the size of the box (this enforces clipping)
        layer = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # Horizontal positioning
        if align == "center":
            draw_x = (box_w - text_w) / 2 - tx0
        elif align == "right":
            draw_x = box_w - text_w - tx0
        else:  # left
            draw_x = -tx0

        # Vertical positioning
        if valign == "center":
            draw_y = (box_h - text_h) / 2 - ty0
        elif valign == "bottom":
            draw_y = box_h - text_h - ty0
        else:  # top
            draw_y = -ty0

        # Draw text onto the layer
        draw.text((draw_x, draw_y), text, font=font, fill=color)

        # Determine if any dimension clips
        clipped = 1 if (text_w > box_w or text_h > box_h) else 0
        statuses[idx] = CLIPPED if clipped else OK

        # Paste the layer into the canvas at (x1, y1) using itself as mask (clip is inherent)
        canvas.alpha_composite(layer, (x1, y1))

    # Save with original format (unless output_path provided)
    if output_path is None:
        root, ext = os.path.splitext(image_path)
        output_path = f"{root}_with_text{ext}"
    # Convert back if original was non-alpha (e.g., JPG)
    if base_img.mode != "RGBA" and output_path.lower().endswith((".jpg", ".jpeg")):
        canvas = canvas.convert("RGB")
    canvas.save(output_path)

    return statuses
