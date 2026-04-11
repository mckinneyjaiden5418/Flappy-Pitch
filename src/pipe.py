"""Pipe obstacle entity."""

import pygame

from src.constants import (
    COLOR_PIPE,
    COLOR_PIPE_DARK,
    PIPE_GAP,
    PIPE_SPEED,
    PIPE_WIDTH,
    STAFF_BOTTOM,
    STAFF_TOP,
    WINDOW_H,
    WINDOW_W,
)

_CAP_OVERHANG: int = 4
_CAP_HEIGHT: int = 20


class Pipe:
    """A pair of top and bottom pipes with a gap the bird must fly through."""

    def __init__(self, gap_center_y: float) -> None:
        """Initialise the pipe just off the right edge of the screen.

        Args:
            gap_center_y (float): Y coordinate of the centre of the gap.
        """
        self.x: float = float(WINDOW_W + PIPE_WIDTH)
        self.gap_center_y: float = gap_center_y
        self.scored: bool = False

    def update(self) -> None:
        """Move the pipe leftward by one frame."""
        self.x -= PIPE_SPEED

    def is_off_screen(self) -> bool:
        """Check whether the pipe has scrolled past the left edge.

        Returns:
            bool: True if the pipe is no longer visible.
        """
        return self.x < -PIPE_WIDTH - 10

    def _top_rect(self) -> pygame.Rect:
        """Return the rect for the top pipe body.

        Returns:
            pygame.Rect: Top pipe body rectangle.
        """
        top_h: float = self.gap_center_y - PIPE_GAP / 2
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, int(top_h))

    def _bottom_rect(self) -> pygame.Rect:
        """Return the rect for the bottom pipe body.

        Returns:
            pygame.Rect: Bottom pipe body rectangle.
        """
        bot_y: float = self.gap_center_y + PIPE_GAP / 2
        return pygame.Rect(int(self.x), int(bot_y), PIPE_WIDTH, WINDOW_H - int(bot_y))

    def draw(self, surface: pygame.Surface) -> None:
        """Render both pipes onto a surface.

        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        top_rect: pygame.Rect = self._top_rect()
        bot_rect: pygame.Rect = self._bottom_rect()

        # Top pipe body
        pygame.draw.rect(surface, COLOR_PIPE, top_rect)
        # Top pipe cap
        cap_top: pygame.Rect = pygame.Rect(
            int(self.x) - _CAP_OVERHANG,
            top_rect.bottom - _CAP_HEIGHT,
            PIPE_WIDTH + _CAP_OVERHANG * 2,
            _CAP_HEIGHT,
        )
        pygame.draw.rect(surface, COLOR_PIPE_DARK, cap_top)

        # Bottom pipe body
        pygame.draw.rect(surface, COLOR_PIPE, bot_rect)
        # Bottom pipe cap
        cap_bot: pygame.Rect = pygame.Rect(
            int(self.x) - _CAP_OVERHANG,
            bot_rect.top,
            PIPE_WIDTH + _CAP_OVERHANG * 2,
            _CAP_HEIGHT,
        )
        pygame.draw.rect(surface, COLOR_PIPE_DARK, cap_bot)

    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        """Check whether the bird collides with either pipe.

        Args:
            bird_rect (pygame.Rect): The bird's collision rectangle.

        Returns:
            bool: True if the bird overlaps with either pipe.
        """
        return bird_rect.colliderect(self._top_rect()) or bird_rect.colliderect(self._bottom_rect())

    @staticmethod
    def random_gap_center() -> float:
        """Generate a random gap centre Y within the playable staff area.

        Returns:
            float: Gap centre Y coordinate.
        """
        import random
        margin: int = 40
        return random.uniform(  # noqa: S311
            STAFF_TOP + margin,
            STAFF_BOTTOM - margin,
        )
