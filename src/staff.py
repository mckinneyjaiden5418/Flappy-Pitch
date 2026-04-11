"""Musical staff background renderer."""

import pygame

from src.constants import (
    COLOR_STAFF_LABEL,
    COLOR_STAFF_LINE,
    STAFF_BOTTOM,
    STAFF_TOP,
    WINDOW_W,
)
from src.utils.pitch import midi_to_y

_LABEL_NOTES: tuple[tuple[int, str], ...] = (
    (72, "C5"),
    (67, "G4"),
    (64, "E4"),
    (60, "C4"),
    (55, "G3"),
    (52, "E3"),
    (48, "C3"),
)

_STAFF_LINE_MIDIS: tuple[int, ...] = (64, 67, 71, 74, 77)


class Staff:
    """Draws a musical staff in the background of the game."""

    def __init__(self) -> None:
        """Initialise the staff and cache its label font."""
        self._font: pygame.font.Font = pygame.font.SysFont("Arial", 13)

    def draw(self, surface: pygame.Surface) -> None:
        """Render the staff lines and note labels onto a surface.

        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        span: float = STAFF_BOTTOM - STAFF_TOP
        line_spacing: float = span / 6

        for i in range(5):
            y: int = int(STAFF_TOP + 20 + i * line_spacing)
            pygame.draw.line(surface, COLOR_STAFF_LINE, (0, y), (WINDOW_W, y), 1)

        for midi, label in _LABEL_NOTES:
            y: int = int(midi_to_y(midi))
            label_surf: pygame.Surface = self._font.render(label, True, COLOR_STAFF_LABEL)
            surface.blit(label_surf, (4, y - 7))
