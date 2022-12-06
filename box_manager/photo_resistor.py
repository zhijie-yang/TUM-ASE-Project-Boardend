import RPi.GPIO as GPIO
import time

PIN_PHOTO_RESISTOR = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(PIN_PHOTO_RESISTOR, GPIO.IN)

try:
    while True:
        val = GPIO.input(PIN_PHOTO_RESISTOR)
        print(val)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
