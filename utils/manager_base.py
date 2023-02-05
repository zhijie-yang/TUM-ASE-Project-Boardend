import RPi.GPIO as GPIO
from utils.singleton import Singleton


class ManagerBase(metaclass=Singleton):
    """Singleton manager base class. Implements enter and exit methods
    to make sure GPIO is cleaned up upon destruction.
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        GPIO.cleanup()
