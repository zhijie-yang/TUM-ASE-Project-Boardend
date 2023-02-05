#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


class Singleton(type):
    """Singleton metaclass base class

    Returns:
        __call__: class singleton instance
    """

    _instances = dict()  # type: ignore

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
