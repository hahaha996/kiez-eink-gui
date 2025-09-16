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

def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Split text into lines that fit within max_width."""
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def draw_text_boxes_fixed(
    image_path: str,
    items: List[Dict],
    *,
    output_path: Optional[str] = None,
    default_align: str = "left",     # "left" | "center" | "right"
    default_valign: str = "top"      # "top" | "center" | "bottom"
) -> Dict[int, int]:
    """
    Draws text into (x1,y1,x2,y2) boxes WITH wrapping.
    If wrapped text exceeds the box vertically, extra lines are trimmed.
    Returns {index: OK|CLIPPED}.
    """
    base_img = Image.open(image_path).convert("RGBA")
    canvas = base_img.copy()
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
        layer = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # --- Wrap text to fit width ---
        lines = _wrap_text(draw, text, font, box_w)
        line_h = font.getbbox("Hg")[3] - font.getbbox("Hg")[1]
        total_h = len(lines) * line_h

        # >>> new: add adjustable line spacing factor <<<
        line_spacing = int(line_h * 1.2)   # e.g. 20% more space
        total_h = len(lines) * line_spacing

        # Vertical positioning offset
        if valign == "center":
            y = max(0, (box_h - total_h) / 2)
        elif valign == "bottom":
            y = max(0, box_h - total_h)
        else:  # top
            y = 0

        clipped = 0
        for line in lines:
            if y + line_h > box_h:  # line would exceed box height
                clipped = 1
                break
            w = draw.textlength(line, font=font)
            if align == "center":
                x = (box_w - w) / 2
            elif align == "right":
                x = box_w - w
            else:
                x = 0
            draw.text((x, y), line, font=font, fill=color)
            # y += line_h
            y += line_spacing   # <<< use spacing instead of line_h

        statuses[idx] = CLIPPED if clipped else OK
        canvas.alpha_composite(layer, (x1, y1))

    if output_path is None:
        root, ext = os.path.splitext(image_path)
        output_path = f"{root}_with_text{ext}"
    if base_img.mode != "RGBA" and output_path.lower().endswith((".jpg", ".jpeg")):
        canvas = canvas.convert("RGB")
    canvas.save(output_path)

    return statuses


def draw_text_boxes_rgba(
    image_path: str,
    items: List[Dict],
    *,
    output_path: Optional[str] = None,
    default_align: str = "left",     # "left" | "center" | "right"
    default_valign: str = "top"      # "top" | "center" | "bottom"
) -> Dict[int, int]:
    """
    Anti-aliased RGBA rendering (like your original), with integer positioning and adjustable line spacing.
    Returns {index: OK|CLIPPED}.
    """
    base_img = Image.open(image_path).convert("RGBA")
    canvas = base_img.copy()
    statuses: Dict[int, int] = {}

    for idx, it in enumerate(items):
        text: str = it["text"]
        x1, y1, x2, y2 = map(int, it["box"])
        font_path: str = it["font_path"]
        size: int = int(it["size"])
        color = _parse_color(it["color"])  # RGBA tuple
        align = it.get("align", default_align)
        valign = it.get("valign", default_valign)

        box_w = max(0, x2 - x1)
        box_h = max(0, y2 - y1)
        if box_w == 0 or box_h == 0:
            statuses[idx] = CLIPPED
            continue

        font = _load_font(font_path, size)

        # Render on transparent RGBA layer to preserve soft edges
        layer = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # --- Wrap text to fit width ---
        lines = _wrap_text(draw, text, font, box_w)

        # metrics
        bbox = font.getbbox("Hg")
        line_h = (bbox[3] - bbox[1]) if bbox else int(font.size * 1.2)
        line_spacing = int(line_h * 1.2)  # 20% extra
        total_h = len(lines) * line_spacing

        # Vertical positioning offset
        if valign == "center":
            y = max(0, (box_h - total_h) / 2)
        elif valign == "bottom":
            y = max(0, box_h - total_h)
        else:
            y = 0

        clipped = 0
        for line in lines:
            if y + line_h > box_h:
                clipped = 1
                break
            w = draw.textlength(line, font=font)
            if align == "center":
                x = (box_w - w) / 2
            elif align == "right":
                x = box_w - w
            else:
                x = 0

            # draw (allow fractional x/y for natural AA in RGBA)
            draw.text((x, y), line, font=font, fill=color)
            y += line_spacing

        statuses[idx] = CLIPPED if clipped else OK
        canvas.alpha_composite(layer, (x1, y1))

    if output_path is None:
        root, ext = os.path.splitext(image_path)
        output_path = f"{root}_with_text{ext}"
    # Convert to RGB if saving JPEG
    if output_path.lower().endswith((".jpg", ".jpeg")):
        canvas = canvas.convert("RGB")
    canvas.save(output_path)
    return statuses

def _luminance(color_rgba) -> float:
    r, g, b, *rest = color_rgba
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def draw_text_boxes_1bit_mono(
    image_path: str,
    items: List[Dict],
    *,
    output_path: Optional[str] = None,
    default_align: str = "left",     # "left" | "center" | "right"
    default_valign: str = "top"      # "top" | "center" | "bottom"
) -> Dict[int, int]:
    """
    Draw crisp text onto a mono (1-bit) bitmap (e.g., 960x680).
    - No anti-aliasing, no dithering.
    - Uses a 1-bit mask per box; pastes ink (0 or 1) into the canvas through that mask.
    Returns {index: OK|CLIPPED}.
    """
    base_img = Image.open(image_path)
    if base_img.mode != "1":
        # Keep it bilevel; avoid introducing grayscale/AA.
        base_img = base_img.convert("1")
    canvas = base_img.copy()

    statuses: Dict[int, int] = {}

    for idx, it in enumerate(items):
        text: str = it["text"]
        x1, y1, x2, y2 = map(int, it["box"])
        font_path: str = it["font_path"]
        size: int = int(it["size"])
        rgba = _parse_color(it["color"])  # any RGBA -> will map to black/white ink
        align = it.get("align", default_align)
        valign = it.get("valign", default_valign)

        # Choose ink: 1 = white pixel, 0 = black pixel (Pillow "1" mode)
        ink = 1 if _luminance(rgba) >= 128 else 0

        box_w = max(0, x2 - x1)
        box_h = max(0, y2 - y1)
        if box_w == 0 or box_h == 0:
            statuses[idx] = CLIPPED
            continue

        font = _load_font(font_path, size)

        # 1-bit mask layer: glyphs drawn as 1, background 0
        mask = Image.new("1", (box_w, box_h), 0)
        mdraw = ImageDraw.Draw(mask)

        # Wrap text to fit width (measure using the same draw+font)
        lines = _wrap_text(mdraw, text, font, box_w)

        # Metrics
        bbox = font.getbbox("Hg")
        line_h = (bbox[3] - bbox[1]) if bbox else int(font.size * 1.2)
        line_spacing = int(line_h * 1.2)  # integer spacing for clean rows
        total_h = len(lines) * line_spacing

        # Vertical offset (integer to avoid subpixel)
        if valign == "center":
            y = max(0, (box_h - total_h) // 2)
        elif valign == "bottom":
            y = max(0, box_h - total_h)
        else:
            y = 0

        clipped = 0
        for line in lines:
            if y + line_h > box_h:
                clipped = 1
                break

            # Width + integer x for pixel-snapped placement
            w = mdraw.textlength(line, font=font)
            w_i = int(round(w))
            if align == "center":
                x = (box_w - w_i) // 2
            elif align == "right":
                x = box_w - w_i
            else:
                x = 0

            # Draw glyphs onto 1-bit mask (no anti-aliasing)
            mdraw.text((int(x), int(y)), line, font=font, fill=1)
            y += line_spacing

        statuses[idx] = CLIPPED if clipped else OK

        # Paste chosen ink through the 1-bit mask into the 1-bit canvas
        # This only flips pixels where mask==1 inside the target box.
        canvas.paste(ink, (x1, y1, x2, y2), mask)

    if output_path is None:
        root, ext = os.path.splitext(image_path)
        # Keep the original extension; PNG preserves 1-bit well.
        output_path = f"{root}_with_text_1bit{ext}"

    # Ensure final stays bilevel and undithered
    canvas = canvas.convert("1", dither=Image.NONE)
    canvas.save(output_path)
    return statuses