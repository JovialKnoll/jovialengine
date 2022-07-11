import configparser

import constants


CONFIG_SECTION = 'Game'
CONFIG_MAX_FRAMERATE = 'MaxFramerate'
CONFIG_FULLSCREEN = 'Fullscreen'
CONFIG_SCREEN_SCALE = 'ScreenScale'
CONFIG_DEFAULTS = {
    CONFIG_MAX_FRAMERATE: 1000,
    CONFIG_SCREEN_SCALE: 0,
    CONFIG_FULLSCREEN: False,
}
_CONFIG_TYPES = {
    CONFIG_MAX_FRAMERATE: 'int',
    CONFIG_SCREEN_SCALE: 'int',
    CONFIG_FULLSCREEN: 'bool',
}
_config = configparser.ConfigParser(CONFIG_DEFAULTS, default_section=CONFIG_SECTION)
_config.read(constants.CONFIG_FILE)
for section in _config.sections():
    _config.remove_section(section)


def get(key: str):
    key_type = _CONFIG_TYPES.get(key)
    if key_type == 'int':
        return _config.getint(CONFIG_SECTION, key)
    elif key_type == 'bool':
        return _config.getboolean(CONFIG_SECTION, key)
    return _config.get(CONFIG_SECTION, key)


def update(key: str, value):
    _config.set(CONFIG_SECTION, key, str(value))


def save():
    with open(constants.CONFIG_FILE, 'w') as file:
        _config.write(file, space_around_delimiters=False)
