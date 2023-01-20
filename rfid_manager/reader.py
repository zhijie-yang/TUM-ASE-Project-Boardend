#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from typing import Tuple, Optional
from mfrc522 import SimpleMFRC522
from utils.manager_base import ManagerBase


class RfidReader(ManagerBase):
    """Type annotated RFID reader class

    Should always be used as `with RfidReader() as reader` to ensure clean exit

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """

    def __init__(self):
        self.reader = SimpleMFRC522()

    def blocked_read(self) -> Tuple[int, str]:
        """Reads any tag once. Blocks when no card is read.

        Returns:
            Tuple[int, str]: the uid and the text in the tag
        """
        return self.reader.read()

    def read(self) -> Tuple[Optional[int], Optional[str]]:
        """Reads any tag. Returns id == None if no card presents.

        Returns:
            Tuple[Opeional[int], Optional[str]]: the uid and the text in
            the tag. None for no card presents.
        """
        return self.reader.read_no_block()

    def write(self, text: str) -> None:
        """Writes any tag once

        Args:
            text (str): text to be writen
        """
        self.reader.write(text)


def main():
    """Main function for testing"""
    with RfidReader() as reader:
        while True:
            tag_id, tag_text = reader.read()
            print(tag_id, tag_text)


if __name__ == "__main__":
    main()
