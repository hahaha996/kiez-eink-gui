"""nina_warning_to_epd

Fetch a NINA warning by ID, build E-Paper display text items, and render them
using `run_epd_with_text` from `text_on_template_to_c_program`.

This module can be imported (use `render_warning_epd(...)`) or executed
directly as a script.
"""
from __future__ import annotations

import argparse
import html
import logging
import os
import re
import sys
import json
from typing import Any, Dict, List

import requests
from requests import Response

# Import your existing renderer
from text_on_template_to_c_program import run_epd_with_text
from datetime import datetime

# -----------------------------
# Configuration & Constants
# -----------------------------
API_BASE = os.environ.get("NINA_API_BASE", "https://nina.api.proxy.bund.dev/api31")
DEFAULT_TIMEOUT = float(os.environ.get("NINA_TIMEOUT", "10"))
DEFAULT_MELDUNG_ID = os.environ.get(
    "NINA_MELDUNG_ID",
    "biw.BIWAPP-90480_NGRjZTkwNzI3NzRkZTBmNA",
)
MAX_DESCRIPTION_LEN = int(os.environ.get("NINA_MAX_DESC_LEN", "300"))

# Layout constants
INNER_Y_DISTANCE = 20
OUTER_Y_DISTANCE = 90  # kept for compatibility; not used directly here
FROM_Y = 200

# German transliteration map
GERMAN_MAP = str.maketrans(
    {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }
)


# -----------------------------
# Utilities
# -----------------------------
import unicodedata


