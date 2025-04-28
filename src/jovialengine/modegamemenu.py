import abc
import enum
import string

import pygame

from . import gamebuilder
from . import display
from . import gameinput
from . import utility
from .fontwrap import get_default_font_wrap
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
    _MENU_CHAR_WIDTH = 40
    _SHARED_DISP_TEXT = "Options:\nESC) Go Back\n"

    __slots__ = (
        '_MENU_WIDTH',
        '_previous_mode',
        '_last_disp_text',
        '_menu_surface',
        '_previous_hat',
    )

    def __init__(self, previous_mode: ModeBase, old_screen: pygame.Surface | None = None):
        super().__init__()
        self._MENU_WIDTH = get_default_font_wrap().font.size('_' * self._MENU_CHAR_WIDTH)[0] + 1
        self._previous_mode = previous_mode
        if old_screen is None:
            old_screen = self._get_old_screen()
        self._background = old_screen
        self._last_disp_text: str | None = None
        self._menu_surface: pygame.Surface
        self._previous_hat = (0, 0)

    def _get_old_screen(self):
        return display.get_blurred_screen(self._previous_mode)

    def _get_action(self, event: pygame.event.Event):
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
    def _get_selected_char(is_selected: bool):
        return ">" if is_selected else "_"

    def _draw_text_always(self, disp_text: str):
        self._last_disp_text = disp_text
        self._menu_surface = get_default_font_wrap().render_inside(
            self._MENU_WIDTH,
            disp_text,
            self._TEXT_COLOR,
            self._BACKGROUND_COLOR
        )
        self._menu_surface.set_alpha(235)

    def _draw_text(self, disp_text: str):
        if self._last_disp_text != disp_text:
            self._draw_text_always(disp_text)


class ModeGameMenuList(ModeGameMenu, abc.ABC):
    __slots__ = (
        '_index',
    )

    def __init__(self, previous_mode, old_screen):
        super().__init__(previous_mode, old_screen)
        self._index = 0

    @abc.abstractmethod
    def _get_options_length(self) -> int:
        raise NotImplementedError(
            type(self).__name__ + "._get_options_length(self)"
        )

    @abc.abstractmethod
    def _get_option_name(self, index: int) -> str:
        raise NotImplementedError(
            type(self).__name__ + "._get_option_name(self, index)"
        )

    def _get_options_text(self) -> str:
        text = ""
        for i in range(-1, 2):
            text += "\n"
            this_index = self._index + i
            text += ">" if i == 0 else "_"
            if 0 <= this_index < self._get_options_length():
                text += self._get_option_name(this_index)
        return text


