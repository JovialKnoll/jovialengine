import configparser

from . import config

import constants


CONFIG_SECTION = 'Game'
CONFIG_MAX_FRAMERATE = 'MaxFramerate'
CONFIG_FULLSCREEN = 'Fullscreen'
CONFIG_SCREEN_SCALE = 'ScreenScale'
CONFIG_DEFAULTS = {
    CONFIG_MAX_FRAMERATE: 1000,
    CONFIG_SCREEN_SCALE: 4,
    CONFIG_FULLSCREEN: False,
}
config = configparser.ConfigParser(config.CONFIG_DEFAULTS, default_section=config.CONFIG_SECTION)
config.read(constants.CONFIG_FILE)
for section in config.sections():
    config.remove_section(section)


def saveConfig():
    with open(constants.CONFIG_FILE, 'w') as file:
        config.write(file, space_around_delimiters=False)
