import os
import math

import pygame

from . import config
from . import utility
from .modebase import ModeBase


_screenshot_directory: str
screen_size: tuple[int, int]
_title: str
_window_icon: pygame.Surface | None
_monitor_res: tuple[int, int]
_upscale_max: int
_windowed_flags: int
_fullscreen_flags: int
is_fullscreen: bool
upscale: int
_disp_res: tuple[int, int]
screen: pygame.Surface | None = None
_fullscreen_offset: tuple[int, int] | None
_full_screen: pygame.Surface | None
_disp_screen: pygame.Surface
max_framerate: int = 0


def init(
    screenshot_directory: str,
    screen_size_in: tuple[int, int],
    title: str,
    window_icon: str | None
):
    global _screenshot_directory
    global screen_size
    global _title
    global _window_icon
    global is_fullscreen
    global upscale
    global screen
    global _fullscreen_offset
    global _full_screen
    global _monitor_res
    global _upscale_max
    global _windowed_flags
    global _fullscreen_flags
    if screen:
        raise RuntimeError("error: screen is already set")
    _screenshot_directory = screenshot_directory
    screen_size = screen_size_in
    screen = pygame.Surface(screen_size)
    _title = title
    _window_icon = None
    if window_icon:
        _window_icon = pygame.image.load(window_icon)
    display_info = pygame.display.Info()
    _monitor_res = (
        display_info.current_w,
        display_info.current_h,
    )
    _upscale_max = min(
        _monitor_res[0] // screen_size[0],
        _monitor_res[1] // screen_size[1]
    )
    max_disp_res = (
        screen_size[0] * _upscale_max,
        screen_size[1] * _upscale_max,
    )
    _windowed_flags = 0
    _fullscreen_flags = 0
    if pygame.display.mode_ok(_monitor_res, pygame.FULLSCREEN):
        _fullscreen_flags = pygame.FULLSCREEN
    elif pygame.display.mode_ok(_monitor_res, pygame.NOFRAME):
        _fullscreen_flags = pygame.NOFRAME
    _fullscreen_offset = None
    _full_screen = None
    is_fullscreen = config.get(config.FULLSCREEN)
    upscale = 0
    target_scale = config.get(config.SCREEN_SCALE)
    if target_scale == 0:
        target_scale = math.ceil(_upscale_max / 2)
    set_scale(target_scale)


def set_scale(new_scale: int):
    global upscale
    global screen
    global _disp_res
    new_scale = pygame.math.clamp(new_scale, 1, _upscale_max)
    if new_scale == upscale:
        return
    upscale = new_scale
    _disp_res = (
        screen_size[0] * upscale,
        screen_size[1] * upscale,
    )
    if is_fullscreen:
        _set_fullscreen()
    else:
        pygame.display.quit()
        pygame.display.init()
        _set_windowed()
    screen = screen.convert()
    config.update(config.SCREEN_SCALE, upscale)


def change_scale(scale_change: int):
    set_scale(upscale + scale_change)


def toggle_fullscreen():
    global is_fullscreen
    global screen
    is_fullscreen = not is_fullscreen
    pygame.display.quit()
    pygame.display.init()
    if is_fullscreen:
        _set_fullscreen()
    else:
        _set_windowed()
    screen = screen.convert()
    config.update(config.FULLSCREEN, is_fullscreen)


def _set_windowed():
    global _fullscreen_offset
    global _full_screen
    global _disp_screen
    # center window
    x = (_monitor_res[0] - _disp_res[0]) // 2
    y = (_monitor_res[1] - _disp_res[1]) // 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'
    _fullscreen_offset = None
    _full_screen = None
    _disp_screen = _set_mode(_disp_res, _windowed_flags)


def _set_fullscreen():
    global _fullscreen_offset
    global _full_screen
    global _disp_screen
    _fullscreen_offset = (
        (_monitor_res[0] - _disp_res[0]) // 2,
        (_monitor_res[1] - _disp_res[1]) // 2,
    )
    if _full_screen is None:
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        _full_screen = _set_mode(_monitor_res, _fullscreen_flags)
    else:
        _full_screen.fill((0, 0, 0))
    _disp_screen = pygame.Surface(_disp_res).convert()


def _set_mode(size: tuple[int, int], flags: int):
    global max_framerate
    pygame.display.set_caption(_title)
    if _window_icon:
        pygame.display.set_icon(_window_icon)
    max_framerate = 0
    try:
        return pygame.display.set_mode(size, flags, vsync=1)
    except pygame.error:
        pass
    max_framerate = max(pygame.display.get_desktop_refresh_rates())
    return pygame.display.set_mode(size, flags)


def scale_draw():
    """Scale screen onto display surface, then flip the display."""
    pygame.transform.scale(screen, _disp_res, _disp_screen)
    if is_fullscreen:
        _full_screen.blit(_disp_screen, _fullscreen_offset)
    pygame.display.flip()


def scale_mouse_input(event: pygame.event.Event):
    """Scale mouse position for events in terms of the screen (as opposed to the display surface)."""
    if event.type in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN}:
        if is_fullscreen:
            event_dict = {
                'pos': (
                    (event.pos[0] - _fullscreen_offset[0]) // upscale,
                    (event.pos[1] - _fullscreen_offset[1]) // upscale,
                )
            }
        else:
            event_dict = {
                'pos': (
                    event.pos[0] // upscale,
                    event.pos[1] // upscale,
                )
            }
        if event.type == pygame.MOUSEMOTION:
            event_dict['rel'] = (
                event.rel[0] // upscale,
                event.rel[1] // upscale,
            )
            event_dict['buttons'] = event.buttons
        else:
            event_dict['button'] = event.button
        return pygame.event.Event(event.type, event_dict)
    return event


def is_in_screen(pos: tuple[int, int]):
    return (
        0 <= pos[0] < screen_size[0]
        and 0 <= pos[1] < screen_size[1]
    )


def get_blurred_screen(mode: ModeBase):
    result = pygame.Surface(screen_size).convert()
    mode.draw(result)
    result = pygame.transform.smoothscale(
        result,
        (screen_size[0] * 4 // 5, screen_size[1] * 4 // 5)
    )
    result = pygame.transform.smoothscale(
        result,
        screen_size
    )
    return result


def take_screenshot():
    try:
        os.mkdir(_screenshot_directory)
    except FileExistsError:
        pass
    file_name = f'{utility.get_datetime_file_name()}.png'
    file_path = os.path.join(_screenshot_directory, file_name)
    pygame.image.save(screen, file_path)
