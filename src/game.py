"""Core game loop and state machine."""

from enum import Enum, auto
from typing import Final

import pygame

from src.bird import Bird
from src.constants import (
    COLOR_SKY,
    FPS,
    KEY_NOTE_MAP,
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
from src.utils.mic import MicDetector
from src.utils.pitch import clamp_midi, freq_to_midi, midi_to_name, midi_to_y

_MIN_AUDIBLE_FREQ: Final[float] = 80.0
_MAX_AUDIBLE_FREQ: Final[float] = 1200.0


class GameState(Enum):
    """All possible game states."""

    IDLE = auto()
    PLAYING = auto()
    DEAD = auto()


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

        self._held_keys: set[str] = set()
        self._mic_mode: bool = False
        self._mic: MicDetector = MicDetector()

        self._active_note: str | None = None

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

            elif event.type == pygame.KEYUP:
                key: str = pygame.key.name(event.key).lower()
                self._held_keys.discard(key)

    def _on_key_down(self, key_code: int) -> None:
        """React to a key press event.

        Args:
            key_code (int): pygame key constant.
        """
        key: str = pygame.key.name(key_code).lower()

        if key == "m":
            self._toggle_mic()
            return

        if key == "r":
            self._reset()
            return

        if key in KEY_NOTE_MAP and not self._mic_mode:
            self._held_keys.add(key)
            if self._state in (GameState.IDLE, GameState.DEAD):
                self._reset()

    # ------------------------------------------------------------------
    # Internal — mic
    # ------------------------------------------------------------------

    def _toggle_mic(self) -> None:
        """Toggle between keyboard and microphone input modes."""
        if self._mic_mode:
            self._mic.stop()
            self._mic_mode = False
        else:
            try:
                self._mic.start()
                self._mic_mode = True
                if self._state in (GameState.IDLE, GameState.DEAD):
                    self._reset()
            except Exception:  # noqa: BLE001
                pass  # Mic unavailable; stay in keyboard mode

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
        """Determine the bird's target Y from the active input source.

        Returns:
            float | None: Target Y in pixels, or None if no note is active.
        """
        if self._mic_mode:
            return self._get_mic_target_y()
        return self._get_keyboard_target_y()

    def _get_keyboard_target_y(self) -> float | None:
        """Return target Y from the currently held keyboard note.

        Returns:
            float | None: Target Y, or None if no note key is held.
        """
        for key in KEY_NOTE_MAP:
            if key in self._held_keys:
                note_name, midi = KEY_NOTE_MAP[key]
                self._active_note = note_name
                return midi_to_y(midi)
        self._active_note = None
        return None

    def _get_mic_target_y(self) -> float | None:
        """Return target Y from the microphone pitch detector.

        Returns:
            float | None: Target Y, or None if pitch is inaudible.
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
            # Drift downward slowly when silent
            self._bird.set_target(self._bird.y + 3)

        self._bird.update()

        # Spawn pipes
        if self._frame % PIPE_SPAWN_INTERVAL == 0:
            self._pipes.append(Pipe(gap_center_y=Pipe.random_gap_center()))

        # Update pipes, check scoring and collision
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

        mode_label: str = "mic" if self._mic_mode else "keyboard"
        self._hud.draw_score(self._screen, self._score, self._best)
        self._hud.draw_note(self._screen, self._active_note, mode_label)
        self._hud.draw_keybinds(self._screen)

        if self._state == GameState.IDLE:
            self._hud.draw_overlay(
                self._screen,
                "Flappy Pitch",
                "Hold a key to fly  |  R to restart  |  M to toggle mic",
            )
        elif self._state == GameState.DEAD:
            self._hud.draw_overlay(
                self._screen,
                f"Score: {self._score}",
                "R to play again  |  M to toggle mic",
            )

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Internal — cleanup
    # ------------------------------------------------------------------

    def _quit(self) -> None:
        """Clean up resources and exit the application."""
        if self._mic_mode:
            self._mic.stop()
        pygame.quit()
        raise SystemExit
