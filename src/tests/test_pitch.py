"""Tests for pitch utility functions."""

import pytest

from src.utils.pitch import clamp_midi, freq_to_midi, midi_to_name, midi_to_y
from src.constants import MIDI_MIN, MIDI_MAX, STAFF_TOP, STAFF_BOTTOM


class TestMidiToY:
    """Tests for midi_to_y."""

    def test_min_midi_maps_to_staff_bottom(self) -> None:
        """MIDI_MIN should map to STAFF_BOTTOM (bottom of staff)."""
        assert midi_to_y(MIDI_MIN) == pytest.approx(STAFF_BOTTOM)

    def test_max_midi_maps_to_staff_top(self) -> None:
        """MIDI_MAX should map to STAFF_TOP (top of staff)."""
        assert midi_to_y(MIDI_MAX) == pytest.approx(STAFF_TOP)

    def test_middle_c_maps_to_centre(self) -> None:
        """Middle C (60) should land roughly in the middle of the staff."""
        y: float = midi_to_y(60)
        assert STAFF_TOP < y < STAFF_BOTTOM

    def test_higher_midi_gives_lower_y(self) -> None:
        """Higher MIDI values should give lower Y coordinates (higher on screen)."""
        assert midi_to_y(65) < midi_to_y(55)


class TestFreqToMidi:
    """Tests for freq_to_midi."""

    def test_a4_is_midi_69(self) -> None:
        """440 Hz (A4) must return MIDI 69."""
        assert freq_to_midi(440.0) == 69

    def test_middle_c_is_midi_60(self) -> None:
        """261.63 Hz (C4) must return MIDI 60."""
        assert freq_to_midi(261.63) == 60


class TestMidiToName:
    """Tests for midi_to_name."""

    def test_middle_c(self) -> None:
        """MIDI 60 should be C4."""
        assert midi_to_name(60) == "C4"

    def test_a4(self) -> None:
        """MIDI 69 should be A4."""
        assert midi_to_name(69) == "A4"


class TestClampMidi:
    """Tests for clamp_midi."""

    def test_value_below_min_is_clamped(self) -> None:
        assert clamp_midi(MIDI_MIN - 10) == MIDI_MIN

    def test_value_above_max_is_clamped(self) -> None:
        assert clamp_midi(MIDI_MAX + 10) == MIDI_MAX

    def test_value_within_range_is_unchanged(self) -> None:
        assert clamp_midi(60) == 60
