#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from typing import Tuple
from utils.singleton import Singleton


class RfidReader:
    def __init__(self):
        self.reader = SimpleMFRC522()

    def read(self) -> Tuple[int, str]:
        id, text = self.reader.read()
        return id, text


if __name__ == "__main__":
    reader = RfidReader()
    while True:
        try:
            id, text = reader.read()
            print(id, text)
            print(type(id), type(text))
        except KeyboardInterrupt:
            GPIO.cleanup()
            raise