def german_to_ascii(text: str) -> str:
    """Transliterate German characters to ASCII.

    - Applies German-specific transliterations (�?ae, �?ss, ...)
    - Strips any remaining diacritics safely
    """
    text = (text or "").translate(GERMAN_MAP)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def _http_get(url: str, *, timeout: float = DEFAULT_TIMEOUT) -> Response:
    """HTTP GET with basic error handling."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp


def _clean_html_to_text(s: str) -> str:
    """Convert simple HTML-ish content to plain text.

    - Unescape HTML entities (&nbsp;, &amp;, ...)
    - Replace <br> / <br/> with newlines
    - Remove other tags conservatively
    - Collapse whitespace
    """
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<\s*br\s*/?\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", " ", s)  # strip any other tags
    s = re.sub(r"\s+", " ", s).strip()
    return s


# -----------------------------
# Core builders
# -----------------------------

def fetch_warning(meldung_id: str) -> Dict[str, Any]:
    """Fetch a warning object by its ID from the NINA API."""
    url = f"{API_BASE}/warnings/{meldung_id}.json"          # Live 
    url = f"{API_BASE}/archive/alerts/{meldung_id}?contentType=json"    # Archieve
    
    logging.debug("Fetching warning: %s", url)
    resp = _http_get(url)
    return resp.json()


def build_text_items_from_warning(data: Dict[str, Any], *,
                                  from_y: int = FROM_Y,
                                  inner_y_distance: int = INNER_Y_DISTANCE,
                                  max_description_len: int = MAX_DESCRIPTION_LEN) -> List[Dict[str, Any]]:
    """Build the list of text item dicts expected by `run_epd_with_text`.

    The function is defensive against missing keys in the API response.
    """
    def safe_get(path: List[Any], default: str = "") -> str:
        cur: Any = data
        try:
            for p in path:
                if isinstance(p, int):
                    cur = cur[p]
                else:
                    cur = cur.get(p)  # type: ignore[assignment]
            if cur is None:
                return default
            return str(cur)
        except (KeyError, IndexError, TypeError):
            return default

    i = 1
    items: List[Dict[str, Any]] = []

    headline = german_to_ascii(safe_get(["info", 0, "headline"]))
    if headline:
        items.append(
            {
                "text": f"Headline: {headline}",
                "box": [450, from_y + i * inner_y_distance, 999, 999],
                "size": 20,
                "color": "red",
                "style": "bold",
            }
        )
        i += 4

    category = german_to_ascii(safe_get(["info", 0, "category", 0]))
    if category:
        items.append(
            {
                "text": f"Category: {category}",
                "box": [450, from_y + i * inner_y_distance, 999, 999],
                "size": 16,
                "color": "black",
                "style": "bold",
            }
        )
        i += 1
    # .strftime("%H:%M:%S %d:%m:%Y")
    sender = german_to_ascii(safe_get(["sender"]))
    sent = datetime.fromisoformat(safe_get(["sent"])).strftime("%H:%M:%S %d:%m:%Y")

    if sender or sent:
        items.append(
            {
                "text": f"Sent by {sender} at {sent}".strip(),
                "box": [450, from_y + i * inner_y_distance, 999, 999],
                "size": 16,
                "color": "black",
                "style": "bold",
            }
        )
        i += 1

    area_desc = german_to_ascii(safe_get(["info", 0, "area", 0, "areaDesc"]))
    if area_desc:
        items.append(
            {
                "text": area_desc,
                "box": [450, from_y + i * inner_y_distance, 999, 999],
                "size": 16,
                "color": "black",
                "style": "bold",
            }
        )
        i += 1

    identifier = safe_get(["identifier"])
    if identifier:
        items.append(
            {
                "text": f"ID: {identifier}",
                "box": [450, from_y + i * inner_y_distance, 999, 999],
                "size": 16,
                "color": "black",
                "style": "bold",
            }
        )
        i += 2

    raw_desc = safe_get(["info", 0, "description"]) or ""
    cleaned = _clean_html_to_text(raw_desc)
    desc = german_to_ascii(cleaned)[:max_description_len]
    if desc:
        items.append(
            {
                "text": f"Description: {desc}",
                "box": [450, from_y + i * inner_y_distance, 999, 999],
                "size": 16,
                "color": "black",
                "style": "bold",
            }
        )
        i += 1

    return items


# -----------------------------
# Public orchestration
# -----------------------------

def render_warning_epd(
    *,
    meldung_id: str = DEFAULT_MELDUNG_ID,
    use_local_json: bool = False,
    black_bmp_name: str | None = None,
    ry_bmp_name: str | None = None,
    fallback_black_bmp: str = "blank_black_white.bmp",
    fallback_ry_bmp: str = "blank_red_white.bmp",
) -> List[Dict[str, Any]]:
    """Fetch the warning, build items, and render via `run_epd_with_text`.

    Returns the list of items used for rendering (useful for testing).
    """
    if use_local_json:
        with open(f'static/{meldung_id}.json') as f:
            data = json.load(f)
    else:
        data = fetch_warning(meldung_id)

    items = build_text_items_from_warning(data)
    print(items)
    exit()
    # Choose template by category if available
    category = (
        (data.get("info") or [{}])[0].get("category") or [""]
    )[0] if isinstance(data, dict) else ""

    if not black_bmp_name or not ry_bmp_name:
        if category == "Safety":
            black_bmp_name = black_bmp_name or "kiezbox_sensor_black_white.bmp"
            ry_bmp_name = ry_bmp_name or "kiezbox_sensor_black_white.bmp"
        else:
            black_bmp_name = black_bmp_name or fallback_black_bmp
            ry_bmp_name = ry_bmp_name or fallback_ry_bmp

    logging.info("Rendering category %s using %s / %s", category, black_bmp_name, ry_bmp_name)
    run_epd_with_text(items=items, black_bmp_name=black_bmp_name, ry_bmp_name=ry_bmp_name)
    return items


# -----------------------------
# CLI
# -----------------------------

def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render a NINA warning on an E-Paper display.")
    p.add_argument("meldung_id", nargs="?", default=DEFAULT_MELDUNG_ID, help="Warning (Meldung) ID")
    p.add_argument(
        "--use-local-json",
        dest="use_local_json",
        action="store_true",
        help="Use local JSON file from the static folder instead of fetching from API",
    )    
    p.add_argument("--black-bmp", dest="black_bmp", default=None, help="Path to black/white BMP template")
    p.add_argument("--ry-bmp", dest="ry_bmp", default=None, help="Path to red/white BMP template")
    p.add_argument(
        "--log-level", default=os.environ.get("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = _parse_args(argv or sys.argv[1:])
    logging.basicConfig(level=getattr(logging, ns.log_level), format="%(levelname)s: %(message)s")
    print(ns)
    try:
        items = render_warning_epd(
            meldung_id=ns.meldung_id,
            use_local_json=ns.use_local_json,
            black_bmp_name=ns.black_bmp,
            ry_bmp_name=ns.ry_bmp,
        )
        # Print for visibility / debugging when run as a script
        print(items)
        return 0
    except requests.HTTPError as e:
        logging.error("HTTP error: %s", e)
        return 2
    except requests.RequestException as e:
        logging.error("Network error: %s", e)
        return 3
    except Exception as e:  # keep last-resort guard in CLI mode
        logging.exception("Unexpected error: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
