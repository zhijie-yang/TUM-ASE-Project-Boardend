import time
import RPi.GPIO as GPIO
from utils.singleton import Singleton  # pylint: disable=import-error

PIN_PHOTO_RESISTOR = 13


class PhotoResistor(metaclass=Singleton):
    """Photo resistor manager class, running as a singleton"""

    def __init__(self, pin_photo_resistor: int = PIN_PHOTO_RESISTOR):
        self._pin_photo_resistor = pin_photo_resistor

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(PIN_PHOTO_RESISTOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _read_sensor(self):
        return GPIO.input(self._pin_photo_resistor)

    def is_closed(self) -> bool:
        """Returns whether the box lid is closed

        Returns:
            bool: result
        """
        return self._read_sensor() == 1

    def is_opened(self) -> bool:
        """Returns whether the box lid is opened

        Returns:
            bool: result
        """
        return not self.is_closed()

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


if __name__ == "__main__":
    main()
