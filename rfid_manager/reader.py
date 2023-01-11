#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from typing import Tuple
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from utils.singleton import Singleton


class RfidReader(metaclass=Singleton):
    """Type annotated RFID reader class

    Should always be used as `with RfidReader() as reader` to ensure clean exit

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """

    def __init__(self):
        self.reader = SimpleMFRC522()

    def read(self) -> Tuple[int, str]:
        """Reads any tag once

        Returns:
            Tuple[int, str]: the uid and the text in the tag
        """
        return self.reader.read()

    def write(self, text: str) -> None:
        """Writes any tag once

        Args:
            text (str): text to be writen
        """
        self.reader.write(text)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        GPIO.cleanup()


def main():
    """Main function for testing"""
    with RfidReader() as reader:
        while True:
            tag_id, tag_text = reader.read()
            print(tag_id, tag_text)


if __name__ == "__main__":
    main()
