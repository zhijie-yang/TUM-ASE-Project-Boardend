#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import time
import os
import logging
import argparse
import ast
import sys

from box_manager.box_manager import BoxManager
from utils.configure_reader import BOX_STATUS_REFRESH_INTERVAL


def main():  # pylint: disable=missing-function-docstring
    with BoxManager() as manager:
        manager.start()
        while True:
            manager.routine_loop()
            time.sleep(BOX_STATUS_REFRESH_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ASE Project Boardend Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--background",
        type=ast.literal_eval,
        dest="background",
        required=False,
        default=False,
        help="Whether code runs in background, affects logging scheme.",
    )

    parser.add_argument(
        "--log",
        type=str,
        dest="log_path",
        required=False,
        default="/tmp/board.log",
        help="log path",
    )

    args = vars(parser.parse_args(sys.argv[1:]))

    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
    if args["background"]:
        logging.basicConfig(
            level=LOGLEVEL,
            format="[%(asctime)s] [%(levelname)s] %(filename)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filename=args["log_path"],
            filemode="a",
        )

    else:
        logging.basicConfig(
            level=os.environ.get("LOGLEVEL", "DEBUG").upper(),
            format="[%(asctime)s] [%(levelname)s] %(filename)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    main()
