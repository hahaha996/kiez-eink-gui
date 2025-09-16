#!/usr/bin/env python3
"""
Split a red/black/white image into two 1-bit BMPs:
- <name>_black_white.bmp : black pixels -> black, everything else -> white
- <name>_red_white.bmp   : red pixels   -> black, everything else -> white
"""

import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image


def parse_args():
    p = argparse.ArgumentParser(description="Export 1-bit BMPs for black/white and red/white from an RBW image.")
    p.add_argument("input", help="Path to the input image (PNG/JPG/BMP, etc.)")
    p.add_argument("--outdir", default=None, help="Optional output directory.")
    return p.parse_args()


def exact_mask(arr: np.ndarray, rgb: Tuple[int, int, int]) -> np.ndarray:
    """
    Return a boolean mask where pixels match exactly the given RGB tuple.
    """
    return np.all(arr == np.array(rgb, dtype=np.uint8), axis=2)

def reddish_mask(arr, hue_low=340, hue_high=30, sat_min=40, val_min=60):
    """Return mask for red/orange/pink colors based on HSV."""
    hsv = Image.fromarray(arr, mode="RGB").convert("HSV")
    hsv = np.array(hsv, dtype=np.uint16)
    H = hsv[..., 0].astype(np.float32) * (360.0 / 255.0)
    S, V = hsv[..., 1], hsv[..., 2]
    hue_ok = (H >= hue_low) | (H <= hue_high)  # wraparound at 0°
    return hue_ok & (S >= sat_min) & (V >= val_min)

def mask_to_1bpp(mask: np.ndarray) -> Image.Image:
    """
    Convert a boolean mask to a 1-bit PIL image:
      True  -> black (0)
      False -> white (255)
    """
    l_img = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8), mode="L")
    return l_img.convert("1", dither=Image.NONE)


def spit_red_black(path: str, outdir: str | None = None) -> Tuple[Path, Path]:
    """
    Process the image at `path` and write two 1-bit BMPs:
      - <stem>_black_white.bmp (exact black preserved)
      - <stem>_red_white.bmp   (exact red preserved)

    Returns: (bw_path, rw_path)
    """
    in_path = Path(path)
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    output_dir = Path(outdir) if outdir else in_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load as RGB array
    img = Image.open(in_path).convert("RGB")
    arr = np.array(img)

    # Exact color masks
    black_mask = exact_mask(arr, (0, 0, 0))
    red_mask   = exact_mask(arr, (255, 0, 0))
    # red_mask   = reddish_mask(arr)

    # Convert to 1-bit images
    bw_img = mask_to_1bpp(black_mask)
    rw_img = mask_to_1bpp(red_mask)

    # Save
    stem = in_path.stem
    bw_path = output_dir / f"{stem}__black_white.bmp"
    rw_path = output_dir / f"{stem}__red_white.bmp"

    bw_img.save(bw_path, format="BMP")
    rw_img.save(rw_path, format="BMP")

    return bw_path, rw_path


def main():
    args = parse_args()
    bw_path, rw_path = spit_red_black(args.input, args.outdir)
    print(f"Saved:\n  {bw_path}\n  {rw_path}")


if __name__ == "__main__":
    main()
