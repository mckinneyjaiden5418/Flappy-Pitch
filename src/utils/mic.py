"""Microphone pitch detection via autocorrelation."""

import math
import threading
from typing import Final

SILENCE_THRESHOLD: Final[float] = 0.02
MIN_FREQ: Final[float] = 80.0
MAX_FREQ: Final[float] = 1200.0
POLL_INTERVAL: Final[float] = 0.03  # seconds


def _autocorrelate(buf: list[float], sample_rate: int) -> float:
    """Estimate fundamental frequency from a buffer using autocorrelation.

    Args:
        buf (list[float]): Audio samples in range [-1.0, 1.0].
        sample_rate (int): Sample rate in Hz.

    Returns:
        float: Estimated frequency in Hz, or -1 if undetectable.
    """
    size: int = len(buf)

    rms: float = math.sqrt(sum(s * s for s in buf) / size)
    if rms < SILENCE_THRESHOLD:
        return -1.0

    # Trim leading/trailing silence
    r1: int = 0
    r2: int = size - 1
    for i in range(size // 2):
        if abs(buf[i]) >= 0.2:
            r1 = i
            break
    for i in range(1, size // 2):
        if abs(buf[size - i]) >= 0.2:
            r2 = size - i
            break

    trimmed: list[float] = buf[r1:r2]
    trim_len: int = len(trimmed)
    if trim_len < 2:
        return -1.0

    # Build autocorrelation array
    corr: list[float] = [0.0] * trim_len
    for i in range(trim_len):
        for j in range(trim_len - i):
            corr[i] += trimmed[j] * trimmed[j + i]

    # Find first local minimum (d), then find max after it
    d: int = 0
    while d < trim_len - 1 and corr[d] > corr[d + 1]:
        d += 1

    max_val: float = -1.0
    max_pos: int = -1
    for i in range(d, trim_len):
        if corr[i] > max_val:
            max_val = corr[i]
            max_pos = i

    if max_pos <= 0:
        return -1.0

    # Parabolic interpolation for sub-sample accuracy
    t0: float = float(max_pos)
    if 0 < max_pos < trim_len - 1:
        x1, x2, x3 = corr[max_pos - 1], corr[max_pos], corr[max_pos + 1]
        a: float = (x1 + x3 - 2 * x2) / 2
        b: float = (x3 - x1) / 2
        if a != 0:
            t0 -= b / (2 * a)

    return sample_rate / t0


class MicDetector:
    """Continuously detects pitch from the default microphone in a background thread."""

    def __init__(self) -> None:
        """Initialise the detector (does not start the stream yet)."""
        self._freq: float = -1.0
        self._lock: threading.Lock = threading.Lock()
        self._running: bool = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Open the microphone stream and begin pitch detection.

        Raises:
            ImportError: If sounddevice or numpy is not installed.
            RuntimeError: If the microphone cannot be opened.
        """
        import sounddevice as sd  # type: ignore[import]
        import numpy as np  # type: ignore[import]

        self._running = True

        def _callback(indata: "np.ndarray", frames: int, time: object, status: object) -> None:  # noqa: ARG001
            samples: list[float] = indata[:, 0].tolist()
            freq: float = _autocorrelate(buf=samples, sample_rate=44100)
            with self._lock:
                self._freq = freq

        self._stream = sd.InputStream(
            samplerate=44100,
            channels=1,
            blocksize=4096,
            callback=_callback,
            device=2, # 2 = Quadcast (MME). Hardcoded rn changing later.
        )
        self._stream.start()

    def stop(self) -> None:
        """Stop the microphone stream."""
        self._running = False
        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()

    @property
    def frequency(self) -> float:
        """Most recent detected frequency in Hz, or -1 if silent/undetectable.

        Returns:
            float: Frequency in Hz.
        """
        with self._lock:
            return self._freq
