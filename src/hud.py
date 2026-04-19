"""HUD (heads-up display) renderer."""

from typing import TYPE_CHECKING

import pygame

from src.constants import (
    COLOR_BLACK,
    COLOR_GOLD,
    COLOR_SETTINGS_BG,
    COLOR_SETTINGS_BORDER,
    COLOR_SETTINGS_ITEM,
    COLOR_SETTINGS_SELECTED,
    COLOR_TEXT_MUTED,
    COLOR_WHITE,
    WINDOW_H,
    WINDOW_W,
)

if TYPE_CHECKING:
    pass

_OVERLAY_ALPHA: int = 140
_SETTINGS_PANEL_W: int = 460
_SETTINGS_PANEL_H: int = 300
_SETTINGS_ROW_H: int = 32
_SETTINGS_MAX_VISIBLE: int = 6  # max device rows shown at once before scrolling


class HUD:
    """Renders score, current note name, input mode, and game-state overlays."""

    def __init__(self) -> None:
        """Initialise fonts for all HUD elements."""
        self._font_score: pygame.font.Font = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_note: pygame.font.Font = pygame.font.SysFont("Arial", 30, bold=True)
        self._font_label: pygame.font.Font = pygame.font.SysFont("Arial", 13)
        self._font_overlay_title: pygame.font.Font = pygame.font.SysFont("Arial", 34, bold=True)
        self._font_overlay_sub: pygame.font.Font = pygame.font.SysFont("Arial", 16)
        self._font_settings_title: pygame.font.Font = pygame.font.SysFont("Arial", 18, bold=True)
        self._font_settings_item: pygame.font.Font = pygame.font.SysFont("Arial", 14)
        self._font_settings_hint: pygame.font.Font = pygame.font.SysFont("Arial", 12)

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

    def draw_note(self, surface: pygame.Surface, note_name: str | None) -> None:
        """Draw the current detected note name at the top-right.

        Args:
            surface (pygame.Surface): Surface to draw on.
            note_name (str | None): Active written Bb note name, or None if silent.
        """
        display: str = note_name if note_name else "—"
        note_surf: pygame.Surface = self._font_note.render(display, True, COLOR_GOLD)
        note_rect: pygame.Rect = note_surf.get_rect(topright=(WINDOW_W - 16, 16))
        surface.blit(note_surf, note_rect)

    def draw_hint_bar(self, surface: pygame.Surface, text: str) -> None:
        """Draw a small hint string centred at the bottom of the screen.

        Args:
            surface (pygame.Surface): Surface to draw on.
            text (str): Hint text to display.
        """
        hint_surf: pygame.Surface = self._font_label.render(text, True, COLOR_TEXT_MUTED)
        hint_rect: pygame.Rect = hint_surf.get_rect(
            midbottom=(WINDOW_W // 2, WINDOW_H - 8),
        )
        surface.blit(hint_surf, hint_rect)

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

    def draw_settings_overlay(
        self,
        surface: pygame.Surface,
        devices: list[tuple[int, str]],
        selected_index: int,
        active_device: int,
    ) -> None:
        """Draw the mic device selection overlay.

        Renders a centred panel listing all available input devices. The
        currently selected row is highlighted in gold; the currently active
        device is marked with a ● indicator.

        Args:
            surface (pygame.Surface): Surface to draw on.
            devices (list[tuple[int, str]]): Available input devices as
                (device_index, device_name) pairs from query_input_devices().
            selected_index (int): Index into `devices` of the highlighted row.
            active_device (int): sounddevice index of the device currently in use.
        """
        # Full-screen dim
        dim: pygame.Surface = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        surface.blit(dim, (0, 0))

        # Panel background
        panel_x: int = (WINDOW_W - _SETTINGS_PANEL_W) // 2
        panel_y: int = (WINDOW_H - _SETTINGS_PANEL_H) // 2
        panel_rect: pygame.Rect = pygame.Rect(panel_x, panel_y, _SETTINGS_PANEL_W, _SETTINGS_PANEL_H)

        panel_surf: pygame.Surface = pygame.Surface(
            (_SETTINGS_PANEL_W, _SETTINGS_PANEL_H), pygame.SRCALPHA
        )
        panel_surf.fill(COLOR_SETTINGS_BG)
        surface.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(surface, COLOR_SETTINGS_BORDER, panel_rect, 1)

        # Title
        title_surf: pygame.Surface = self._font_settings_title.render(
            "Select Microphone", True, COLOR_WHITE
        )
        surface.blit(title_surf, (panel_x + 16, panel_y + 14))

        # Divider
        div_y: int = panel_y + 42
        pygame.draw.line(
            surface, COLOR_SETTINGS_BORDER,
            (panel_x + 1, div_y), (panel_x + _SETTINGS_PANEL_W - 1, div_y), 1
        )

        # Device rows — scroll window centred on selected_index
        list_top: int = div_y + 8
        visible_count: int = min(_SETTINGS_MAX_VISIBLE, len(devices))
        scroll_start: int = max(
            0,
            min(selected_index - visible_count // 2, len(devices) - visible_count),
        )

        for row, i in enumerate(range(scroll_start, scroll_start + visible_count)):
            if i >= len(devices):
                break

            dev_idx, dev_name = devices[i]
            row_y: int = list_top + row * _SETTINGS_ROW_H
            is_selected: bool = i == selected_index
            is_active: bool = dev_idx == active_device

            # Highlight bar for selected row
            if is_selected:
                highlight_rect: pygame.Rect = pygame.Rect(
                    panel_x + 4, row_y - 2,
                    _SETTINGS_PANEL_W - 8, _SETTINGS_ROW_H - 4,
                )
                highlight_surf: pygame.Surface = pygame.Surface(
                    (highlight_rect.width, highlight_rect.height), pygame.SRCALPHA
                )
                highlight_surf.fill((255, 193, 7, 40))
                surface.blit(highlight_surf, (highlight_rect.x, highlight_rect.y))
                pygame.draw.rect(surface, COLOR_SETTINGS_SELECTED, highlight_rect, 1)

            color: tuple[int, int, int] = (
                COLOR_SETTINGS_SELECTED if is_selected else COLOR_SETTINGS_ITEM
            )

            # Active device indicator
            indicator: str = "●  " if is_active else "    "
            label: str = f"{indicator}{dev_name}"
            item_surf: pygame.Surface = self._font_settings_item.render(label, True, color)
            surface.blit(item_surf, (panel_x + 16, row_y + 6))

        # Scroll hints if list overflows
        if len(devices) > _SETTINGS_MAX_VISIBLE:
            if scroll_start > 0:
                up_surf: pygame.Surface = self._font_settings_hint.render(
                    "▲ more", True, COLOR_TEXT_MUTED
                )
                surface.blit(up_surf, (panel_x + _SETTINGS_PANEL_W - 60, list_top - 14))
            if scroll_start + visible_count < len(devices):
                down_surf: pygame.Surface = self._font_settings_hint.render(
                    "▼ more", True, COLOR_TEXT_MUTED
                )
                bottom_row_y: int = list_top + visible_count * _SETTINGS_ROW_H
                surface.blit(down_surf, (panel_x + _SETTINGS_PANEL_W - 60, bottom_row_y))

        # Bottom hint bar
        hint_y: int = panel_y + _SETTINGS_PANEL_H - 26
        pygame.draw.line(
            surface, COLOR_SETTINGS_BORDER,
            (panel_x + 1, hint_y), (panel_x + _SETTINGS_PANEL_W - 1, hint_y), 1
        )
        hints: str = "↑ ↓  navigate    Enter  confirm    Esc  cancel"
        hint_surf: pygame.Surface = self._font_settings_hint.render(hints, True, COLOR_TEXT_MUTED)
        hint_rect: pygame.Rect = hint_surf.get_rect(
            center=(panel_x + _SETTINGS_PANEL_W // 2, hint_y + 13)
        )
        surface.blit(hint_surf, hint_rect)