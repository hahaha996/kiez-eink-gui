from img_helper import *

FONT_PATH_1 = "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf"

items = [
    {
        "text": "Persönliche Vorsorge",
        "box": (15, 300, 900, 330),
        "font_path": FONT_PATH_1,
        "size": 28,
        "color": "#000000",
        "align": "left",
        "valign": "top",
    },
    {
        "text": "Essen und Trinken",
        "box": (15, 350, 900, 380),
        "font_path": FONT_PATH_1,
        "size": 22,
        "color": (255, 0, 0),
        "align": "left",
        "valign": "top",
    },
    {
        "text": "This line won't wrap and may be clipped sdffdxf.",
        "box": (15, 385, 900, 430),
        "font_path": FONT_PATH_1,
        "size": 10,
        "color": (0, 0, 0),
        "align": "left",
        "valign": "top",
    },
]

items = [
  {
    "text": "CBRN-Gefahrenstoffe",
    "box": [40, 320, 820, 345],
    "size": 22,
    "color": "red",
    "style": "bold"
  },
  {
    "text": "Die unterschiedlichen Gefahrenstoffe",
    "box": [40, 355, 820, 370],
    "size": 15,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Ein Laie kann in der Regel die Gefährlichkeit von chemischen (C), biologischen (B),  radiologischen (R) und nuklearen (N) Gefahrenstoffen nicht erkennen.",
    "box": [40, 375, 820, 410],
    "size": 14,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "Wirkung auf Haut und Körper",
    "box": [40, 420, 820, 440],
    "size": 15,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Verhalten bei Gefahrenstoff-Freisetzung. Kontaktieren Sie die lokale Giftnotrufzentrale.",
    "box": [40, 445, 820, 470],
    "size": 14,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "Giftnotruf der Charité Universitätsmedizin Berlin:",
    "box": [40, 470, 650, 495],
    "size": 14,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "030 192 40",
    "box": [468, 470, 820, 495],
    "size": 14,
    "color": "red",
    "style": "bold"
  },
  {
    "text": "Verhalten zu Hause",
    "box": [40, 500, 820, 520],
    "size": 15,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Bleiben Sie im Gebäude, schließen Sie Fenster und Türen. Schalten Sie Ventilatoren und  Lüftungen aus. Vermeiden Sie unnötigen Sauerstoffverbrauch durch Kerzen oder Ähnliches. Bei radioaktiven Stoffen: suchen Sie einen Kellerraum auf",
    "box": [40, 525, 820, 580],
    "size": 14,
    "color": "black",
    "style": "normal"
  },
  {
    "text": "Verhalten im Auto oder im Freien",
    "box": [40, 590, 820, 615],
    "size": 15,
    "color": "black",
    "style": "bold"
  },
  {
    "text": "Bewegen Sie sich möglichst quer zur Windrichtung. Atmen Sie möglichst durch einen Atemschutz, zumindest durch ein Taschentuch. Waschen Sie Hände, Gesicht und Haare, ebenso Nase und Ohren mit Wasser und Seife. Bei biologischen Stoffen: desinfizieren Sie Ihre Hände zusätzlich.",
    "box": [40, 620, 820, 670],
    "size": 14,
    "color": "black",
    "style": "normal"
  }
]

FONT_MAP = {
    "normal": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf",
    "bold": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Bold.ttf",
    "italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Italic.ttf",
    "bold-italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-BoldItalic.ttf",
}
COLOR_MAP = {"black": (0,0,0), "red": (255,0,0), "white": (255,255,255)}

processed_items: List[Dict] = []
for it in items:
    try:
        text = it["text"]
        x1,y1,x2,y2 = it["box"]
        size = int(it["size"])
        color = COLOR_MAP.get(it.get("color","black"), (0,0,0))
        style = it.get("style","normal").lower()
        font_path = FONT_MAP.get(style, FONT_MAP["normal"])
        processed_items.append({
            "text": text,
            "box": (x1,y1,x2,y2),
            "font_path": font_path,
            "size": size,
            "color": color,
            "align": "left",
            "valign": "top",
        })
    except Exception:
        # ignore malformed entries per your spec
        continue

codes = draw_text_boxes_fixed(
    image_path="/home/pi/kiezbox-ha/img_templates/prevent_massnahme_template.png",
    items=processed_items,
    output_path="texted.png"  # saves as banner_with_text.png
)
print(codes)  # e.g., {0: 0, 1: 0, 2: 1}  (2 was clipped)
