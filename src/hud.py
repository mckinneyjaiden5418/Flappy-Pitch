"""HUD (heads-up display) renderer."""

from typing import TYPE_CHECKING

import pygame

from src.constants import (
    COLOR_BLACK,
    COLOR_GOLD,
    COLOR_TEXT_MUTED,
    COLOR_WHITE,
    WINDOW_H,
    WINDOW_W,
)

if TYPE_CHECKING:
    pass

_OVERLAY_ALPHA: int = 140


class HUD:
    """Renders score, current note name, input mode, and game-state overlays."""

    def __init__(self) -> None:
        """Initialise fonts for all HUD elements."""
        self._font_score: pygame.font.Font = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_note: pygame.font.Font = pygame.font.SysFont("Arial", 30, bold=True)
        self._font_label: pygame.font.Font = pygame.font.SysFont("Arial", 13)
        self._font_overlay_title: pygame.font.Font = pygame.font.SysFont("Arial", 34, bold=True)
        self._font_overlay_sub: pygame.font.Font = pygame.font.SysFont("Arial", 16)

    def draw_score(self, surface: pygame.Surface, score: int, best: int) -> None:
        """Draw the current score and best score in the top-left corner.

        Args:
            surface (pygame.Surface): Surface to draw on.
            score (int): Current run score.
            best (int): All-time best score.
        """
        score_surf: pygame.Surface = self._font_score.render(
            f"Score: {score}", True, COLOR_BLACK,
        )
        best_surf: pygame.Surface = self._font_label.render(
            f"Best: {best}", True, COLOR_TEXT_MUTED,
        )
        surface.blit(score_surf, (16, 16))
        surface.blit(best_surf, (16, 42))

    def draw_note(self, surface: pygame.Surface, note_name: str | None, mode: str) -> None:
        """Draw the current note name and input mode label at the top-right.

        Args:
            surface (pygame.Surface): Surface to draw on.
            note_name (str | None): Active note name, or None if silent.
            mode (str): Input mode label (e.g. 'keyboard' or 'mic').
        """
        display: str = note_name if note_name else "—"
        note_surf: pygame.Surface = self._font_note.render(display, True, COLOR_GOLD)
        note_rect: pygame.Rect = note_surf.get_rect(topright=(WINDOW_W - 16, 16))
        surface.blit(note_surf, note_rect)

        mode_surf: pygame.Surface = self._font_label.render(
            f"mode: {mode}", True, COLOR_TEXT_MUTED,
        )
        mode_rect: pygame.Rect = mode_surf.get_rect(topright=(WINDOW_W - 16, 50))
        surface.blit(mode_surf, mode_rect)

    def draw_overlay(self, surface: pygame.Surface, title: str, subtitle: str) -> None:
        """Draw a semi-transparent dark overlay with centred title and subtitle text.

        Args:
            surface (pygame.Surface): Surface to draw on.
            title (str): Large title text.
            subtitle (str): Smaller subtitle text below the title.
        """
        overlay: pygame.Surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, _OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        title_surf: pygame.Surface = self._font_overlay_title.render(title, True, COLOR_WHITE)
        title_rect: pygame.Rect = title_surf.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 - 20))
        surface.blit(title_surf, title_rect)

        sub_surf: pygame.Surface = self._font_overlay_sub.render(subtitle, True, (210, 210, 210))
        sub_rect: pygame.Rect = sub_surf.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 20))
        surface.blit(sub_surf, sub_rect)

    def draw_keybinds(self, surface: pygame.Surface) -> None:
        """Draw the keyboard hint bar at the bottom of the screen.

        Args:
            surface (pygame.Surface): Surface to draw on.
        """
        hints: str = "Keys:  A=C3  S=E3  D=G3  F=C4  G=E4  H=G4  J=C5   |   M = toggle mic"
        hint_surf: pygame.Surface = self._font_label.render(hints, True, COLOR_TEXT_MUTED)
        hint_rect: pygame.Rect = hint_surf.get_rect(
            midbottom=(WINDOW_W // 2, WINDOW_H - 8),
        )
        surface.blit(hint_surf, hint_rect)
