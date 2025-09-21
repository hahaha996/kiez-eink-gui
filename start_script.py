#
import json 
from signal import pause
import threading
import queue
import time
import signal
import sys
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import subprocess

from helpers import *
from img_helper import draw_text_boxes_fixed, draw_text_boxes_rgba, draw_text_boxes_1bit_mono
from splitter import spit_red_black

from remote_data import sensor__get_remote_data, sensor__items_to_textitems
from nina_warning_to_epd import build_text_items_from_warning
from text_on_template_to_c_program import run_epd_with_text
from button import setup_buttons, turn_red_on, turn_red_off, turn_green_on, turn_green_off
from gen_slide import *

# --- thread plumbing ---
_stop = threading.Event()
_devices_q: "queue.Queue[tuple]" = queue.Queue()

# DEFAULT_BTN20 = 20
# DEFAULT_LED_RED = 26
# DEFAULT_BTN16 = 16
# DEFAULT_LED_GREEN = 19

# FONT_MAP = {
#     "normal": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf",
#     "bold": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Bold.ttf",
#     "italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Italic.ttf",
#     "bold-italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-BoldItalic.ttf",
# }
# FONT_MAP = {
#     "normal": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
#     "bold": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
#     "italic": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
#     "bold-italic": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
# }
# COLOR_MAP = {"black": (0,0,0), "red": (255,0,0), "white": (255,255,255)}
# OUTDIR = "/home/pi/kiezbox-ha/temp/"

eink_busy_flag = threading.Event()

def run_once_in_thread(text_items):
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(
            run_epd_with_text,
            items=text_items,
            black_bmp_name="kiezbox_sensor_black_white.bmp",
            ry_bmp_name="kiezbox_sensor_red_white.bmp",
        )
        # wait (optionally add a timeout, e.g. 30s)
        return fut.result(timeout=None)  # or timeout=30

# from enum import Enum

# class EinkTopic(Enum):
#     SLIDE0 = 0
#     SLIDE1 = 1
#     SLIDE2 = 2
#     SLIDE3 = 3
#     SLIDE4 = 4
#     MAIN = 5

topics = [e.value for e in EinkTopic]
# current_topic: EinkTopic = EinkTopic.MAIN


# def run_epd(TOOL_CMD: str, mode: str, black_bmp: str, ry_bmp: str):
#     cmd = [TOOL_CMD, mode, str(black_bmp), str(ry_bmp)]
#     try:
#         print(cmd)
#         code = subprocess.run(cmd)
#     except Exception as e:
#         print("Error running cmd: " + e)

# def display_main_page():
#     print("IN display_main_page!")
#     return
#     global current_topic
#     text_items = []
#     ## Sensors
#     data_by_device = sensor__get_remote_data()
#     sensor__text_items = sensor__items_to_textitems(data_by_device)
#     text_items += sensor__text_items
#     ## Remote warning
#     data = {}
#     meldung_id = "mow.DE-BR-B-SE017-20250909-17-001"
#     with open(f'static/{meldung_id}.json') as f:
#         data = json.load(f)
#         warning__text_items = build_text_items_from_warning(data)
#         text_items += warning__text_items

#     print(f"Plotting MAIN: Textbausteine len={len(text_items)}!")
#     current_topic = EinkTopic.MAIN

#     processed_items_bw = []
#     processed_items_rw = []
#     for item in text_items:
#         try:
#             text = item["text"]
#             x1,y1,x2,y2 = item["box"]
#             size = int(item["size"])
#             color = COLOR_MAP.get(item.get("color","black"), (0,0,0))
#             style = item.get("style","normal").lower()
#             font_path = FONT_MAP.get(style, FONT_MAP["normal"])
#             processed_item = {
#                 "text": text,
#                 "box": (x1,y1,x2,y2),
#                 "font_path": font_path,
#                 "size": size,
#                 "color": color,
#                 "align": "left",
#                 "valign": "top",
#             }
#             if item.get("color","black") == "black":
#                 processed_items_bw.append(processed_item)
#             else:
#                 processed_items_rw.append(processed_item)
#         except Exception:
#             # ignore malformed entries per your spec
#             continue
#     print("plotting ...")
#     outdir = "/home/pi/kiezbox-ha/temp/"
#     # texted_img_path = outdir + "texted__kiezbox_sensor.png"
#     draw_text_boxes_1bit_mono(
#         image_path="/home/pi/kiezbox-ha/ready_to_use/kiezbox_sensor_black_white.bmp",
#         items=processed_items_bw,
#         output_path=outdir + "texted__kiezbox_sensor__bw.bmp"
#     )
#     draw_text_boxes_1bit_mono(
#         image_path="/home/pi/kiezbox-ha/ready_to_use/kiezbox_sensor_red_white.bmp",
#         items=processed_items_rw,
#         output_path=outdir + "texted__kiezbox_sensor__rw.bmp"
#     )

