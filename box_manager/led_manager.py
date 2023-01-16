import time
import RPi.GPIO as GPIO
from utils.singleton import Singleton

PIN_LED_GREEN = 11
PIN_LED_RED = 12


class LedManager(metaclass=Singleton):
    def __init__(self, pin_green: int = PIN_LED_GREEN, pin_red: int = PIN_LED_RED):
        self._pin_green = pin_green
        self._pin_red = pin_red

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_LED_RED, GPIO.OUT, initial=GPIO.LOW)

    def _turn_on(self, pin: int):
        GPIO.output(pin, GPIO.HIGH)

    def _turn_off(self, pin: int):
        GPIO.output(pin, GPIO.LOW)

    def light_led_with_seconds(self, pin: int, sec: float):  # pylint: disable=missing-function-docstring
        self._turn_on(pin)
        time.sleep(sec)
        self._turn_off(pin)

    def turn_on_red(self):  # pylint: disable=missing-function-docstring
        self._turn_on(self._pin_red)

    def turn_on_green(self):  # pylint: disable=missing-function-docstring
        self._turn_on(self._pin_green)

    def turn_off_red(self):  # pylint: disable=missing-function-docstring
        self._turn_off(self._pin_red)

    def turn_off_green(self):  # pylint: disable=missing-function-docstring
        self._turn_off(self._pin_green)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        GPIO.cleanup()


def main():
    with LedManager() as led:
        while True:
            print("start")
            led.turn_on_green()
            time.sleep(0.5)
            led.turn_off_green()
            led.turn_on_red()
            time.sleep(0.5)
            led.turn_off_red()


if __name__ == '__main__':
    main()
