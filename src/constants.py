"""Game-wide constants."""

from typing import Final

# Window
WINDOW_TITLE: Final[str] = "Flappy Pitch"
WINDOW_W: Final[int] = 720
WINDOW_H: Final[int] = 520
FPS: Final[int] = 60

# Colors (RGB)
COLOR_SKY: Final[tuple[int, int, int]] = (214, 239, 247)
COLOR_STAFF_LINE: Final[tuple[int, int, int]] = (170, 170, 170)
COLOR_STAFF_LABEL: Final[tuple[int, int, int]] = (200, 200, 200)
COLOR_PIPE: Final[tuple[int, int, int]] = (92, 184, 92)
COLOR_PIPE_DARK: Final[tuple[int, int, int]] = (76, 174, 76)
COLOR_BIRD_BODY: Final[tuple[int, int, int]] = (245, 166, 35)
COLOR_BIRD_WING: Final[tuple[int, int, int]] = (232, 136, 26)
COLOR_BIRD_EYE: Final[tuple[int, int, int]] = (255, 255, 255)
COLOR_BIRD_PUPIL: Final[tuple[int, int, int]] = (51, 51, 51)
COLOR_BIRD_BEAK: Final[tuple[int, int, int]] = (245, 166, 35)
COLOR_WHITE: Final[tuple[int, int, int]] = (255, 255, 255)
COLOR_BLACK: Final[tuple[int, int, int]] = (0, 0, 0)
COLOR_OVERLAY: Final[tuple[int, int, int, int]] = (0, 0, 0, 115)
COLOR_GREEN: Final[tuple[int, int, int]] = (92, 184, 92)
COLOR_RED: Final[tuple[int, int, int]] = (220, 53, 69)
COLOR_GOLD: Final[tuple[int, int, int]] = (255, 193, 7)
COLOR_TEXT_MUTED: Final[tuple[int, int, int]] = (120, 120, 120)

# Staff layout
STAFF_TOP: Final[int] = 100
STAFF_BOTTOM: Final[int] = 400
STAFF_LINE_COUNT: Final[int] = 5

# MIDI pitch range shown on screen
MIDI_MIN: Final[int] = 45  # A2
MIDI_MAX: Final[int] = 75  # D#5

# Pipe
PIPE_WIDTH: Final[int] = 60
PIPE_GAP: Final[int] = 100
PIPE_SPEED: Final[float] = 2.5
PIPE_SPAWN_INTERVAL: Final[int] = 90  # frames

# Bird
BIRD_X: Final[int] = 120
BIRD_LERP: Final[float] = 0.12  # smoothing factor toward target pitch Y

# Scoring
SCORE_X: Final[int] = 20
SCORE_Y: Final[int] = 20

# Keyboard note mapping: key -> (note name, MIDI number)
KEY_NOTE_MAP: Final[dict[str, tuple[str, int]]] = {
    "a": ("C3", 48),
    "s": ("E3", 52),
    "d": ("G3", 55),
    "f": ("C4", 60),
    "g": ("E4", 64),
    "h": ("G4", 67),
    "j": ("C5", 72),
}