#     run_epd(
#         "/home/pi/kiezbox-ha/c-eink-project/epd", "kiezbox_epd13in3b", 
#         outdir + "texted__kiezbox_sensor__bw.bmp",
#         outdir + "texted__kiezbox_sensor__rw.bmp"
#     )

def switch_topic(target_topic: EinkTopic = None, dry_run: bool = False):
    """ By default jump to next topic. If target_topic, then show it """
    global current_topic
    print("Switching topic. Current: " + str(current_topic))
    if eink_busy_flag.is_set():
        print("Eink busy. Return")
    else:
        eink_busy_flag.set()
        if target_topic != None:
            run__slide(target_topic, TEMP_DIR, dry_run)
        else:
            next_topic = (current_topic.value + 1) % len(EinkTopic)
            current_topic = EinkTopic(next_topic)
            if current_topic == EinkTopic.MAIN or current_topic.value > 5:
                print("Back to main. Turn led off")
                # eink_busy_flag.set()
                turn_red_off()
                run__slide(current_topic, TEMP_DIR, dry_run)
                # eink_busy_flag.clear()
            else:
                turn_red_on()
                # eink_busy_flag.set()
                print("slide: ",current_topic.value)
                run__slide(current_topic, TEMP_DIR, dry_run)
                # eink_busy_flag.clear()
        eink_busy_flag.clear()
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
        bounce_time=0.1,
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
    print("########################### App starting up ...")
    global current_topic
    current_topic = EinkTopic.MAIN
    run__slide(current_topic, TEMP_DIR)

    #### ONLY for thread
    # # Start worker as a daemon (exits with the main program)
    # t = threading.Thread(target=buttons_worker, args=(eink_busy_flag,), daemon=True)
    # t.start()
    # # Retrieve the created devices so they don't get GC'd
    # btn20, led_red, btn16, led_green = _devices_q.get()

    btn20, led_red, btn16, led_green = setup_buttons(
        btn20_pin=DEFAULT_BTN20,
        led_red_pin=DEFAULT_LED_RED,
        btn16_pin=DEFAULT_BTN16,
        led_green_pin=DEFAULT_LED_GREEN,
        bounce_time=0.1,
        eink_busy_flag=eink_busy_flag,
        red_callback=on_red,
        green_callback=on_green,
    )
    print("Init button returns: ", btn20, led_red, btn16, led_green)

    #### ONLY for thread
    # # --- optional: clean shutdown handling ---
    # def _shutdown(*_args):
    #     print("Shutting down...")
    #     _stop.set()
    #     # give worker a moment to exit
    #     t.join(timeout=2.0)
    #     sys.exit(0)

    # signal.signal(signal.SIGINT, _shutdown)   # Ctrl+C
    # signal.signal(signal.SIGTERM, _shutdown)  # system stop

    # Your main loop can keep doing other work here
    # time.sleep(15)
    # eink_busy_flag.set()

    try:
        while True:
            # ... other tasks ...
            time.sleep(10)
            if not eink_busy_flag.is_set():
                if current_topic != EinkTopic.MAIN:
                    print("### Period task: Keep current topic: ", current_topic)
                    continue
                print("### Period task: start updating MAIN page.")
                switch_topic(EinkTopic.MAIN)
                print("### Period task: DONE updating MAIN page.")
            
    except KeyboardInterrupt:
        print("### Shutting down ...")
        # _shutdown()