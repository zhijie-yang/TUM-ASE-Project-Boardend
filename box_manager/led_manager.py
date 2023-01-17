import time
from typing import Dict
import logging
import RPi.GPIO as GPIO
from utils.singleton import Singleton

logger = logging.getLogger(__name__)

PIN_LED_GREEN = 11
PIN_LED_RED = 12


class LedManager(metaclass=Singleton):
    def __init__(self, pin_green: int = PIN_LED_GREEN, pin_red: int = PIN_LED_RED):
        self._pin_green = pin_green
        self._pin_red = pin_red
        self._leds_on: Dict[int, bool] = {
            self._pin_green: False, self._pin_red: False}

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(PIN_LED_RED, GPIO.OUT, initial=GPIO.LOW)

    def _turn_on(self, pin: int):
        if self._get_led_status(pin):
            logger.error(
                "Turning LED {} ON while it is already ON.".format(  # pylint: disable=logging-format-interpolation, consider-using-f-string
                    pin
                )
            )
        GPIO.output(pin, GPIO.HIGH)
        self._leds_on[pin] = True

    def _turn_off(self, pin: int):
        if not self._get_led_status(pin):
            logger.error(
                "Turning LED {} OFF while it is already OFF.".format(  # pylint: disable=logging-format-interpolation, consider-using-f-string
                    pin
                )
            )
        GPIO.output(pin, GPIO.LOW)
        self._leds_on[pin] = False

    def _get_led_status(self, pin: int):
        return self._leds_on[pin]

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

    def get_status_red(self) -> bool:  # pylint: disable=missing-function-docstring
        return self._get_led_status(self._pin_red)

    def get_status_green(self) -> bool:  # pylint: disable=missing-function-docstring
        return self._get_led_status(self._pin_green)

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
