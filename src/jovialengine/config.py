import configparser


MAX_FRAMERATE = 'MaxFramerate'
FULLSCREEN = 'Fullscreen'
SCREEN_SCALE = 'ScreenScale'
_DEFAULTS = {
    MAX_FRAMERATE: 1000,
    SCREEN_SCALE: 0,
    FULLSCREEN: False,
}
_TYPES = {
    MAX_FRAMERATE: 'int',
    SCREEN_SCALE: 'int',
    FULLSCREEN: 'bool',
}
_SECTION = 'Game'
_config = configparser.ConfigParser(_DEFAULTS, default_section=_SECTION)
_config_file: str


def init(config_file: str):
    global _config_file
    _config_file = config_file
    _config.read(_config_file)
    for section in _config.sections():
        _config.remove_section(section)


def get(key: str):
    match _TYPES.get(key):
        case 'int':
            return _config.getint(_SECTION, key)
        case 'bool':
            return _config.getboolean(_SECTION, key)
        case _:
            return _config.get(_SECTION, key)


def update(key: str, value):
    _config.set(_SECTION, key, str(value))


def save():
    with open(_config_file, 'w') as file:
        _config.write(file, space_around_delimiters=False)
