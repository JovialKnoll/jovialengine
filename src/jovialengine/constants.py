import sys
import os


SCREEN_SIZE = (0, 0)
SCREEN_CENTER = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
SCREEN_RECT = pygame.Rect((0, 0), SCREEN_SIZE)
CURSOR_TIME = 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SAVE_EXT = '.sav'

_location = '.'
if getattr(sys, 'frozen', False):
    _location = sys.executable
elif __file__:
    _location = __file__
SRC_DIRECTORY = os.path.dirname(_location)

ASSETS_DIRECTORY = os.path.join(SRC_DIRECTORY, 'assets')
GRAPHICS_DIRECTORY = os.path.join(ASSETS_DIRECTORY, 'gfx')
SOUND_DIRECTORY = os.path.join(ASSETS_DIRECTORY, 'sfx')
TEXT_DIRECTORY = os.path.join(ASSETS_DIRECTORY, 'txt')
VERSION_TEXT = os.path.join(TEXT_DIRECTORY, 'version.txt')

SAVE_DIRECTORY = os.path.join(SRC_DIRECTORY, 'saves')
IMAGE_DIRECTORY = os.path.join(SRC_DIRECTORY, 'images')
SCREENSHOT_DIRECTORY = os.path.join(SRC_DIRECTORY, 'screenshots')

CONFIG_FILE = os.path.join(SRC_DIRECTORY, 'config.ini')
CONFIG_SECTION = 'Game'
CONFIG_MAX_FRAMERATE = 'MaxFramerate'
CONFIG_FULLSCREEN = 'Fullscreen'
CONFIG_SCREEN_SCALE = 'ScreenScale'
CONFIG_DEFAULTS = {
    CONFIG_MAX_FRAMERATE: 1000,
    CONFIG_SCREEN_SCALE: 4,
    CONFIG_FULLSCREEN: False,
}

with open(VERSION_TEXT) as version_file:
    VERSION = version_file.readline().rstrip('\n')
