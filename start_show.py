#
import json 
from signal import pause
import threading
import queue
import time
import signal
import sys
from enum import Enum

from remote_data import sensor__get_remote_data, sensor__items_to_textitems
from nina_warning_to_epd import build_text_items_from_warning
from text_on_template_to_c_program import run_epd_with_text
from button import setup_buttons

# --- thread plumbing ---
_stop = threading.Event()
_devices_q: "queue.Queue[tuple]" = queue.Queue()

DEFAULT_BTN20 = 20
DEFAULT_LED_RED = 26
DEFAULT_BTN16 = 16
DEFAULT_LED_GREEN = 19

eink_busy_flag = threading.Event()


class EinkTopic(Enum):
    SLIDE0 = 0
    SLIDE1 = 1
    SLIDE2 = 2
    SLIDE3 = 3
    SLIDE4 = 4
    MAIN = 9
current_topic: EinkTopic = EinkTopic.MAIN


def display_main_page():
    global current_topic
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

    print(f"Plotting {len(text_items)} Textbausteine!")
    # run_epd_with_text(items=text_items, black_bmp_name="kiezbox_sensor_black_white.bmp", ry_bmp_name="kiezbox_sensor_red_white.bmp")
    current_topic = EinkTopic.MAIN

def switch_topic(target_topic: EinkTopic = None):
    global current_topic
    print("Switching topic. Current: " + str(current_topic))

    if target_topic == EinkTopic.MAIN:
        display_main_page()
    # TODO: switch to slidex. By default: next.
    else:
        if current_topic == EinkTopic.MAIN:
            current_topic = EinkTopic.SLIDE0
        else:
            next_topic = (current_topic.value + 1) % (len(EinkTopic) - 1)
            current_topic = EinkTopic(next_topic) 
    print("New topic: " + str(current_topic))

def on_red():
    # Sloppy check for concurrency:
    if not eink_busy_flag.is_set():
        print(">> red action")
        switch_topic()
    else:
        print("Eink is busy. Ignore.")

def on_green():
    print(">> green action")

def buttons_worker(eink_busy_flag: threading.Event):
    # Create buttons/LEDs on this thread
    devices = setup_buttons(
        btn20_pin=DEFAULT_BTN20,
        led_red_pin=DEFAULT_LED_RED,
        btn16_pin=DEFAULT_BTN16,
        led_green_pin=DEFAULT_LED_GREEN,
        bounce_time=0.2,
        eink_busy_flag=eink_busy_flag,
        red_callback=on_red,
        green_callback=on_green,
    )
    # Hand the tuple (btn20, led_red, btn16, led_green) to the main thread
    _devices_q.put(devices)

    print("Buttons initiated!")

    # Keep this thread alive so gpiozero's callbacks remain active
    # (no busy loop; sleep until asked to stop)
    while not _stop.is_set():
        _stop.wait(1.0)
    

if __name__ == "__main__":
    # display_main_page()

    # Start worker as a daemon (exits with the main program)
    t = threading.Thread(target=buttons_worker, args=(eink_busy_flag,), daemon=True)
    t.start()

    # Retrieve the created devices so they don't get GC'd
    btn20, led_red, btn16, led_green = _devices_q.get()

    # --- optional: clean shutdown handling ---
    def _shutdown(*_args):
        print("Shutting down...")
        _stop.set()
        # give worker a moment to exit
        t.join(timeout=2.0)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)   # Ctrl+C
    signal.signal(signal.SIGTERM, _shutdown)  # system stop

    # Your main loop can keep doing other work here
    time.sleep(5)
    eink_busy_flag.set()
    try:
        while True:
            # ... other tasks ...
            time.sleep(0.5)
    except KeyboardInterrupt:
        _shutdown()