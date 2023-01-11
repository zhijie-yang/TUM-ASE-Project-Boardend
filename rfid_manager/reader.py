#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from typing import Tuple
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from utils.singleton import Singleton


class RfidReader(metaclass=Singleton):
    """Type annotated RFID reader class

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


def main():
    """Main function for testing"""
    reader = RfidReader()
    while True:
        try:
            tag_id, tag_text = reader.read()
            print(tag_id, tag_text)
        except KeyboardInterrupt:
            GPIO.cleanup()
            raise


if __name__ == "__main__":
    main()
