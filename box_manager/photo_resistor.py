import RPi.GPIO as GPIO
import time
from utils.singleton import Singleton

PIN_PHOTO_RESISTOR = 13


class PhotoResistor():
    def __init__(self, pin_photo_resistor: int = PIN_PHOTO_RESISTOR):
        self._pin_photo_resistor = pin_photo_resistor

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_PHOTO_RESISTOR, GPIO.IN)

    def _read_sensor(self):
        return GPIO.input(self._pin_photo_resistor)

    def is_closed(self) -> bool:
        """Returns whether the box lid is closed

        Returns:
            bool: result
        """
        # TODO find the correct way to measure the photo resistor
        return self._read_sensor() < 1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        GPIO.cleanup()


def main():  # pylint: disable=missing-function-docstring
    with PhotoResistor() as pr:  # pylint: disable=invalid-name
        while True:
            val = pr.is_closed
            print(val)
            time.sleep(1)


if __name__ == '__main__':
    main()
