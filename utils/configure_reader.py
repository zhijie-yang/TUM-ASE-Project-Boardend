#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import yaml
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ConfigureReader():
    def __init__(self, file_path: str = 'config.yaml'):
        self._file_path = file_path
        self.required_entries = ['name', 'id', 'address']
        self._configs = {}  # type: ignore

        self._read_config()
        self._check_entries()

    def _check_entries(self):
        for entry in self.required_entries:
            if entry not in self._configs.keys():
                logger.error("Configuration file {} has no entry {}.".format(  # pylint: disable=logging-format-interpolation, consider-using-f-string
                    self._file_path, entry))
                return False

    def _read_config(self):
        with open(self._file_path, 'r', encoding='utf-8') as f:  # pylint: disable=invalid-name
            self._configs = yaml.safe_load(f)

    def get_configs(self) -> Dict[str, Any]:
        """ Returns a copy of the configuration to prevent modifications.

        Returns:
            Dict[str, Any]: Configurations
        """
        return self._configs.copy()

    def get(self, key: str) -> Any:
        return self._configs[key]

    def get_vals(self, keys: list[str]) -> Any:
        ret = []
        for key in keys:
            ret.append(self._configs[key])
        return ret


def main():
    config_reader = ConfigureReader('../config.yaml')
    for k in config_reader.required_entries:
        print('{}: {}'.format(k, config_reader.get(k)))
    print(k, config_reader.get_vals(config_reader.required_entries))
    print(config_reader.get_configs())


if __name__ == '__main__':
    main()
