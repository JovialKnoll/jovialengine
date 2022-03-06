import configparser

import jovialengine

import constants


config = configparser.ConfigParser(jovialengine.engineconstants.CONFIG_DEFAULTS,
                                   default_section=jovialengine.engineconstants.CONFIG_SECTION)
config.read(jovialengine.engineconstants.CONFIG_FILE)
for section in config.sections():
    config.remove_section(section)


def saveConfig():
    with open(jovialengine.engineconstants.CONFIG_FILE, 'w') as file:
        config.write(file, space_around_delimiters=False)
