#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from rfid_manager.reader import RfidReader

if __name__ == "__main__":
    reader = RfidReader()
    print(reader.read())
