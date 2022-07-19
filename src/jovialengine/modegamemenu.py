import abc

import pygame

from . import game
from . import display
from .fontwrap import getDefaultFontWrap
from .modebase import ModeBase
from .save import Save
from .saveable import Saveable


class ModeGameMenu(ModeBase, abc.ABC):
    _MENU_CHAR_WIDTH = 26
    _SHARED_DISP_TEXT = "Options:\nESC) Go Back\n"

    __slots__ = (
        '_MENU_WIDTH',
        '_previous_mode',
        '_last_disp_text',
        '_menu_surface',
    )

    def __init__(self, previous_mode: ModeBase, old_screen=None):
        self._init(display.screen_size)
        self._MENU_WIDTH = getDefaultFontWrap().font.size('_' * self._MENU_CHAR_WIDTH)[0] + 1
        self._previous_mode = previous_mode
        if old_screen is None:
            old_screen = self._getOldScreen()
        self._background = old_screen
        self._last_disp_text = None
        self._menu_surface = None

    def _getOldScreen(self):
        return display.getBlurredScreen(self._previous_mode)

    def _drawTextAlways(self, disp_text: str):
        self._last_disp_text = disp_text
        self._menu_surface = getDefaultFontWrap().renderInside(
            self._MENU_WIDTH,
            disp_text,
            (255, 255, 255),
            (0, 0, 0)
        )
        self._menu_surface.set_alpha(235)

    def _drawText(self, disp_text: str):
        if self._last_disp_text != disp_text:
            self._drawTextAlways(disp_text)


