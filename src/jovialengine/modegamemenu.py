import abc
import enum
import string

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
            case pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    return MenuAction.CONFIRM
                else:
                    return MenuAction.REJECT
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

    @staticmethod
    def _getSelectedChar(is_selected: bool):
        return ">" if is_selected else "_"

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


class ModeGameMenuList(ModeGameMenu):
    __slots__ = (
        '_index',
    )

    def __init__(self, previous_mode, old_screen):
        super().__init__(previous_mode, old_screen)
        self._index = 0

    def _getOptionsLength(self) -> int:
        raise NotImplementedError(
            type(self).__name__ + "._getOptionsLength(self)"
        )

    def _getOptionName(self, index: int) -> str:
        raise NotImplementedError(
            type(self).__name__ + "._getOptionName(self, index)"
        )

    def _getOptionsText(self):
        text = "ARROW KEYS + ENTER) Select a save:"
        for i in range(-1, 2):
            text += "\n"
            this_index = self._index + i
            text += ">" if i == 0 else "_"
            if 0 <= this_index < self._getOptionsLength():
                text += self._getOptionName(this_index)
        return text


class ModeGameMenuTop(ModeGameMenu):
    _OPTIONS = [
        "Save",
        "Load",
        "Options",
        "Restart",
        "Quit",
    ]

    __slots__ = (
        '_selected',
    )

    def __init__(self, previous_mode, old_screen=None):
        super().__init__(previous_mode, old_screen)
        self._selected = 0

    def _inputEvent(self, event):
        match self._getAction(event):
            case MenuAction.QUIT:
                game.getGame().running = False
            case MenuAction.REJECT:
                self.next_mode = self._previous_mode
            case MenuAction.UP | MenuAction.LEFT:
                self._selected -= 1
            case MenuAction.DOWN | MenuAction.RIGHT:
                self._selected += 1
            case MenuAction.CONFIRM:
                match self._selected:
                    case 0:
                        self.next_mode = ModeGameMenuSave(self._previous_mode, self._background)
                    case 1:
                        self.next_mode = ModeGameMenuLoad(self._previous_mode, self._background)
                    case 2:
                        pressed_return = event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                        self.next_mode = ModeGameMenuOptions(self._previous_mode, self._background, pressed_return)
                    case 3:
                        self._stopMixer()
                        game.getGame().state = game.getGame().state_cls()
                        self._previous_mode = game.getGame().start_mode_cls()
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                        self._background = self._getOldScreen()
                        self._last_disp_text = None
                    case 4:
                        game.getGame().running = False
        self._selected = utility.clamp(self._selected, 0, 4)

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += "ARROW KEYS + ENTER)"
        for index, option in enumerate(self._OPTIONS):
            disp_text += "\n"
            disp_text += self._getSelectedChar(self._selected == index)
            disp_text += option
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuSave(ModeGameMenu):
    _CONTROLLER_CHARS = string.ascii_lowercase + string.digits
    _CURSOR_TIME = 500

    __slots__ = (
        '_save_name',
        '_cursor_position',
        '_confirm_overwrite',
        '_save_success',
        '_cursor_switch',
        '_cursor_timer',
    )

    def __init__(self, previous_mode, old_screen):
        super().__init__(previous_mode, old_screen)
        self._save_name = ''
        self._resetCursorBlink()
        self._cursor_position = 0
        self._confirm_overwrite = False
        self._save_success = None

    def _resetCursorBlink(self):
        self._cursor_switch = True
        self._cursor_timer = 0

    def _controllerType(self, direction: int):
        if self._cursor_position == len(self._save_name):
            if self._cursor_position < (self._MENU_CHAR_WIDTH - 1):
                char_pos = max(direction - 1, -1)
                self._save_name += self._CONTROLLER_CHARS[char_pos]
                self._resetCursorBlink()
        else:
            char_pos = self._CONTROLLER_CHARS.find(
                self._save_name[self._cursor_position].lower()
            )
            new_char_pos = (char_pos + direction) % len(self._CONTROLLER_CHARS)
            self._save_name = self._save_name[:self._cursor_position] \
                + self._CONTROLLER_CHARS[new_char_pos] \
                + self._save_name[self._cursor_position + 1:]

    def _backspace(self):
        self._save_name = self._save_name[:self._cursor_position - 1] + self._save_name[self._cursor_position:]
        self._cursor_position -= 1
        self._resetCursorBlink()

    def _inputEvent(self, event):
        match self._getAction(event):
            case MenuAction.QUIT:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case MenuAction.REJECT:
                if self._confirm_overwrite:
                    self._confirm_overwrite = False
                    self._save_success = None
                elif event.type == pygame.JOYBUTTONDOWN and self._cursor_position > 0:
                    self._backspace()
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
            case MenuAction.LEFT:
                self._cursor_position -= 1
                self._resetCursorBlink()
            case MenuAction.RIGHT:
                self._cursor_position += 1
                self._resetCursorBlink()
            case MenuAction.UP:
                if event.type == pygame.JOYHATMOTION:
                    self._controllerType(-1)
            case MenuAction.DOWN:
                if event.type == pygame.JOYHATMOTION:
                    self._controllerType(1)
        if event.type == pygame.KEYDOWN:
            match event.key:
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
                    self._backspace()
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


