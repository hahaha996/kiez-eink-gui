from img_helper import *
from helpers import *
from splitter import *
from pathlib import Path
import os
import subprocess
import ctypes


allowed_size = [8, 12, 16, 20, 24]

items = [
  {
    "text": "CBRN-Gefahrenstoffe",
    "box": [40, 320, 820, 345],
    "size": 20,
    "color": "red",
    "style": "bold"
  },
  {
    "text": "Die unterschiedlichen Gefahrenstoffe",
    "box": [40, 355, 820, 370],
    "size": 16,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Ein Laie kann in der Regel die Gefaehrlichkeit von chemischen (C), biologischen (B),  radiologischen (R) und nuklearen (N) Gefahrenstoffen nicht erkennen.",
    "box": [40, 375, 820, 410],
    "size": 12,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "Wirkung auf Haut und Koerper",
    "box": [40, 420, 820, 440],
    "size": 16,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Verhalten bei Gefahrenstoff-Freisetzung. Kontaktieren Sie die lokale Giftnotrufzentrale.",
    "box": [40, 445, 820, 470],
    "size": 12, 
    "color": "black",
    "style": "normal"
  },
  {
    "text": "Giftnotruf der Charite Universitaetsmedizin Berlin:",
    "box": [40, 470, 650, 495],
    "size": 12,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "030 192 40",
    "box": [468, 470, 820, 495],
    "size": 12,
    "color": "red",
    "style": "bold"
  },
  {
    "text": "Verhalten zu Hause",
    "box": [40, 500, 820, 520],
    "size": 16,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Bleiben Sie im Gebaeude, schliessen Sie Fenster und Tueren. Schalten Sie Ventilatoren und  Lueftungen aus. Vermeiden Sie unnoetigen Sauerstoffverbrauch durch Kerzen oder aehnliches. Bei radioaktiven Stoffen: suchen Sie einen Kellerraum auf",
    "box": [40, 525, 820, 580],
    "size": 12,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "Verhalten im Auto oder im Freien",
    "box": [40, 590, 820, 615],
    "size": 16,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Bewegen Sie sich moeglichst quer zur Windrichtung. Atmen Sie moeglichst durch einen Atemschutz, zumindest durch ein Taschentuch. Waschen Sie Haende, Gesicht und Haare, ebenso Nase und Ohren mit Wasser und Seife. Bei biologischen Stoffen: desinfizieren Sie Ihre Haende zusaetzlich.",
    "box": [40, 620, 820, 670],
    "size": 12,
    "color": "black",
    "style": "normal"
  }
]

# Obsoleted
FONT_MAP = {
    "normal": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf",
    "bold": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Bold.ttf",
    "italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Italic.ttf",
    "bold-italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-BoldItalic.ttf",
}
COLOR_MAP = {"black": (0,0,0), "red": (255,0,0), "white": (255,255,255)}

BASE_DIR = Path(__file__).resolve().parent
ORIGIN_DIR = BASE_DIR / "origin"
OUTPUT_DIR = BASE_DIR / "ready_to_use"

#############
# load the shared library .so
lib = ctypes.CDLL("./c-eink-project/libepd13in3b.so")

class TextItem(ctypes.Structure):
    _fields_ = [
        ("text",   ctypes.c_char_p),     # const char*
        ("box",    ctypes.c_int * 4),    # int[4]
        ("color",  ctypes.c_char_p),     # "red" or "black"
        ("size",    ctypes.c_int),       # int[4]

    ]

lib.print_something.argtypes = ()
lib.print_something.restype = None
lib.print_something()

# Declare the function signature
lib.kiezbox_EPD_13in3b_with_text.argtypes = [
     ctypes.c_char_p,                   # black_bmp_path
     ctypes.c_char_p,                   # ry_bmp_path
     ctypes.POINTER(TextItem),          # text_items (array decays to pointer)
     ctypes.c_int                       # count
]
lib.kiezbox_EPD_13in3b_with_text.restype =  ctypes.c_int

items_for_c = []
for item in items:
  size = item["size"]
  items_for_c.append(TextItem(
    text=bytes(item["text"], "utf-8"),
    box=(ctypes.c_int * 4)(item["box"][0], item["box"][1], item["box"][2], item["box"][3]),
    color=bytes(item["color"], "utf-8"),
    size=size if size in allowed_size else allowed_size[0]
  ))
  # break

# Build a C array of TextItem[2]
ArrayType = TextItem * len(items_for_c)
items_for_c = ArrayType(*items_for_c)

# prepare parameters
black_path = b"/home/pi/kiezbox-ha/ready_to_use/vorsorge_black_white.bmp"   # must be bytes
ry_path = b"/home/pi/kiezbox-ha/ready_to_use/vorsorge_red_white.bmp"

# call the function
result = lib.kiezbox_EPD_13in3b_with_text(black_path, ry_path, items_for_c, len(items_for_c))
print("C function returned:", result)

