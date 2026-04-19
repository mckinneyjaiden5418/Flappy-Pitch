"""Musical staff background renderer."""

import pygame

from src.constants import (
    COLOR_STAFF_LABEL,
    COLOR_STAFF_LINE,
    WINDOW_W,
)
from src.utils.pitch import midi_to_y

# Concert MIDI values for the five treble-clef staff lines: E4 G4 B4 D5 F5.
# Using concert pitch here so midi_to_y() maps them correctly on screen.
# Written (Bb) equivalents: F#4 A4 C#5 E5 G5.
_STAFF_LINE_CONCERT_MIDIS: tuple[int, ...] = (64, 67, 71, 74, 77)

# Landmark notes shown as text labels on the left edge.
# Stored as concert MIDI; displayed as their concert Bb names (C4, C5, C6)
# — i.e. what a trumpet player calls these pitches.
# Concert C4 = MIDI 60, concert C5 = MIDI 72, concert C6 = MIDI 84.
_LANDMARK_NOTES: tuple[tuple[int, str], ...] = (
    (60, "C4"),
    (72, "C5"),
    (84, "C6"),
)

_TREBLE_CLEF: str = "\U0001D11E"  # 𝄞


class Staff:
    """Draws a musical staff in the background of the game."""

    def __init__(self) -> None:
        """Initialise the staff and cache its fonts."""
        self._font_label: pygame.font.Font = pygame.font.SysFont("Arial", 13)
        # Segoe UI Symbol / DejaVu Sans carry the treble clef glyph on most platforms.
        self._font_clef: pygame.font.Font = pygame.font.SysFont(
            "segoeuisymbol, dejavusans, Arial", 64
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Render the staff lines, treble clef, and landmark labels onto a surface.

        Staff lines are positioned using midi_to_y() so they share the exact same
        coordinate system as the bird, ensuring the bird sits on the correct line
        for each pitch.

        Landmark labels show concert Bb note names (C4, C5, C6) — the names a
        trumpet player uses for those pitches.

        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        # Draw the five staff lines at their true midi_to_y positions.
        for concert_midi in _STAFF_LINE_CONCERT_MIDIS:
            y: int = int(midi_to_y(concert_midi))
            pygame.draw.line(surface, COLOR_STAFF_LINE, (0, y), (WINDOW_W, y), 1)

        # Treble clef glyph on the far left, vertically centred between lines 1 and 5.
        y_top: int = int(midi_to_y(_STAFF_LINE_CONCERT_MIDIS[-1]))
        y_bot: int = int(midi_to_y(_STAFF_LINE_CONCERT_MIDIS[0]))
        clef_surf: pygame.Surface = self._font_clef.render(_TREBLE_CLEF, True, COLOR_STAFF_LABEL)
        clef_y: int = (y_top + y_bot) // 2 - clef_surf.get_height() // 2
        surface.blit(clef_surf, (6, clef_y))

        # Landmark labels on the left edge.
        for concert_midi, label in _LANDMARK_NOTES:
            y = int(midi_to_y(concert_midi))
            label_surf: pygame.Surface = self._font_label.render(label, True, COLOR_STAFF_LABEL)
            surface.blit(label_surf, (4, y - 7))