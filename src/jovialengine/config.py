import configparser

import constants


CONFIG_MAX_FRAMERATE = 'MaxFramerate'
CONFIG_FULLSCREEN = 'Fullscreen'
CONFIG_SCREEN_SCALE = 'ScreenScale'
_DEFAULTS = {
    CONFIG_MAX_FRAMERATE: 1000,
    CONFIG_SCREEN_SCALE: 0,
    CONFIG_FULLSCREEN: False,
}
_SECTION = 'Game'
_TYPES = {
    CONFIG_MAX_FRAMERATE: 'int',
    CONFIG_SCREEN_SCALE: 'int',
    CONFIG_FULLSCREEN: 'bool',
}
_config = configparser.ConfigParser(_DEFAULTS, default_section=_SECTION)
_config.read(constants.CONFIG_FILE)
for section in _config.sections():
    _config.remove_section(section)


def get(key: str):
    key_type = _TYPES.get(key)
    if key_type == 'int':
        return _config.getint(_SECTION, key)
    elif key_type == 'bool':
        return _config.getboolean(_SECTION, key)
    return _config.get(_SECTION, key)


def update(key: str, value):
    _config.set(_SECTION, key, str(value))


def save():
    with open(constants.CONFIG_FILE, 'w') as file:
        _config.write(file, space_around_delimiters=False)