class ModeGameMenuTop(ModeGameMenu):
    _OPTIONS = [
        "Save",
        "Load",
        "Options",
        "Edit Controls",
        "Reset Controls",
        "Restart",
        "Quit",
    ]

    __slots__ = (
        '_options',
        '_selected',
    )

    def __init__(self, previous_mode, old_screen=None):
        super().__init__(previous_mode, old_screen)
        self._options = self._OPTIONS[2:] if gamebuilder.get_auto_save() else self._OPTIONS
        self._selected = 0

    def _take_event(self, event):
        match self._get_action(event):
            case MenuAction.QUIT:
                gamebuilder.stop()
            case MenuAction.REJECT:
                self.next_mode = self._previous_mode
            case MenuAction.UP | MenuAction.LEFT:
                self._selected -= 1
            case MenuAction.DOWN | MenuAction.RIGHT:
                self._selected += 1
            case MenuAction.CONFIRM:
                match self._selected + (2 if gamebuilder.get_auto_save() else 0):
                    case 0:
                        self.next_mode = ModeGameMenuSave(self._previous_mode, self._background)
                    case 1:
                        self.next_mode = ModeGameMenuLoad(self._previous_mode, self._background)
                    case 2:
                        pressed_return = event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                        self.next_mode = ModeGameMenuOptions(self._previous_mode, self._background, pressed_return)
                    case 3:
                        self.next_mode = ModeGameMenuControls(self._previous_mode, self._background)
                    case 4:
                        gameinput.reset_default_mapping()
                    case 5:
                        self._stop_mixer()
                        if gamebuilder.get_restart_affects_state():
                            gamebuilder.set_state()
                        self._previous_mode = gamebuilder.get_start_mode_cls()()
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                        self._background = self._get_old_screen()
                        self._last_disp_text = None
                    case 6:
                        gamebuilder.stop()
        self._selected = pygame.math.clamp(self._selected, 0, len(self._options) - 1)

    def _draw_post_camera(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += "ARROW KEYS + ENTER)"
        for index, option in enumerate(self._options):
            disp_text += "\n"
            disp_text += self._get_selected_char(self._selected == index)
            disp_text += option
        self._draw_text(disp_text)
        screen.blit(self._menu_surface)


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
        self._reset_cursor_blink()
        self._cursor_position = 0
        self._confirm_overwrite = False
        self._save_success = None

    def _reset_cursor_blink(self):
        self._cursor_switch = True
        self._cursor_timer = 0

    def _controller_type(self, direction: int):
        if self._cursor_position == len(self._save_name):
            if self._cursor_position < (self._MENU_CHAR_WIDTH - 1):
                char_pos = max(direction - 1, -1)
                self._save_name += self._CONTROLLER_CHARS[char_pos]
                self._reset_cursor_blink()
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
        self._reset_cursor_blink()

    def _take_event(self, event):
        match self._get_action(event):
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
                        self._save_name = utility.get_datetime_file_name()
                    if Save.will_overwrite(self._save_name) and not self._confirm_overwrite:
                        self._confirm_overwrite = True
                    else:
                        new_save = Save.get_from_mode(self._save_name, self._previous_mode)
                        self._save_success = new_save.save()
            case MenuAction.LEFT:
                self._cursor_position -= 1
                self._reset_cursor_blink()
            case MenuAction.RIGHT:
                self._cursor_position += 1
                self._reset_cursor_blink()
            case MenuAction.UP:
                if event.type == pygame.JOYHATMOTION:
                    self._controller_type(-1)
            case MenuAction.DOWN:
                if event.type == pygame.JOYHATMOTION:
                    self._controller_type(1)
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP | pygame.K_HOME | pygame.K_PAGEUP:
                    self._cursor_position = 0
                    self._reset_cursor_blink()
                case pygame.K_DOWN | pygame.K_END | pygame.K_PAGEDOWN:
                    self._cursor_position = len(self._save_name)
                    self._reset_cursor_blink()
                case pygame.K_DELETE:
                    self._save_name = self._save_name[:self._cursor_position] \
                        + self._save_name[self._cursor_position + 1:]
                    self._reset_cursor_blink()
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
                        self._reset_cursor_blink()
        self._cursor_position = pygame.math.clamp(self._cursor_position, 0, len(self._save_name))

    def _update_pre_sprites(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer >= self._CURSOR_TIME:
            self._cursor_switch = not self._cursor_switch
            self._cursor_timer -= self._CURSOR_TIME

    def _draw_post_camera(self, screen):
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
        self._draw_text_always(disp_text)
        if self._cursor_switch and draw_cursor:
            cursor_x = get_default_font_wrap().font.size(">" + self._save_name[:self._cursor_position])[0]
            cursor_y = self._menu_surface.get_height() - get_default_font_wrap().line_height
            self._menu_surface.fill(
                self._TEXT_COLOR,
                (
                    (cursor_x, cursor_y),
                    (1, get_default_font_wrap().line_height)
                )
            )
        screen.blit(self._menu_surface)


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
        self._saves = Save.get_all_from_files()
        self._state = self.STATE_DEFAULT
        self._selected_save_option = self.OPTION_LOAD

    def _take_event(self, event):
        action = self._get_action(event)
        if action == MenuAction.QUIT:
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
                self._index = pygame.math.clamp(self._index, 0, len(self._saves) - 1)
            case self.STATE_LOADED_SAVE:
                if action in {MenuAction.CONFIRM, MenuAction.REJECT}:
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case self.STATE_DELETED_SAVE:
                if action in {MenuAction.CONFIRM, MenuAction.REJECT}:
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
                            self._stop_mixer()
                            self._previous_mode = self._saves[self._index].load()
                            pygame.mixer.music.pause()
                            pygame.mixer.pause()
                            self._background = self._get_old_screen()
                            self._state = self.STATE_LOADED_SAVE
                        elif self._selected_save_option == self.OPTION_DELETE:
                            self._saves[self._index].delete()
                            del self._saves[self._index]
                            self._index = pygame.math.clamp(self._index, 0, len(self._saves) - 1)
                            self._state = self.STATE_DELETED_SAVE
                    case MenuAction.REJECT:
                        self._state = self.STATE_DEFAULT

    def _get_options_length(self):
        return len(self._saves)

    def _get_option_name(self, index):
        return self._saves[index].save_name

    def _get_option_status(self, option: int):
        return self._get_selected_char(self._selected_save_option == option)

    def _draw_post_camera(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        match self._state:
            case self.STATE_DEFAULT:
                if len(self._saves) == 0:
                    disp_text += "\nThere are no saves to select from."
                else:
                    disp_text += "ARROW KEYS + ENTER) Select a save:"
                    disp_text += self._get_options_text()
            case self.STATE_LOADED_SAVE:
                disp_text += "\nLoaded successfully.\nPress ENTER to continue."
            case self.STATE_DELETED_SAVE:
                disp_text += "\nDeleted successfully.\nPress ENTER to continue."
            case self.STATE_SELECTED_SAVE:
                disp_text += "ARROW KEYS + ENTER) Select a save:"
                disp_text += self._get_options_text()
                disp_text += f"\n{self._get_option_status(self.OPTION_LOAD)}Load" \
                    + f"\n{self._get_option_status(self.OPTION_DELETE)}Delete"
        self._draw_text(disp_text)
        screen.blit(self._menu_surface)


class ModeGameMenuOptions(ModeGameMenu):
    __slots__ = (
        '_pressed_return',
    )

    def __init__(self, previous_mode, old_screen, pressed_return: bool):
        super().__init__(previous_mode, old_screen)
        self._pressed_return = pressed_return

    def _get_action(self, event: pygame.event.Event):
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
        return super()._get_action(event)

    def _take_event(self, event):
        match self._get_action(event):
            case MenuAction.QUIT | MenuAction.REJECT:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            case MenuAction.DOWN | MenuAction.LEFT:
                display.change_scale(-1)
            case MenuAction.UP | MenuAction.RIGHT:
                display.change_scale(1)
            case MenuAction.CONFIRM:
                display.toggle_fullscreen()
        if event.type == pygame.KEYDOWN and '1' <= event.unicode <= '9':
            target_scale = int(event.unicode)
            display.set_scale(target_scale)

    def _draw_post_camera(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += f"ARROW KEYS) Upscaling: {display.upscale}" \
            + f"\nENTER) Fullscreen: {self.get_tick_box(display.is_fullscreen)}"
        self._draw_text(disp_text)
        screen.blit(self._menu_surface)

    @staticmethod
    def get_tick_box(value: bool):
        inside = "*" if value else "_"
        return f"[{inside}]"


class ModeGameMenuControls(ModeGameMenuList):
    STATE_CHOOSE_PLAYER = 0
    STATE_CHOOSE_EVENT = 1
    STATE_CHOOSE_INPUT = 2

    __slots__ = (
        '_state',
        '_selected_player',
        '_selected_input',
        '_selection_timer',
    )

    def __init__(self, previous_mode, old_screen):
        super().__init__(previous_mode, old_screen)
        self._state = self.STATE_CHOOSE_PLAYER if self._must_select_player() else self.STATE_CHOOSE_EVENT
        self._selected_player = 0
        self._selection_timer = 5000

    @staticmethod
    def _must_select_player() -> bool:
        return gameinput.max_players != 1

    def _get_options_length(self):
        return gameinput.num_inputs

    def _get_option_name(self, index):
        return gameinput.get_event_with_controls(self._selected_player, index)

    def _take_event(self, event):
        action = self._get_action(event)
        if action == MenuAction.QUIT:
            self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            return
        match self._state:
            case self.STATE_CHOOSE_PLAYER:
                match action:
                    case MenuAction.UP | MenuAction.LEFT:
                        self._selected_player -= 1
                    case MenuAction.DOWN | MenuAction.RIGHT:
                        self._selected_player += 1
                    case MenuAction.CONFIRM:
                        self._state = self.STATE_CHOOSE_EVENT
                        self._index = 0
                    case MenuAction.REJECT:
                        self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
                self._selected_player = pygame.math.clamp(self._selected_player, 0, gameinput.max_players - 1)
            case self.STATE_CHOOSE_EVENT:
                match action:
                    case MenuAction.UP | MenuAction.LEFT:
                        self._index -= 1
                    case MenuAction.DOWN | MenuAction.RIGHT:
                        self._index += 1
                    case MenuAction.CONFIRM:
                        self._state = self.STATE_CHOOSE_INPUT
                        self._selection_timer = 5000
                    case MenuAction.REJECT:
                        if self._must_select_player():
                            self._state = self.STATE_CHOOSE_PLAYER
                        else:
                            self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
                self._index = pygame.math.clamp(self._index, 0, gameinput.num_inputs - 1)
            case self.STATE_CHOOSE_INPUT:
                if gameinput.set_input_mapping(self._selected_player, self._index, event):
                    self._state = self.STATE_CHOOSE_EVENT

    def _update_pre_sprites(self, dt):
        if self._state == self.STATE_CHOOSE_INPUT:
            self._selection_timer -= dt
            if self._selection_timer <= 0:
                self._state = self.STATE_CHOOSE_EVENT

    def _draw_post_camera(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        if self._state != self.STATE_CHOOSE_INPUT:
            disp_text += "ARROW KEYS + ENTER)\n"
        if self._must_select_player():
            disp_text += f"Player: {self._selected_player + 1}\n"
        if self._state == self.STATE_CHOOSE_EVENT:
            disp_text += "Action:"
            disp_text += self._get_options_text()
        if self._state == self.STATE_CHOOSE_INPUT:
            disp_text += f"Action: {gameinput.get_event_name(self._index)}"
            disp_text += "\n\n____press a button to select"
            disp_text += f"\n____(wait {(self._selection_timer // 1000) + 1} seconds to exit)"
        self._draw_text(disp_text)
        screen.blit(self._menu_surface)
