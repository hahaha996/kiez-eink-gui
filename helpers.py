#





import asyncio
from enum import Enum

counter: int = 0
counter_lock = asyncio.Lock()
stop_event = asyncio.Event()

eink_lock = asyncio.Lock()

# async def increment_counter():
#     async with state.counter_lock:     # wait until lock is free
#         state.counter += 1
#         return state.counter

# async def reset_counter():
#     async with state.counter_lock:
#         state.counter = 0

# --- Long-term background worker ---
async def long_term_worker():
    try:
        while not stop_event.is_set():
            # Your repeated work here
            print("Background worker: doing some work...")
            await gen_eink_show()
            await asyncio.sleep(5)   # e.g. poll, update, etc.
    except asyncio.CancelledError:
        print("Background worker: cancelled, cleaning up…")
        raise

class EinkTopic(Enum):
    SLIDE0 = 0
    SLIDE1 = 1
    SLIDE2 = 2
    SLIDE3 = 3
    SLIDE4 = 4
    MAIN = 5

DEFAULT_BTN20 = 20
DEFAULT_LED_RED = 26
DEFAULT_BTN16 = 16
DEFAULT_LED_GREEN = 19

FONT_MAP = {
    "normal": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Regular.ttf",
    "bold": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Bold.ttf",
    "italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-Italic.ttf",
    "bold-italic": "/home/pi/kiezbox-ha/Roboto_Mono/static/RobotoMono-BoldItalic.ttf",
}
FONT_MAP = {
    "normal": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
    "bold": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
    "italic": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
    "bold-italic": "/home/pi/kiezbox-ha/fonts/ProFontWindows.ttf",
}
COLOR_MAP = {"black": (0,0,0), "red": (255,0,0), "white": (255,255,255)}
TEMP_DIR = "/home/pi/kiezbox-ha/temp/"
TEMPLATE_DIR = "/home/pi/kiezbox-ha/img_templates/"
EPD_EXE_PATH = "/home/pi/kiezbox-ha/c-eink-project/epd"
EPD_MODE = "kiezbox_epd13in3b"

current_topic: EinkTopic = EinkTopic.MAIN

# By default, only iterate over SLIDEx. ONE_TIME is set only once, after that it starts from over.
async def gen_eink_show():
    global current_topic
    print("Current topic: " + str(current_topic))
    async with eink_lock:
        if current_topic == EinkTopic.ONE_TIME:
            current_topic = EinkTopic.SLIDE0
        else:
            next_topic = (current_topic.value + 1) % (len(EinkTopic) - 1)
            current_topic = EinkTopic(next_topic) 