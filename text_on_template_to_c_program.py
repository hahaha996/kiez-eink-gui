# file: epd_text_runner.py
from pathlib import Path
import ctypes as ct
import argparse
import sys

# -------------------------
# Constants (no hardcoded absolute paths)
# -------------------------
ALLOWED_SIZES = [8, 12, 16, 20, 24]

DEFAULT_BLACK_BMP_NAME = "vorsorge_black_white.bmp"
DEFAULT_RY_BMP_NAME    = "vorsorge_red_white.bmp"

# Default items payload (edit freely)
DEFAULT_ITEMS = [
    {
        "text": "CBRN-Gefahrenstoffe",
        "box": [40, 320, 820, 345],
        "size": 20,
        "color": "red",
        "style": "bold",
    },
    {
        "text": "Die unterschiedlichen Gefahrenstoffe",
        "box": [40, 355, 820, 370],
        "size": 16,
        "color": "black",
        "style": "bold",
    },
    {
        "text": "Ein Laie kann in der Regel die Gefaehrlichkeit von chemischen (C), biologischen (B),  radiologischen (R) und nuklearen (N) Gefahrenstoffen nicht erkennen.",
        "box": [40, 375, 820, 410],
        "size": 12,
        "color": "black",
        "style": "normal",
    },
    {
        "text": "Wirkung auf Haut und Koerper",
        "box": [40, 420, 820, 440],
        "size": 16,
        "color": "black",
        "style": "bold",
    },
    {
        "text": "Verhalten bei Gefahrenstoff-Freisetzung. Kontaktieren Sie die lokale Giftnotrufzentrale.",
        "box": [40, 445, 820, 470],
        "size": 12,
        "color": "black",
        "style": "normal",
    },
    {
        "text": "Giftnotruf der Charite Universitaetsmedizin Berlin:",
        "box": [40, 470, 650, 495],
        "size": 12,
        "color": "black",
        "style": "normal",
    },
    {
        "text": "030 192 40",
        "box": [468, 470, 820, 495],
        "size": 12,
        "color": "red",
        "style": "bold",
    },
    {
        "text": "Verhalten zu Hause",
        "box": [40, 500, 820, 520],
        "size": 16,
        "color": "black",
        "style": "bold",
    },
    {
        "text": "Bleiben Sie im Gebaeude, schliessen Sie Fenster und Tueren. Schalten Sie Ventilatoren und  Lueftungen aus. Vermeiden Sie unnoetigen Sauerstoffverbrauch durch Kerzen oder aehnliches. Bei radioaktiven Stoffen: suchen Sie einen Kellerraum auf",
        "box": [40, 525, 820, 580],
        "size": 12,
        "color": "black",
        "style": "normal",
    },
    {
        "text": "Verhalten im Auto oder im Freien",
        "box": [40, 590, 820, 615],
        "size": 16,
        "color": "black",
        "style": "bold",
    },
    {
        "text": "Bewegen Sie sich moeglichst quer zur Windrichtung. Atmen Sie moeglichst durch einen Atemschutz, zumindest durch ein Taschentuch. Waschen Sie Haende, Gesicht und Haare, ebenso Nase und Ohren mit Wasser und Seife. Bei biologischen Stoffen: desinfizieren Sie Ihre Haende zusaetzlich.",
        "box": [40, 620, 820, 670],
        "size": 12,
        "color": "black",
        "style": "normal",
    },
]

# -------------------------
# ctypes struct
# -------------------------
class TextItem(ct.Structure):
    _fields_ = [
        ("text",  ct.c_char_p),   # const char*
        ("box",   ct.c_int * 4),  # int[4]
        ("color", ct.c_char_p),   # "red" or "black"
        ("size",  ct.c_int),      # point size
    ]

# -------------------------
# Helpers
# -------------------------
def _discover_library(base_dir: Path) -> Path:
    """
    Try common spots relative to this file:
    - ./c-eink-project/libepd13in3b.so
    - ./libepd13in3b.so
    """
    candidates = [
        base_dir / "c-eink-project" / "libepd13in3b.so",
        base_dir / "libepd13in3b.so",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "Shared library libepd13in3b.so not found. "
        f"Tried: {', '.join(str(c) for c in candidates)}"
    )

def _build_ctypes_items(items_py):
    items_for_c = []
    for it in items_py:
        size = it.get("size", ALLOWED_SIZES[0])
        if size not in ALLOWED_SIZES:
            size = ALLOWED_SIZES[0]
        b = it["box"]
        items_for_c.append(TextItem(
            text=it["text"].encode("utf-8"),
            box=(ct.c_int * 4)(b[0], b[1], b[2], b[3]),
            color=it["color"].encode("ascii"),  # "red"/"black"
            size=size,
        ))
    ArrayType = TextItem * len(items_for_c)
    return ArrayType(*items_for_c)

# -------------------------
# Public API
# -------------------------
def run_epd_with_text(
    items=DEFAULT_ITEMS,
    lib_path: str | None = None,
    output_dir: str | Path | None = None,
    black_bmp_name: str = DEFAULT_BLACK_BMP_NAME,
    ry_bmp_name: str    = DEFAULT_RY_BMP_NAME,
) -> int:
    """
    Load the shared library and call:
      int kiezbox_EPD_13in3b_with_text(const char* black_bmp_path,
                                       const char* ry_bmp_path,
                                       TextItem *text_items,
                                       int count)

    Returns the C function's integer result.
    """
    base_dir = Path(__file__).resolve().parent

    # Discover library path if not provided
    lib_file = Path(lib_path) if lib_path else _discover_library(base_dir)

    # Discover output dir (defaults to ./ready_to_use next to this file)
    out_dir = Path(output_dir) if output_dir else (base_dir / "ready_to_use")
    black_path = out_dir / black_bmp_name
    ry_path    = out_dir / ry_bmp_name

    # Load shared library
    lib = ct.CDLL(str(lib_file))

    # Declare function signature
    lib.kiezbox_EPD_13in3b_with_text.argtypes = [
        ct.c_char_p,                # black_bmp_path
        ct.c_char_p,                # ry_bmp_path
        ct.POINTER(TextItem),       # text_items
        ct.c_int                    # count
    ]
    lib.kiezbox_EPD_13in3b_with_text.restype = ct.c_int

    # Build C array
    items_arr = _build_ctypes_items(items)

    # Prepare parameters (bytes)
    black_b = str(black_path).encode("utf-8")
    ry_b    = str(ry_path).encode("utf-8")

    # Call the C function
    result = lib.kiezbox_EPD_13in3b_with_text(black_b, ry_b, items_arr, len(items_arr))
    return result

# -------------------------
# CLI / test entrypoint
# -------------------------
def _parse_args(argv):
    p = argparse.ArgumentParser(description="Run EPD with text items via ctypes.")
    p.add_argument("--lib", help="Path to libepd13in3b.so (defaults to discovery).")
    p.add_argument("--out", help="Directory containing BMPs (defaults to ./ready_to_use).")
    p.add_argument("--black", default=DEFAULT_BLACK_BMP_NAME,
                   help=f"Black BMP filename (default: {DEFAULT_BLACK_BMP_NAME})")
    p.add_argument("--ry", default=DEFAULT_RY_BMP_NAME,
                   help=f"Red/Yellow BMP filename (default: {DEFAULT_RY_BMP_NAME})")
    return p.parse_args(argv)

if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    try:
        rc = run_epd_with_text(
            items=DEFAULT_ITEMS,
            lib_path=args.lib,
            output_dir=args.out,
            black_bmp_name=args.black,
            ry_bmp_name=args.ry,
        )
        print("C function returned:", rc)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
