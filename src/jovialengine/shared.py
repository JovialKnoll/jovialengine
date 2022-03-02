import configparser

import constants
import engineconstants
from fontwrap import FontWrap
from display import Display
from state import State


config = configparser.ConfigParser(engineconstants.CONFIG_DEFAULTS, default_section=engineconstants.CONFIG_SECTION)
config.read(engineconstants.CONFIG_FILE)
for section in config.sections():
    config.remove_section(section)
font_wrap = FontWrap(constants.FONT, constants.FONT_SIZE)
display = Display()
state = State()
game_running = True


def saveConfig():
    with open(engineconstants.CONFIG_FILE, 'w') as file:
        config.write(file, space_around_delimiters=False)
