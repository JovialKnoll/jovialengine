import abc
import enum

import pygame

from . import game
from . import display
from . import utility
from .fontwrap import getDefaultFontWrap
from .modebase import ModeBase
from .save import Save
from .saveable import Saveable


class MenuAction(enum.Enum):
    NOTHING = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()
    CONFIRM = enum.auto()
    REJECT = enum.auto()
    QUIT = enum.auto()


class ModeGameMenu(ModeBase, abc.ABC):
    _TEXT_COLOR = (255, 255, 255)
    _BACKGROUND_COLOR = (0, 0, 0)
    _MENU_CHAR_WIDTH = 26
    _SHARED_DISP_TEXT = "Options:\nESC) Go Back\n"

    __slots__ = (
        '_MENU_WIDTH',
        '_previous_mode',
        '_last_disp_text',
        '_menu_surface',
        '_previous_hat',
    )

    def __init__(self, previous_mode: ModeBase, old_screen: pygame.Surface | None = None):
        self._init(display.screen_size)
        self._MENU_WIDTH = getDefaultFontWrap().font.size('_' * self._MENU_CHAR_WIDTH)[0] + 1
        self._previous_mode = previous_mode
        if old_screen is None:
            old_screen = self._getOldScreen()
        self._background = old_screen
        self._last_disp_text: str | None = None
        self._menu_surface: pygame.Surface
        self._previous_hat = (0, 0)

    def _getOldScreen(self):
        return display.getBlurredScreen(self._previous_mode)

    def _getAction(self, event: pygame.event.Event):
        match event.type:
            case pygame.QUIT:
                return MenuAction.QUIT
            case pygame.JOYHATMOTION:
                result = MenuAction.NOTHING
                if event.value[0] == -1 != self._previous_hat[0]:
                    result = MenuAction.LEFT
                elif event.value[0] == 1 != self._previous_hat[0]:
                    result = MenuAction.RIGHT
                elif event.value[1] == 1 != self._previous_hat[1]:
                    result = MenuAction.UP
                elif event.value[1] == -1 != self._previous_hat[1]:
                    result = MenuAction.DOWN
                self._previous_hat = event.value
                return result
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_LEFT:
                        return MenuAction.LEFT
                    case pygame.K_RIGHT:
                        return MenuAction.RIGHT
                    case pygame.K_UP:
                        return MenuAction.UP
                    case pygame.K_DOWN:
                        return MenuAction.DOWN
                    case pygame.K_RETURN:
                        return MenuAction.CONFIRM
                    case pygame.K_ESCAPE:
                        return MenuAction.REJECT
        return MenuAction.NOTHING

    def _drawTextAlways(self, disp_text: str):
        self._last_disp_text = disp_text
        self._menu_surface = getDefaultFontWrap().renderInside(
            self._MENU_WIDTH,
            disp_text,
            self._TEXT_COLOR,
            self._BACKGROUND_COLOR
        )
        self._menu_surface.set_alpha(235)

    def _drawText(self, disp_text: str):
        if self._last_disp_text != disp_text:
            self._drawTextAlways(disp_text)


