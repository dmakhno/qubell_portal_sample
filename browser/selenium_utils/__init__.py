"""
This module provides common utilities, and have no specific implementations.
Some of the code was borrowed from https://github.com/wiredrive/wtframework
"""
import logging
import os

import yaml


logger = logging.getLogger("selenium_utils")


def read_utils_config(config_file_location):
    env_prefix = "wd_"

    def read_from_file():
        with open(config_file_location, 'r') as config_yaml:
            return yaml.load(config_yaml)

    def flatten_dict(d, result={}, prv_keys=[]):
        for k, v in d.iteritems():
            if isinstance(v, dict):
                flatten_dict(v, result, prv_keys + [k])
            else:
                result['_'.join(prv_keys + [k])] = v
        return result

    configs = read_from_file()
    env_config = {k[len(env_prefix):]: v for k, v in os.environ.iteritems() if k.startswith(env_prefix)}
    yml_config = flatten_dict(configs)
    yml_config.update(env_config)  # override values from env
    return yml_config