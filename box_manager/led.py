import RPi.GPIO as GPIO

import time

PIN_LED_GREEN = 11
PIN_LED_RED = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(PIN_LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PIN_LED_RED, GPIO.OUT, initial=GPIO.LOW)

def light_led(pin, sec=0.1):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(sec)
    GPIO.output(pin, GPIO.LOW)

try:
    while True:
        print("start")
        # time.sleep(4)
        light_led(PIN_LED_GREEN)
        # time.sleep(4)
        light_led(PIN_LED_RED)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
