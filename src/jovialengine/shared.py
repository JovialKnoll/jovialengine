import configparser

import jovialengine

import constants


config = configparser.ConfigParser(jovialengine.config.CONFIG_DEFAULTS,
                                   default_section=jovialengine.config.CONFIG_SECTION)
config.read(constants.CONFIG_FILE)
for section in config.sections():
    config.remove_section(section)


def saveConfig():
    with open(constants.CONFIG_FILE, 'w') as file:
        config.write(file, space_around_delimiters=False)
