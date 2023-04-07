"""
Tests for translation files.
"""
from fnmatch import fnmatch
from os import walk
from os.path import join, dirname

import pytest
from unittest import TestCase

from homeassistant.util.json import load_json

import custom_components.tuya_gateway as root
from custom_components.tuya_gateway.helpers.device_config import (
    available_configs,
    TuyaDeviceConfig,
)


def get_translations():
    translations = join(dirname(root.__file__), "translations")
    for (path, dirs, files) in walk(translations):
        for file in files:
            if fnmatch(file, "*.json"):
                yield load_json(join(path, file))


english = None


def get_english():
    global english
    if english is None:
        translations = join(dirname(root.__file__), "translations", "en.json")
        json = load_json(translations)
        english = json["config"]["step"]["choose_entities"]["data"]

    return english


def get_devices():
    for device in available_configs():
        yield TuyaDeviceConfig(device)


# def subtest_entity_covered(entity):
#     strings = get_english()
#     TestCase().assertIn(
#         entity.config_id,
#         strings,
#         f"{entity._device.config}: {entity.config_id} is missing a translation",
#     )


# @pytest.mark.parametrize("device", get_devices())
# def test_device_covered(device):
#     entity = device.primary_entity
#     if entity.deprecated:
#         subtest_entity_covered(entity)

#     for entity in device.secondary_entities():
#         if entity.deprecated:
#             subtest_entity_covered(entity)
