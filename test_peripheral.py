#!/usr/bin/env python3
from gpiozero import Button, LED
from signal import pause

# BCM pin numbers
button20 = Button(20, pull_up=True, bounce_time=0.2)  # GPIO20
led_red   = LED(26)                                   # GPIO26

button16 = Button(16, pull_up=True, bounce_time=0.2)  # GPIO16
led_green = LED(19)                                   # GPIO19

# For each button:
# - when pressed  -> LED off
# - when released -> print + LED on

def on_release_btn20():
    print("Button 20 (yellow) released!")
    led_red.on()

def on_press_btn20():
    led_red.off()

def on_release_btn16():
    print("Button 16 (lila) released!")
    led_green.on()

def on_press_btn16():
    led_green.off()

button20.when_pressed = on_press_btn20
button20.when_released = on_release_btn20

button16.when_pressed = on_press_btn16
button16.when_released = on_release_btn16

print("Ready. Release a button to turn its LED on (Ctrl+C to quit).")
pause()
