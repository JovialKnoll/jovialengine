import pygame

import constants


class FontWrap(object):
    __slots__ = (
        'font',
        '_antialias',
    )

    def __init__(self, font: pygame.font.Font, antialias: bool):
        self.font = font
        self._antialias = antialias

    def renderTo(self, surf: pygame.Surface, dest, text: str, color, background=None):
        surf.blit(self.font.render(text, self._antialias, color, background), dest)

    def renderToCentered(self, surf: pygame.Surface, dest, text: str, color, background=None):
        text_size = self.font.size(text)
        surf.blit(
            self.font.render(text, self._antialias, color, background),
            (dest[0] - text_size[0] // 2, dest[1] - text_size[1] // 2)
        )

    def _calculateLinesForWords(self, width: int, words: list[str]):
        lines = [words[0].replace('_', ' ')]
        for word in words[1:]:
            new_word = word.replace('_', ' ')
            if self.font.size(lines[-1] + " " + new_word)[0] > width:
                lines.append(new_word)
            else:
                lines[-1] += " " + new_word
        return lines

    def renderToInside(self, surf: pygame.Surface, dest, width: int, text: str, color, background=None):
        # probably more efficient to do once?
        part_dest = [dest[0], dest[1]]
        for words in [line.split() for line in text.splitlines()]:
            if not words:
                words = [""]
            if background is None:
                img = self.renderWordsInside(width, words, color, constants.COLORKEY)
                img.set_colorkey(constants.COLORKEY)
            else:
                img = self.renderWordsInside(width, words, color, background)
            surf.blit(img, part_dest)
            part_dest[1] += img.get_height()

    def _renderWordsInside(self, width: int, words: list[str], color, background):
        """Returns a surface of the width with the words drawn on it.
        If any word is too long to fit, it will be in its own line, and truncated.
        """
        lines = self._calculateLinesForWords(width, words)
        result = pygame.Surface((width, constants.FONT_HEIGHT * len(lines))).convert()
        result.fill(background)
        for i, line in enumerate(lines):
            drawn_line = self.font.render(line, self._antialias, color, background).convert()
            result.blit(drawn_line, (0, i * constants.FONT_HEIGHT))
        return result

    def renderInside(self, width: int, text: str, color, background):
        # probably more efficient if keeping resultant surface and using that to draw over and over?
        height = 0
        imgs = []
        for words in [line.split() for line in text.splitlines()]:
            if not words:
                words = [""]
            imgs.append(self._renderWordsInside(width, words, color, background))
            height += imgs[-1].get_height()
        result = pygame.Surface((width, height)).convert()
        dest = [0, 0]
        for img in imgs:
            result.blit(img, dest)
            dest[1] += img.get_height()
        return result
