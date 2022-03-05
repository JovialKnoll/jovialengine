import configparser

import jovialengine

from .display import Display

import constants
from state import State


config = configparser.ConfigParser(jovialengine.engineconstants.CONFIG_DEFAULTS, default_section=jovialengine.engineconstants.CONFIG_SECTION)
config.read(jovialengine.engineconstants.CONFIG_FILE)
for section in config.sections():
    config.remove_section(section)
font_wrap = jovialengine.fontwrap.FontWrap(constants.FONT, constants.FONT_SIZE)
display = Display()
state = State()
game_running = True


def saveConfig():
    with open(engineconstants.CONFIG_FILE, 'w') as file:
        config.write(file, space_around_delimiters=False)
