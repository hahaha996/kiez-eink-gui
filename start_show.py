#
import json 

from remote_data import sensor__get_remote_data, sensor__items_to_textitems
from nina_warning_to_epd import build_text_items_from_warning
from text_on_template_to_c_program import run_epd_with_text




def display_main_page():
    text_items = []
    ## Sensors
    data_by_device = sensor__get_remote_data()
    sensor__text_items = sensor__items_to_textitems(data_by_device)
    text_items += sensor__text_items
    ## Remote warning
    data = {}
    meldung_id = "mow.DE-BR-B-SE017-20250909-17-001"
    with open(f'static/{meldung_id}.json') as f:
        data = json.load(f)
        warning__text_items = build_text_items_from_warning(data)
        text_items += warning__text_items

    run_epd_with_text(items=text_items, black_bmp_name="kiezbox_sensor_black_white.bmp", ry_bmp_name="kiezbox_sensor_red_white.bmp")

def setup_buttons():
    pass





if __name__ == "__main__":
    display_main_page()