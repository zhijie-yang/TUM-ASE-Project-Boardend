#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from typing import Any, Dict
import logging
import yaml

logger = logging.getLogger(__name__)

BOX_STATUS_REFRESH_RATE = 5
BOX_STATUS_REFRESH_INTERVAL = 1.0 / BOX_STATUS_REFRESH_RATE


class ConfigureReader:
    """Reads and parses YAML configuration file."""

    def __init__(self, file_path: str = "config.yaml"):
        self._file_path = file_path
        self.required_entries = ["name", "id", "password", "address", "backend_url"]
        self._configs = {}  # type: ignore

        self._read_config()
        self._check_entries()

    def _check_entries(self) -> bool:
        for entry in self.required_entries:
            if entry not in self._configs.keys():
                logger.error(
                    "Configuration file {} has no entry {}.".format(  # pylint: disable=logging-format-interpolation
                        self._file_path, entry
                    )
                )
                return False
        return True

    def _read_config(self):
        with open(
            self._file_path, "r", encoding="utf-8"
        ) as f:  # pylint: disable=invalid-name
            self._configs = yaml.safe_load(f)

    def get_configs(self) -> Dict[str, Any]:
        """Returns a copy of the configuration to prevent modifications.

        Returns:
            Dict[str, Any]: Configurations
        """
        return self._configs.copy()

    def get(self, key: str) -> Any:
        """Gets configuration entry value

        Args:
            key (str): Key to query

        Returns:
            Any: Value stored in the configuration file
        """
        return self._configs[key]

    def get_vals(self, keys: list[str]) -> Any:
        """Gets values from configuration file with given keys

        Args:
            keys (list[str]): Keys to query

        Returns:
            Any: Values resp. to keys in the configuration file
        """
        ret = []
        for key in keys:
            ret.append(self._configs[key])
        return ret


def main():  # pylint: disable=missing-function-docstring
    config_reader = ConfigureReader("../config.yaml")
    for k in config_reader.required_entries:
        print("{}: {}".format(k, config_reader.get(k)))
    print(k, config_reader.get_vals(config_reader.required_entries))
    print(config_reader.get_configs())


if __name__ == "__main__":
    main()
