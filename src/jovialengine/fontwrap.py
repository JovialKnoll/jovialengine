import pygame


class FontWrap(object):
    __slots__ = (
        'font',
        'line_height',
        '_antialias',
    )

    def __init__(self, font: pygame.font.Font, line_height: int, antialias: bool):
        self.font = font
        self.line_height = line_height
        self._antialias = antialias

    def render_to(self, surf: pygame.Surface, dest: pygame.typing.IntPoint, text: str,
                  color: pygame.typing.ColorLike, bgcolor: pygame.typing.ColorLike | None=None):
        surf.blit(self.font.render(text, self._antialias, color, bgcolor), dest)

    def render_to_centered(self, surf: pygame.Surface, dest: pygame.typing.IntPoint, text: str,
                           color: pygame.typing.ColorLike, bgcolor: pygame.typing.ColorLike | None = None):
        text_size = self.font.size(text)
        surf.blit(
            self.font.render(text, self._antialias, color, bgcolor),
            (dest[0] - text_size[0] // 2, dest[1] - text_size[1] // 2)
        )

    def _calculate_lines_for_words(self, width: int, words: list[str]):
        lines = [words[0].replace('_', ' ')]
        for word in words[1:]:
            new_word = word.replace('_', ' ')
            if self.font.size(lines[-1] + " " + new_word)[0] > width:
                lines.append(new_word)
            else:
                lines[-1] += " " + new_word
        return lines

    def render_to_inside(self, surf: pygame.Surface, dest: pygame.typing.IntPoint, width: int, text: str,
                         color: pygame.typing.ColorLike,
                         bgcolor: pygame.typing.ColorLike | None = None):
        # probably more efficient to do once?
        part_dest = [dest[0], dest[1]]
        for words in [line.split() for line in text.splitlines()]:
            if not words:
                words = [""]
            lines = self._calculate_lines_for_words(width, words)
            for line in lines:
                surf.blit(
                    self.font.render(line, self._antialias, color, bgcolor),
                    part_dest
                )
                part_dest[1] += self.line_height

    def _render_words_inside(self, width: int, words: list[str],
                             color: pygame.typing.ColorLike,
                             bgcolor: pygame.typing.ColorLike | None = None):
        """Returns a surface of the width with the words drawn on it.
        If any word is too long to fit, it will be in its own line, and truncated.
        """
        lines = self._calculate_lines_for_words(width, words)
        result = pygame.Surface((width, self.line_height * len(lines))).convert()
        result.fill(bgcolor)
        for i, line in enumerate(lines):
            drawn_line = self.font.render(line, self._antialias, color, bgcolor).convert()
            result.blit(drawn_line, (0, i * self.line_height))
        return result

    def render_inside(self, width: int, text: str,
                      color: pygame.typing.ColorLike,
                      bgcolor: pygame.typing.ColorLike | None = None):
        # probably more efficient if keeping resultant surface and using that to draw over and over?
        height = 0
        images = []
        for words in [line.split() for line in text.splitlines()]:
            if not words:
                words = [""]
            images.append(self._render_words_inside(width, words, color, bgcolor))
            height += images[-1].get_height()
        result = pygame.Surface((width, height)).convert()
        dest = [0, 0]
        for image in images:
            result.blit(image, dest)
            dest[1] += image.get_height()
        return result


_default: FontWrap | None = None


def init(font: pygame.font.Font, line_height: int, antialias: bool):
    global _default
    if _default:
        raise RuntimeError("error: _default is already set")
    _default = FontWrap(font, line_height, antialias)


def get_default_font_wrap():
    return _default
