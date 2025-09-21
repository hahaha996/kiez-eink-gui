#!/usr/bin/env python3
"""
button_led_release.py

Behavior:
- Buttons use internal pull-ups (wire each button to its GPIO and GND).
- While pressed: corresponding LED is OFF.
- On release: print a message and turn the LED ON.
- On normal exit: LEDs are turned OFF and GPIOs are closed.

Usage:
  python button_led_release.py
  # or customize pins:
  python button_led_release.py --btn20 20 --led-red 26 --btn16 16 --led-green 19
"""

from __future__ import annotations

import atexit
import threading
import argparse
from signal import pause
from typing import Tuple

from gpiozero import Button, LED

# Defaults (BCM numbering)
DEFAULT_BTN20 = 20
DEFAULT_LED_RED = 26
DEFAULT_BTN16 = 16
DEFAULT_LED_GREEN = 19

IS_LED_GREEN_ON = False
IS_LED_RED_ON = False

led_red = None
led_green = None

def turn_red_on():
    global led_red
    global IS_LED_RED_ON
    led_red.on()
    IS_LED_RED_ON = True

def turn_red_off():
    global led_red
    global IS_LED_RED_ON
    led_red.off()
    IS_LED_RED_ON = False

def turn_green_on():
    global led_green
    global IS_LED_GREEN_ON
    led_green.on()
    IS_LED_GREEN_ON = True

def turn_green_off():
    global led_green
    global IS_LED_GREEN_ON
    led_green.off()
    IS_LED_GREEN_ON = False

def setup_buttons(
    *,
    btn20_pin: int = DEFAULT_BTN20,
    led_red_pin: int = DEFAULT_LED_RED,
    btn16_pin: int = DEFAULT_BTN16,
    led_green_pin: int = DEFAULT_LED_GREEN,
    bounce_time: float = 0.2,
    eink_busy_flag: threading.Event,
    red_callback = None,
    green_callback = None,
) -> Tuple[Button, LED, Button, LED]:
    """Create devices, attach handlers, and register cleanup. Returns (btn20, led_red, btn16, led_green)."""
    global led_red
    global led_green
    try:
        btn20 = Button(btn20_pin, pull_up=True, bounce_time=bounce_time)
        led_red = LED(led_red_pin)

        btn16 = Button(btn16_pin, pull_up=True, bounce_time=bounce_time)
        led_green = LED(led_green_pin)
    except Exception as e:
        print("Failed init button: ", e)
        # TODO: handle error in main thread
        return None, None, None, None

    # Handlers
    def on_release_btn20() -> None:
        print(f"Button {btn20_pin} (yellow) released!")
        red_callback()
        # global IS_LED_RED_ON
        # global IS_LED_GREEN_ON
        # if not eink_busy_flag.is_set():
        #     if not IS_LED_RED_ON:
        #         led_red.on()
        #     else:
        #         led_red.off()
        #     IS_LED_RED_ON = not IS_LED_RED_ON
        #     if red_callback != None:
        #         print("Calling callback red_callback ...")
        #         red_callback()
        # else:
        #     print("Button released but eink busy. Ignore.")

    def on_release_btn16() -> None:
        global IS_LED_RED_ON
        global IS_LED_GREEN_ON
        print(f"Button {btn16_pin} (lila) released!")
        if not IS_LED_GREEN_ON:
            led_green.on()
        else:
            led_green.off() 
        IS_LED_GREEN_ON = not IS_LED_GREEN_ON
        if green_callback != None:
            print("Calling callback green_callback ...")
            green_callback()

    def on_press_btn20() -> None:
        led_red.off()
    def on_press_btn16() -> None:
        led_green.off() 
    btn20.when_pressed = on_press_btn20
    btn16.when_pressed = on_press_btn16

    btn20.when_released = on_release_btn20
    btn16.when_released = on_release_btn16

    # Ensure LEDs off and close on exit
    def tidy() -> None:
        try:
            led_red.off()
            led_green.off()
        finally:
            led_red.close()
            led_green.close()
            btn20.close()
            btn16.close()

    atexit.register(tidy)   # without this the buton will not work!

    return btn20, led_red, btn16, led_green


def run(
    *,
    btn20_pin: int = DEFAULT_BTN20,
    led_red_pin: int = DEFAULT_LED_RED,
    btn16_pin: int = DEFAULT_BTN16,
    led_green_pin: int = DEFAULT_LED_GREEN,
    bounce_time: float = 0.2,
) -> None:
    """Convenience runner: sets up devices and blocks until Ctrl+C."""
    setup_buttons(
        btn20_pin=btn20_pin,
        led_red_pin=led_red_pin,
        btn16_pin=btn16_pin,
        led_green_pin=led_green_pin,
        bounce_time=bounce_time,
    )
    print("Ready. Release a button to turn its LED on (Ctrl+C to quit).")
    pause()  # keep the script running


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Buttons trigger LEDs on release (gpiozero, BCM numbering).")
    p.add_argument("--btn20", type=int, default=DEFAULT_BTN20, help="BCM pin for button 20 (default: 20)")
    p.add_argument("--led-red", type=int, default=DEFAULT_LED_RED, help="BCM pin for red LED (default: 26)")
    p.add_argument("--btn16", type=int, default=DEFAULT_BTN16, help="BCM pin for button 16 (default: 16)")
    p.add_argument("--led-green", type=int, default=DEFAULT_LED_GREEN, help="BCM pin for green LED (default: 19)")
    p.add_argument("--bounce", type=float, default=0.2, help="Debounce time in seconds (default: 0.2)")
    return p.parse_args()


def main() -> int:
    ns = _parse_args()
    run(
        btn20_pin=ns.btn20,
        led_red_pin=ns.led_red,
        btn16_pin=ns.btn16,
        led_green_pin=ns.led_green,
        bounce_time=ns.bounce,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
