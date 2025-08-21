from img_helper import *

FONT_PATH_1 = "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf"
# items = [
#     ("Pers�nliche Vorsorge", (15, 300, 900, 330)),
#     ("Essen und Trinken", (15, 350, 900, 380)),
#     ("Langer Beispieltext der automatisch umbricht und m�glichst nicht �berl�uft.",
#      (15, 385, 900, 430)),
# ]
# codes = draw_text_boxes(
#     image_path="/home/pi/kiezbox-ha/img_templates/prevent_massnahme_template.png",
#     font_path="/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf",
#     base_font_size=28,
#     items=items,
#     color=(0,0,0),
#     min_font_size=10,
#     line_spacing=0.15,
#     padding=6,
#     align="left",
#     output_path="texted.png"  # saves as banner_with_text.png
# )
# print(codes)  # {0: 0, 1: 0, 2: 1} (example)



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
        "text": "This line won't wrap and may be clipped.",
        "box": (15, 385, 900, 430),
        "font_path": FONT_PATH_1,
        "size": 10,
        "color": (0, 0, 0),
        "align": "left",
        "valign": "top",
    },
]

codes = draw_text_boxes_fixed(
    image_path="/home/pi/kiezbox-ha/img_templates/prevent_massnahme_template.png",
    items=items,
    output_path="texted.png"  # saves as banner_with_text.png
)
print(codes)  # e.g., {0: 0, 1: 0, 2: 1}  (2 was clipped)
