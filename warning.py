import requests, json
from text_on_template_to_c_program import run_epd_with_text

import unicodedata

GERMAN_MAP = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    "ß": "ss",
})

def german_to_ascii(text: str) -> str:
    # First apply German-specific transliteration
    text = text.translate(GERMAN_MAP)
    # Then strip any remaining accents/diacritics safely
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")

MELDUNG_ID = "biw.BIWAPP-90480_NGRjZTkwNzI3NzRkZTBmNA"
url = f'https://nina.api.proxy.bund.dev/api31/warnings/{MELDUNG_ID}.json'

resp = requests.get(url=url, params={})
data = resp.json()

inner__y_distance = 20
outer__y_distance = 90
from__y = 320

text_items = []

i = 1
text_items.append({
    "text": "Headline: " + german_to_ascii(data["info"][0]["headline"]),
    "box": [40, from__y + i * inner__y_distance, 999, 999],
    "size": 20,
    "color": "red",
    "style": "bold",
})
i += 2

text_items.append({
    "text": "Category: " + german_to_ascii(data["info"][0]["category"][0]),
    "box": [40, from__y + i * inner__y_distance, 999, 999],
    "size": 16,
    "color": "black",
    "style": "bold",
})
i += 1

text_items.append({
    "text": "Sent by " + german_to_ascii(data["sender"]) + " at " + data["sent"],
    "box": [40, from__y + i * inner__y_distance, 999, 999],
    "size": 16,
    "color": "black",
    "style": "bold",
})
i += 1

text_items.append({
    "text": german_to_ascii(data["info"][0]["area"][0]["areaDesc"]),
    "box": [40, from__y + i * inner__y_distance, 999, 999],
    "size": 16,
    "color": "black",
    "style": "bold",
})
i += 1

text_items.append({
    "text": "ID: " + data["identifier"],
    "box": [40, from__y + i * inner__y_distance, 999, 999],
    "size": 16,
    "color": "black",
    "style": "bold",
})
i += 1

text_items.append({
    "text": "Description: " + german_to_ascii(data["info"][0]["description"]).replace("<br>", "\n").replace("&nbsp;", "").replace("\n", " ")[:300],
    "box": [40, from__y + i * inner__y_distance, 999, 999],
    "size": 16,
    "color": "black",
    "style": "bold",
})
i += 1


print(text_items)
if (data["info"][0]["category"][0] == "Safety"):
    print("Plotting as " + data["info"][0]["category"][0])
    run_epd_with_text(items=text_items, black_bmp_name="hochwasser_black_white.bmp", ry_bmp_name="hochwasser_red_white.bmp")
else:
    run_epd_with_text(items=text_items, black_bmp_name="blank_black_white.bmp", ry_bmp_name="blank_red_white.bmp")