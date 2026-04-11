"""Pitch / MIDI utility functions."""

from src.constants import MIDI_MAX, MIDI_MIN, STAFF_BOTTOM, STAFF_TOP

NOTE_NAMES: tuple[str, ...] = (
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
)


def midi_to_y(midi: int) -> float:
    """Convert a MIDI note number to a Y pixel position on screen.

    Higher MIDI values map to higher on screen (lower Y).

    Args:
        midi (int): MIDI note number.

    Returns:
        float: Y coordinate in pixels.
    """
    t: float = (midi - MIDI_MIN) / (MIDI_MAX - MIDI_MIN)
    return STAFF_BOTTOM - t * (STAFF_BOTTOM - STAFF_TOP)


def freq_to_midi(freq: float) -> int:
    """Convert a frequency in Hz to the nearest MIDI note number.

    Args:
        freq (float): Frequency in Hz.

    Returns:
        int: Nearest MIDI note number.
    """
    import math
    return round(12 * math.log2(freq / 440) + 69)


def midi_to_name(midi: int) -> str:
    """Convert a MIDI note number to a human-readable note name (e.g. 'C4').

    Args:
        midi (int): MIDI note number.

    Returns:
        str: Note name with octave.
    """
    octave: int = (midi // 12) - 1
    name: str = NOTE_NAMES[midi % 12]
    return f"{name}{octave}"


def clamp_midi(midi: int) -> int:
    """Clamp a MIDI value to the visible pitch range.

    Args:
        midi (int): Raw MIDI note number.

    Returns:
        int: Clamped MIDI note number within [MIDI_MIN, MIDI_MAX].
    """
    return max(MIDI_MIN, min(MIDI_MAX, midi))
