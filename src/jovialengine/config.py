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
config = configparser.ConfigParser(CONFIG_DEFAULTS, default_section=CONFIG_SECTION)
config.read(constants.CONFIG_FILE)
for section in config.sections():
    config.remove_section(section)


def saveConfig():
    with open(constants.CONFIG_FILE, 'w') as file:
        config.write(file, space_around_delimiters=False)
