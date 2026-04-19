"""Core game loop and state machine."""

from enum import Enum, auto
from typing import Final

import pygame

from src.bird import Bird
from src.constants import (
    COLOR_SKY,
    FPS,
    MIDI_MAX,
    MIDI_MIN,
    PIPE_SPAWN_INTERVAL,
    WINDOW_H,
    WINDOW_TITLE,
    WINDOW_W,
)
from src.hud import HUD
from src.pipe import Pipe
from src.staff import Staff
from src.utils.mic import MicDetector, query_input_devices
from src.utils.pitch import clamp_midi, freq_to_midi, midi_to_name, midi_to_y

_MIN_AUDIBLE_FREQ: Final[float] = 80.0
_MAX_AUDIBLE_FREQ: Final[float] = 1200.0


class GameState(Enum):
    """All possible game states."""

    IDLE = auto()
    PLAYING = auto()
    DEAD = auto()
    SETTINGS = auto()


class Game:
    """Main game class — owns the loop, entities, and state transitions."""

    def __init__(self) -> None:
        """Initialise pygame, create all subsystems, and set state to IDLE."""
        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(WINDOW_TITLE)
        self._clock: pygame.time.Clock = pygame.time.Clock()

        self._staff: Staff = Staff()
        self._hud: HUD = HUD()
        self._bird: Bird = Bird()
        self._pipes: list[Pipe] = []

        self._state: GameState = GameState.IDLE
        self._score: int = 0
        self._best: int = 0
        self._frame: int = 0

        self._mic: MicDetector = MicDetector()
        self._active_note: str | None = None

        self._settings_devices: list[tuple[int, str]] = []
        self._settings_selected: int = 0
        self._state_before_settings: GameState = GameState.IDLE

        try:
            self._mic.start()
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the main game loop. Blocks until the window is closed."""
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self._clock.tick(FPS)

    # ------------------------------------------------------------------
    # Internal — events
    # ------------------------------------------------------------------

    def _handle_events(self) -> None:
        """Process all pending pygame events for this frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            elif event.type == pygame.KEYDOWN:
                self._on_key_down(event.key)

    def _on_key_down(self, key_code: int) -> None:
        """React to a key press event.

        Args:
            key_code (int): pygame key constant.
        """
        if self._state == GameState.SETTINGS:
            self._on_settings_key(key_code)
            return

        key: str = pygame.key.name(key_code).lower()

        if key == "s":
            self._open_settings()
            return

        if key == "r":
            self._reset()
            return

    def _on_settings_key(self, key_code: int) -> None:
        """Handle key input while in the SETTINGS state.

        Args:
            key_code (int): pygame key constant.
        """
        if key_code == pygame.K_ESCAPE:
            self._close_settings(confirm=False)

        elif key_code in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._close_settings(confirm=True)

        elif key_code == pygame.K_UP:
            self._settings_selected = max(0, self._settings_selected - 1)

        elif key_code == pygame.K_DOWN:
            self._settings_selected = min(
                len(self._settings_devices) - 1,
                self._settings_selected + 1,
            )

    # ------------------------------------------------------------------
    # Internal — settings
    # ------------------------------------------------------------------

    def _open_settings(self) -> None:
        """Load input devices and transition to the SETTINGS state."""
        try:
            self._settings_devices = query_input_devices()
        except Exception:  # noqa: BLE001
            return

        if not self._settings_devices:
            return

        active: int = self._mic.device
        self._settings_selected = next(
            (i for i, (idx, _) in enumerate(self._settings_devices) if idx == active),
            0,
        )

        self._state_before_settings = self._state
        self._state = GameState.SETTINGS

    def _close_settings(self, *, confirm: bool) -> None:
        """Exit the SETTINGS state, optionally applying the selected device.

        Args:
            confirm (bool): If True, restart the mic with the selected device.
                If False, discard the selection and return unchanged.
        """
        if confirm and self._settings_devices:
            new_device: int = self._settings_devices[self._settings_selected][0]
            if new_device != self._mic.device:
                try:
                    self._mic.restart(new_device)
                except Exception:  # noqa: BLE001
                    pass

        self._state = self._state_before_settings

    # ------------------------------------------------------------------
    # Internal — game logic
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        """Reset all game entities and counters for a new run."""
        self._bird = Bird()
        self._pipes = []
        self._score = 0
        self._frame = 0
        self._active_note = None
        self._state = GameState.PLAYING
        self._pipes.append(Pipe(gap_center_y=Pipe.random_gap_center()))

    def _get_target_y(self) -> float | None:
        """Determine the bird's target Y from the microphone pitch detector.

        Returns:
            float | None: Target Y in pixels, or None if pitch is inaudible.
        """
        freq: float = self._mic.frequency
        if freq < _MIN_AUDIBLE_FREQ or freq > _MAX_AUDIBLE_FREQ:
            self._active_note = None
            return None

        midi: int = clamp_midi(freq_to_midi(freq))
        self._active_note = midi_to_name(midi)
        return midi_to_y(midi)

    def _update(self) -> None:
        """Run one frame of game logic."""
        if self._state != GameState.PLAYING:
            return

        self._frame += 1

        target_y: float | None = self._get_target_y()
        if target_y is not None:
            self._bird.set_target(target_y)
        else:
            self._bird.set_target(self._bird.y + 3)

        self._bird.update()

        if self._frame % PIPE_SPAWN_INTERVAL == 0:
            self._pipes.append(Pipe(gap_center_y=Pipe.random_gap_center()))

        for pipe in self._pipes:
            pipe.update()
            if not pipe.scored and pipe.x + 60 < self._bird.x:
                pipe.scored = True
                self._score += 1
                self._best = max(self._best, self._score)
            if pipe.collides_with(self._bird.rect):
                self._state = GameState.DEAD
                return

        self._pipes = [p for p in self._pipes if not p.is_off_screen()]

        if self._bird.is_out_of_bounds():
            self._state = GameState.DEAD

    # ------------------------------------------------------------------
    # Internal — rendering
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        """Render the full frame to the display."""
        self._screen.fill(COLOR_SKY)
        self._staff.draw(self._screen)

        for pipe in self._pipes:
            pipe.draw(self._screen)

        self._bird.draw(self._screen)

        self._hud.draw_score(self._screen, self._score, self._best)
        self._hud.draw_note(self._screen, self._active_note)
        self._hud.draw_hint_bar(self._screen, "R = restart  |  S = mic device")

        if self._state == GameState.IDLE:
            self._hud.draw_overlay(
                self._screen,
                "Flappy Pitch",
                "Hum or sing to fly  |  R = start  |  S = mic device",
            )
        elif self._state == GameState.DEAD:
            self._hud.draw_overlay(
                self._screen,
                f"Score: {self._score}",
                "R = play again  |  S = mic device",
            )
        elif self._state == GameState.SETTINGS:
            self._hud.draw_settings_overlay(
                self._screen,
                self._settings_devices,
                self._settings_selected,
                self._mic.device,
            )

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Internal — cleanup
    # ------------------------------------------------------------------

    def _quit(self) -> None:
        """Clean up resources and exit the application."""
        self._mic.stop()
        pygame.quit()
        raise SystemExit