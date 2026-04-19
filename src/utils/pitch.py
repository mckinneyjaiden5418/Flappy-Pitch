"""Pitch / MIDI utility functions."""

import math

from src.constants import BB_TRANSPOSE, MIDI_MAX, MIDI_MIN, STAFF_BOTTOM, STAFF_TOP

NOTE_NAMES: tuple[str, ...] = (
    "C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"
)


def midi_to_y(midi: int) -> float:
    """Convert a concert MIDI note number to a Y pixel position on screen.

    Higher MIDI values map to higher on screen (lower Y).

    Args:
        midi (int): Concert MIDI note number.

    Returns:
        float: Y coordinate in pixels.
    """
    t: float = (midi - MIDI_MIN) / (MIDI_MAX - MIDI_MIN)
    return STAFF_BOTTOM - t * (STAFF_BOTTOM - STAFF_TOP)


def freq_to_midi(freq: float) -> int:
    """Convert a frequency in Hz to the nearest concert MIDI note number.

    Args:
        freq (float): Frequency in Hz.

    Returns:
        int: Nearest concert MIDI note number.
    """
    return round(12 * math.log2(freq / 440) + 69)


def midi_to_name(midi: int) -> str:
    """Convert a concert MIDI note number to a written Bb note name (e.g. 'D4').

    The returned name is what a Bb instrument player reads on the staff —
    a major second (2 semitones) above concert pitch.

    Args:
        midi (int): Concert MIDI note number.

    Returns:
        str: Written Bb note name with octave (e.g. 'D4', 'F#3').
    """
    written_midi: int = concert_to_written(midi)
    octave: int = (written_midi // 12) - 1
    name: str = NOTE_NAMES[written_midi % 12]
    return f"{name}{octave}"


def concert_to_written(midi: int) -> int:
    """Convert a concert MIDI number to the written (transposed) MIDI for a Bb instrument.

    A Bb instrument player reads a note that is BB_TRANSPOSE semitones higher
    than the concert pitch that sounds.

    Args:
        midi (int): Concert MIDI note number.

    Returns:
        int: Written MIDI note number.
    """
    return midi + BB_TRANSPOSE


def written_to_concert(midi: int) -> int:
    """Convert a written (transposed) MIDI number back to concert pitch.

    Args:
        midi (int): Written MIDI note number for a Bb instrument.

    Returns:
        int: Concert MIDI note number.
    """
    return midi - BB_TRANSPOSE


def clamp_midi(midi: int) -> int:
    """Clamp a concert MIDI value to the visible pitch range.

    Args:
        midi (int): Raw concert MIDI note number.

    Returns:
        int: Clamped concert MIDI note number within [MIDI_MIN, MIDI_MAX].
    """
    return max(MIDI_MIN, min(MIDI_MAX, midi))