class ModeGameMenuTop(ModeGameMenu):
    def _input(self, action):
        if action.type == pygame.QUIT:
            game.getGame().running = False
        elif action.type == pygame.KEYDOWN:
            if action.key == pygame.K_ESCAPE:
                self.next_mode = self._previous_mode
            elif action.key == pygame.K_1:
                self.next_mode = ModeGameMenuSave(self._previous_mode, self._background)
            elif action.key == pygame.K_2:
                self.next_mode = ModeGameMenuLoad(self._previous_mode, self._background)
            elif action.key == pygame.K_3:
                self.next_mode = ModeGameMenuOptions(self._previous_mode, self._background)
            elif action.key == pygame.K_4:
                self._stopMixer()
                game.getGame().state = game.getGame().state_cls()
                self._previous_mode = game.getGame().start_mode_cls()
                pygame.mixer.music.pause()
                pygame.mixer.pause()
                self._background = self._getOldScreen()
                self._last_disp_text = None
            elif action.key == pygame.K_5:
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

    def _input(self, action):
        if action.type == pygame.QUIT:
            self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
        elif action.type == pygame.KEYDOWN:
            char = action.unicode
            length = len(self._save_name)
            if self._save_success:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            elif action.key == pygame.K_ESCAPE:
                if self._confirm_overwrite:
                    self._confirm_overwrite = False
                    self._save_success = None
                else:
                    self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            elif action.key == pygame.K_RETURN:
                if self._save_name and isinstance(self._previous_mode, Saveable):
                    if Save.willOverwrite(self._save_name) and not self._confirm_overwrite:
                        self._confirm_overwrite = True
                    elif not self._save_success:
                        new_save = Save.getFromMode(self._save_name, self._previous_mode)
                        self._save_success = new_save.save()
            elif action.key == pygame.K_LEFT:
                self._cursor_position = max(self._cursor_position - 1, 0)
                self._resetCursorBlink()
            elif action.key == pygame.K_RIGHT:
                self._cursor_position = min(self._cursor_position + 1, length)
                self._resetCursorBlink()
            elif action.key in (pygame.K_UP, pygame.K_HOME):
                self._cursor_position = 0
                self._resetCursorBlink()
            elif action.key in (pygame.K_DOWN, pygame.K_END):
                self._cursor_position = length
                self._resetCursorBlink()
            elif action.key == pygame.K_DELETE:
                self._save_name = self._save_name[:self._cursor_position] + self._save_name[self._cursor_position + 1:]
                self._resetCursorBlink()
            elif action.key == pygame.K_BACKSPACE:
                if self._cursor_position > 0:
                    self._save_name = self._save_name[:self._cursor_position - 1] \
                        + self._save_name[self._cursor_position:]
                    self._cursor_position -= 1
                self._resetCursorBlink()
            elif (
                length < (self._MENU_CHAR_WIDTH - 1)
                and (
                    # numbers
                    ('0' <= char <= '9')
                    # or letters
                    or (96 < action.key < 123)
                )
            ):
                self._save_name = self._save_name[:self._cursor_position] \
                    + char \
                    + self._save_name[self._cursor_position:]
                self._cursor_position += 1
                self._resetCursorBlink()

    def _update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer >= self._CURSOR_TIME:
            self._cursor_switch = not self._cursor_switch
            self._cursor_timer -= self._CURSOR_TIME

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        if not isinstance(self._previous_mode, Saveable):
            disp_text += "\nYou can't save now."
        elif not self._save_success:
            disp_text += "ENTER) Save\nType a save name:\n>"
            if self._save_name:
                disp_text += self._save_name
            if self._confirm_overwrite and self._save_success is None:
                disp_text += "\nThis will overwrite an existing save." \
                    + "\nPress ENTER again to confirm, or ESC to go back."
            elif self._save_success is False:
                disp_text += "\nSave failed.\nPress ENTER to try again, or ESC to go back."
        else:
            disp_text += "\nSaved successfully.\nPress any key to go back."
        self._drawTextAlways(disp_text)
        if self._cursor_switch and not self._confirm_overwrite and self._save_success is None:
            cursor_x = getDefaultFontWrap().font.size(">" + self._save_name[:self._cursor_position])[0]
            self._menu_surface.fill(
                (255, 255, 255),
                (
                    (cursor_x, 4 * getDefaultFontWrap().line_height),
                    (1, getDefaultFontWrap().line_height)
                )
            )
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuLoad(ModeGameMenu):
    __slots__ = (
        '_saves',
        '_save_index',
        '_loaded_save',
        '_confirm_delete',
        '_deleted_save',
    )

    def __init__(self, previous_mode, old_screen=None):
        super().__init__(previous_mode, old_screen)
        self._saves = Save.getAllFromFiles()
        self._save_index = 0
        self._loaded_save = False
        self._confirm_delete = False
        self._deleted_save = False

    def _input(self, action):
        if action.type == pygame.QUIT:
            self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
        elif action.type == pygame.KEYDOWN:
            if action.key == pygame.K_ESCAPE or self._loaded_save:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            elif self._deleted_save:
                self._deleted_save = False
            elif self._confirm_delete:
                if action.key == pygame.K_RETURN:
                    self._confirm_delete = False
                    self._saves[self._save_index].delete()
                    del self._saves[self._save_index]
                    self._save_index = max(0, min(len(self._saves) - 1, self._save_index))
                    self._deleted_save = True
                else:
                    self._confirm_delete = False
            elif len(self._saves) > 0:
                if action.key in (pygame.K_UP, pygame.K_LEFT):
                    self._save_index = max(self._save_index - 1, 0)
                elif action.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    self._save_index = min(self._save_index + 1, len(self._saves) - 1)
                elif action.key == pygame.K_RETURN:
                    self._stopMixer()
                    self._previous_mode = self._saves[self._save_index].load()
                    pygame.mixer.music.pause()
                    pygame.mixer.pause()
                    self._background = self._getOldScreen()
                    self._loaded_save = True
                elif action.key == pygame.K_DELETE:
                    self._confirm_delete = True

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        if len(self._saves) == 0:
            disp_text += "\nThere are no saves to select from."
        elif self._loaded_save:
            disp_text += "\nLoaded successfully.\nPress any key to go back."
        elif self._deleted_save:
            disp_text += "\nDeleted successfully.\nPress any key to continue."
        else:
            disp_text += "ENTER) Load\nDEL) Delete\nARROW KEYS) Select a save:"
            for i in range(-1, 2):
                disp_text += "\n"
                this_index = self._save_index + i
                if i == 0:
                    disp_text += ">"
                else:
                    disp_text += "_"
                if 0 <= this_index < len(self._saves):
                    disp_text += self._saves[this_index].save_name
            if self._confirm_delete:
                disp_text += "\nAre you sure you want to delete?" \
                    + "\nPress ENTER to confirm, or any other key to go back."
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))


class ModeGameMenuOptions(ModeGameMenu):
    def _input(self, action):
        if action.type == pygame.QUIT:
            self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
        elif action.type == pygame.KEYUP:
            if action.key in (
                    pygame.K_DOWN, pygame.K_s,
                    pygame.K_LEFT, pygame.K_a,
                    pygame.K_PAGEDOWN, pygame.K_MINUS,
            ):
                display.changeScale(-1)
            elif action.key in (
                    pygame.K_UP, pygame.K_w,
                    pygame.K_RIGHT, pygame.K_d,
                    pygame.K_PAGEUP, pygame.K_EQUALS,
            ):
                display.changeScale(1)
            elif action.key in (pygame.K_f, pygame.K_F11,):
                display.toggleFullscreen()
        elif action.type == pygame.KEYDOWN:
            if action.key == pygame.K_ESCAPE:
                self.next_mode = ModeGameMenuTop(self._previous_mode, self._background)
            elif '1' <= action.unicode <= '9':
                target_scale = int(action.unicode)
                display.setScale(target_scale)

    def _drawPreSprites(self, screen):
        disp_text = self._SHARED_DISP_TEXT
        disp_text += f"ARROWS) Upscaling: {display.upscale}" \
                     f"\nF) Fullscreen: {self.getTickBox(display.is_fullscreen)}"
        self._drawText(disp_text)
        screen.blit(self._menu_surface, (0, 0))

    @staticmethod
    def getTickBox(value: bool):
        inside = "*" if value else "_"
        return f"[{inside}]"