class ModeGameMenuLoad(ModeGameMenuList):
    STATE_DEFAULT = 0
    STATE_LOADED_SAVE = 1
    STATE_DELETED_SAVE = 2
    STATE_SELECTED_SAVE = 3
    OPTION_LOAD = 0
    OPTION_DELETE = 1

    __slots__ = (
        '_saves',
        '_state',
        '_selected_save_option',
    )

    def __init__(self, previous_mode, old_screen):
        super().__init__(previous_mode, old_screen)
        self._saves = Save.getAllFromFiles()
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
                match action:
                    case MenuAction.REJECT:
                        self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
                    case MenuAction.UP | MenuAction.LEFT:
                        self._index -= 1
                    case MenuAction.DOWN | MenuAction.RIGHT:
                        self._index += 1
                    case MenuAction.CONFIRM:
                        if len(self._saves) > 0:
                            self._state = self.STATE_SELECTED_SAVE
                            self._selected_save_option = self.OPTION_LOAD
                self._index = utility.clamp(self._index, 0, len(self._saves) - 1)
            case self.STATE_LOADED_SAVE:
                if action in (MenuAction.CONFIRM, MenuAction.REJECT):
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case self.STATE_DELETED_SAVE:
                if action in (MenuAction.CONFIRM, MenuAction.REJECT):
                    self._state = self.STATE_DEFAULT
            case self.STATE_SELECTED_SAVE:
                match action:
                    case MenuAction.UP | MenuAction.LEFT:
                        self._selected_save_option -= 1
                        self._selected_save_option %= 2
                    case MenuAction.DOWN | MenuAction.RIGHT:
                        self._selected_save_option += 1
                        self._selected_save_option %= 2
                    case MenuAction.CONFIRM:
                        if self._selected_save_option == self.OPTION_LOAD:
                            self._stopMixer()
                            self._previous_mode = self._saves[self._index].load()
                            pygame.mixer.music.pause()
                            pygame.mixer.pause()
                            self._background = self._getOldScreen()
                            self._state = self.STATE_LOADED_SAVE
                        elif self._selected_save_option == self.OPTION_DELETE:
                            self._saves[self._index].delete()
                            del self._saves[self._index]
                            self._index = utility.clamp(self._index, 0, len(self._saves) - 1)
                            self._state = self.STATE_DELETED_SAVE
                    case MenuAction.REJECT:
                        self._state = self.STATE_DEFAULT

    def _getOptionsLength(self):
        return len(self._saves)

    def _getOptionName(self, index):
        return self._saves[index].save_name

    def _getOptionStatus(self, option: int):
        return self._getSelectedChar(self._selected_save_option == option)

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        match self._state:
            case self.STATE_DEFAULT:
                if len(self._saves) == 0:
                    disp_text += "\nThere are no saves to select from."
                else:
                    disp_text += self._getOptionsText()
            case self.STATE_LOADED_SAVE:
                disp_text += "\nLoaded successfully.\nPress ENTER to continue."
            case self.STATE_DELETED_SAVE:
                disp_text += "\nDeleted successfully.\nPress ENTER to continue."
            case self.STATE_SELECTED_SAVE:
                disp_text += self._getOptionsText()
                disp_text += f"\n{self._getOptionStatus(self.OPTION_LOAD)}Load" \
                    + f"\n{self._getOptionStatus(self.OPTION_DELETE)}Delete"
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuOptions(ModeGameMenu):
    __slots__ = (
        '_pressed_return',
    )

    def __init__(self, previous_mode, old_screen, pressed_return: bool):
        super().__init__(previous_mode, old_screen)
        self._pressed_return = pressed_return

    def _getAction(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE:
            return MenuAction.NOTHING
        elif event.type == pygame.KEYUP:
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
                    if self._pressed_return:
                        self._pressed_return = False
                    else:
                        return MenuAction.CONFIRM
        return super()._getAction(event)

    def _inputEvent(self, event):
        match self._getAction(event):
            case MenuAction.QUIT | MenuAction.REJECT:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case MenuAction.DOWN | MenuAction.LEFT:
                display.changeScale(-1)
            case MenuAction.UP | MenuAction.RIGHT:
                display.changeScale(1)
            case MenuAction.CONFIRM:
                display.toggleFullscreen()
        if event.type == pygame.KEYDOWN and '1' <= event.unicode <= '9':
            target_scale = int(event.unicode)
            display.setScale(target_scale)

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += f"ARROW KEYS) Upscaling: {display.upscale}" \
            + f"\nENTER) Fullscreen: {self.getTickBox(display.is_fullscreen)}"
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))

    @staticmethod
    def getTickBox(value: bool):
        inside = "*" if value else "_"
        return f"[{inside}]"
