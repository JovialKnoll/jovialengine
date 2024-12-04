import configparser

import pygame


FULLSCREEN = 'Fullscreen'
SCREEN_SCALE = 'ScreenScale'
_SECTION = 'Game'
_defaults: dict
_config: configparser.ConfigParser
_config_file: str | None = None


def init(config_file: str):
    global _defaults
    global _config
    global _config_file
    _defaults = {
        SCREEN_SCALE: 0,
        FULLSCREEN: False,
    }
    _config = configparser.ConfigParser(_defaults, default_section=_SECTION)
    if _config_file:
        raise RuntimeError("error: _config_file is already set")
    _config_file = config_file
    _config.read(_config_file)
    for section in _config.sections():
        _config.remove_section(section)


def get(key: str):
    match _defaults.get(key):
        case bool():
            return _config.getboolean(_SECTION, key)
        case int():
            return _config.getint(_SECTION, key)
        case _:
            return _config.get(_SECTION, key)


def update(key: str, value):
    _config.set(_SECTION, key, str(value))


def save():
    with open(_config_file, 'w') as file:
        _config.write(file, space_around_delimiters=False)