class ModeGameMenuTop(ModeGameMenu):
    def _inputEvent(self, event):
        if event.type == pygame.QUIT:
            game.getGame().running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_mode = self._previous_mode
            elif event.key == pygame.K_1:
                self.next_mode = ModeGameMenuSave(self._previous_mode, self._background)
            elif event.key == pygame.K_2:
                self.next_mode = ModeGameMenuLoad(self._previous_mode, self._background)
            elif event.key == pygame.K_3:
                self.next_mode = ModeGameMenuOptions(self._previous_mode, self._background)
            elif event.key == pygame.K_4:
                self._stopMixer()
                game.getGame().state = game.getGame().state_cls()
                self._previous_mode = game.getGame().start_mode_cls()
                pygame.mixer.music.pause()
                pygame.mixer.pause()
                self._background = self._getOldScreen()
                self._last_disp_text = None
            elif event.key == pygame.K_5:
                game.getGame().running = False

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += "1) Save\n2) Load\n3) Options\n4) Restart\n5) Quit"
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuSave(ModeGameMenu):
    _CURSOR_TIME = 500

    __slots__ = (
        '_save_name',
        '_cursor_position',
        '_confirm_overwrite',
        '_save_success',
        '_cursor_switch',
        '_cursor_timer',
    )

    def __init__(self, previous_mode, old_screen=None):
        super().__init__(previous_mode, old_screen)
        self._save_name = ''
        self._resetCursorBlink()
        self._cursor_position = 0
        self._confirm_overwrite = False
        self._save_success = None

    def _resetCursorBlink(self):
        self._cursor_switch = True
        self._cursor_timer = 0

    def _inputEvent(self, event):
        match self._getAction(event):
            case MenuAction.QUIT:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case MenuAction.REJECT:
                if self._confirm_overwrite:
                    self._confirm_overwrite = False
                    self._save_success = None
                else:
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case MenuAction.CONFIRM:
                if self._save_success:
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
                elif isinstance(self._previous_mode, Saveable):
                    if not self._save_name:
                        self._save_name = utility.getDateTimeFileName()
                    if Save.willOverwrite(self._save_name) and not self._confirm_overwrite:
                        self._confirm_overwrite = True
                    else:
                        new_save = Save.getFromMode(self._save_name, self._previous_mode)
                        self._save_success = new_save.save()
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_LEFT:
                    self._cursor_position -= 1
                    self._resetCursorBlink()
                case pygame.K_RIGHT:
                    self._cursor_position += 1
                    self._resetCursorBlink()
                case pygame.K_UP | pygame.K_HOME | pygame.K_PAGEUP:
                    self._cursor_position = 0
                    self._resetCursorBlink()
                case pygame.K_DOWN | pygame.K_END | pygame.K_PAGEDOWN:
                    self._cursor_position = len(self._save_name)
                    self._resetCursorBlink()
                case pygame.K_DELETE:
                    self._save_name = self._save_name[:self._cursor_position] \
                        + self._save_name[self._cursor_position + 1:]
                    self._resetCursorBlink()
                case pygame.K_BACKSPACE:
                    self._save_name = self._save_name[:self._cursor_position - 1] \
                        + self._save_name[self._cursor_position:]
                    self._cursor_position -= 1
                    self._resetCursorBlink()
                case _:
                    if (
                        len(self._save_name) < (self._MENU_CHAR_WIDTH - 1)
                        and (
                            # numbers
                            ('0' <= event.unicode <= '9')
                            # or letters
                            or (96 < event.key < 123)
                        )
                    ):
                        self._save_name = self._save_name[:self._cursor_position] \
                            + event.unicode \
                            + self._save_name[self._cursor_position:]
                        self._cursor_position += 1
                        self._resetCursorBlink()
            self._cursor_position = utility.clamp(self._cursor_position, 0, len(self._save_name))

    def _update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer >= self._CURSOR_TIME:
            self._cursor_switch = not self._cursor_switch
            self._cursor_timer -= self._CURSOR_TIME

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        draw_cursor = False
        if not isinstance(self._previous_mode, Saveable):
            disp_text += "\nYou can't save now."
        elif self._save_success:
            disp_text += "\nSaved successfully.\nPress ENTER to continue."
        else:
            disp_text += "ENTER) Save\nType a save name (or leave blank for default):\n>"
            if self._save_name:
                disp_text += self._save_name
            if self._confirm_overwrite and self._save_success is None:
                disp_text += "\nThis will overwrite an existing save." \
                    + "\nPress ENTER again to confirm, or ESC to go back."
            elif self._save_success is False:
                disp_text += "\nSave failed.\nPress ENTER to try again, or ESC to go back."
            else:
                draw_cursor = True
        self._drawTextAlways(disp_text)
        if self._cursor_switch and draw_cursor:
            cursor_x = getDefaultFontWrap().font.size(">" + self._save_name[:self._cursor_position])[0]
            cursor_y = self._menu_surface.get_height() - getDefaultFontWrap().line_height
            self._menu_surface.fill(
                self._TEXT_COLOR,
                (
                    (cursor_x, cursor_y),
                    (1, getDefaultFontWrap().line_height)
                )
            )
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuLoad(ModeGameMenu):
    STATE_DEFAULT = 0
    STATE_LOADED_SAVE = 1
    STATE_DELETED_SAVE = 2
    STATE_CONFIRM_DELETE = 3
    STATE_SELECTED_SAVE = 4
    OPTION_LOAD = 0
    OPTION_DELETE = 1

    __slots__ = (
        '_saves',
        '_save_index',
        '_state',
        '_selected_save_option',
    )

    def __init__(self, previous_mode, old_screen=None):
        super().__init__(previous_mode, old_screen)
        self._saves = Save.getAllFromFiles()
        self._save_index = 0
        self._state = self.STATE_DEFAULT
        self._selected_save_option = self.OPTION_LOAD

    def _inputEvent(self, event):
        action = self._getAction(event)
        if action == MenuAction.NOTHING:
            return
        elif action == MenuAction.QUIT:
            self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            return
        match self._state:
            case self.STATE_DEFAULT:
                if action == MenuAction.REJECT:
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
                elif len(self._saves) > 0:
                    if action in (MenuAction.UP, MenuAction.LEFT):
                        self._save_index -= 1
                    elif action in (MenuAction.DOWN, MenuAction.RIGHT):
                        self._save_index += 1
                    elif action == MenuAction.CONFIRM:
                        self._state = self.STATE_SELECTED_SAVE
                        self._selected_save_option = self.OPTION_LOAD
                    self._save_index = utility.clamp(self._save_index, 0, len(self._saves) - 1)
            case self.STATE_LOADED_SAVE:
                if action == MenuAction.CONFIRM:
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case self.STATE_DELETED_SAVE:
                if action == MenuAction.CONFIRM:
                    self._state = self.STATE_DEFAULT
            case self.STATE_CONFIRM_DELETE:
                if action == MenuAction.CONFIRM:
                    self._saves[self._save_index].delete()
                    del self._saves[self._save_index]
                    self._save_index = utility.clamp(self._save_index, 0, len(self._saves) - 1)
                    self._state = self.STATE_DELETED_SAVE
                elif action == MenuAction.REJECT:
                    self._state = self.STATE_DEFAULT
            case self.STATE_SELECTED_SAVE:
                if action in (MenuAction.UP, MenuAction.LEFT):
                    self._selected_save_option -= 1
                    self._selected_save_option %= 2
                elif action in (MenuAction.DOWN, MenuAction.RIGHT):
                    self._selected_save_option += 1
                    self._selected_save_option %= 2
                elif action == MenuAction.CONFIRM:
                    if self._selected_save_option == self.OPTION_LOAD:
                        self._stopMixer()
                        self._previous_mode = self._saves[self._save_index].load()
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                        self._background = self._getOldScreen()
                        self._state = self.STATE_LOADED_SAVE
                    elif self._selected_save_option == self.OPTION_DELETE:
                        self._state = self.STATE_CONFIRM_DELETE
                elif action == MenuAction.REJECT:
                    self._state = self.STATE_DEFAULT

    def _getLoadOptionsText(self):
        text = "ARROW KEYS + ENTER) Select a save:"
        for i in range(-1, 2):
            text += "\n"
            this_index = self._save_index + i
            if i == 0:
                text += ">"
            else:
                text += "_"
            if 0 <= this_index < len(self._saves):
                text += self._saves[this_index].save_name
        return text

    def _getOptionStatus(self, option: int):
        return ">" if self._selected_save_option == option else "_"

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        match self._state:
            case self.STATE_DEFAULT:
                if len(self._saves) == 0:
                    disp_text += "\nThere are no saves to select from."
                else:
                    disp_text += self._getLoadOptionsText()
            case self.STATE_LOADED_SAVE:
                disp_text += "\nLoaded successfully.\nPress ENTER to continue."
            case self.STATE_DELETED_SAVE:
                disp_text += "\nDeleted successfully.\nPress ENTER to continue."
            case self.STATE_CONFIRM_DELETE:
                disp_text += self._getLoadOptionsText()
                disp_text += "\nAre you sure you want to delete?" \
                    + "\nPress ENTER to confirm, or ESCAPE to go back."
            case self.STATE_SELECTED_SAVE:
                disp_text += self._getLoadOptionsText()
                disp_text += "\nWhat would you like to do? (ARROW KEYS)" \
                    + f"\n{self._getOptionStatus(self.OPTION_LOAD)}Load" \
                    + f"_{self._getOptionStatus(self.OPTION_DELETE)}Delete" \
                    + "\nPress ENTER to select, or ESCAPE to go back."
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuOptions(ModeGameMenu):
    def _getAction(self, event: pygame.event.Event):
        # keydown events will be triggered again on recreating window
        # so for this mode we need to check keyup events instead
        # maybe just replace this with a timeout
        if event.type == pygame.KEYUP:
            match event.key:
                case pygame.K_LEFT:
                    return MenuAction.LEFT
                case pygame.K_RIGHT:
                    return MenuAction.RIGHT
                case pygame.K_UP:
                    return MenuAction.UP
                case pygame.K_DOWN:
                    return MenuAction.DOWN
                case pygame.K_RETURN:
                    return MenuAction.CONFIRM
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return MenuAction.REJECT
            return MenuAction.NOTHING
        return super()._getAction(event)

    def _inputEvent(self, event):
        match self._getAction(event):
            case MenuAction.QUIT | MenuAction.REJECT:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case MenuAction.LEFT | MenuAction.DOWN:
                display.changeScale(-1)
            case MenuAction.RIGHT | MenuAction.UP:
                display.changeScale(1)
            case MenuAction.CONFIRM:
                display.toggleFullscreen()
        if event.type == pygame.KEYDOWN and '1' <= event.unicode <= '9':
            target_scale = int(event.unicode)
            display.setScale(target_scale)

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += f"ARROWS) Upscaling: {display.upscale}" \
            + f"\nENTER) Fullscreen: {self.getTickBox(display.is_fullscreen)}"
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))

    @staticmethod
    def getTickBox(value: bool):
        inside = "*" if value else "_"
        return f"[{inside}]"
