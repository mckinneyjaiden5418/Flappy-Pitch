"""Microphone pitch detection via autocorrelation."""

import math
import threading
from typing import Final

SILENCE_THRESHOLD: Final[float] = 0.02
MIN_FREQ: Final[float] = 80.0
MAX_FREQ: Final[float] = 1200.0
POLL_INTERVAL: Final[float] = 0.03  # seconds

_DEFAULT_DEVICE: Final[int] = 2  # HyperX QuadCast 2 (MME index)


def query_input_devices() -> list[tuple[int, str]]:
    """Return all available audio input devices as (index, name) pairs.

    Only devices with at least one input channel are included.

    Returns:
        list[tuple[int, str]]: Ordered list of (device_index, device_name).

    Raises:
        ImportError: If sounddevice is not installed.
    """
    import sounddevice as sd  # type: ignore[import]

    devices: list[tuple[int, str]] = []
    for i, info in enumerate(sd.query_devices()):
        if info["max_input_channels"] > 0:  # type: ignore[index]
            devices.append((i, info["name"]))  # type: ignore[index]
    return devices


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
    """Continuously detects pitch from a microphone input in a background thread."""

    def __init__(self, device: int = _DEFAULT_DEVICE) -> None:
        """Initialise the detector with a chosen device index.

        Does not open the stream until :meth:`start` is called.

        Args:
            device (int): sounddevice device index to use. Defaults to the
                HyperX QuadCast 2 (index 2, MME).
        """
        self._device: int = device
        self._freq: float = -1.0
        self._lock: threading.Lock = threading.Lock()
        self._running: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def device(self) -> int:
        """Currently configured device index.

        Returns:
            int: sounddevice device index.
        """
        return self._device

    @property
    def frequency(self) -> float:
        """Most recent detected frequency in Hz, or -1 if silent/undetectable.

        Returns:
            float: Frequency in Hz.
        """
        with self._lock:
            return self._freq

    def start(self) -> None:
        """Open the microphone stream and begin pitch detection.

        Args:
            None

        Raises:
            ImportError: If sounddevice or numpy is not installed.
            RuntimeError: If the microphone cannot be opened.
        """
        import sounddevice as sd  # type: ignore[import]

        self._running = True

        def _callback(
            indata: "object",
            frames: int,  # noqa: ARG001
            time: object,  # noqa: ARG001
            status: object,  # noqa: ARG001
        ) -> None:
            import numpy as np  # type: ignore[import]

            samples: list[float] = indata[:, 0].tolist()  # type: ignore[index]
            freq: float = _autocorrelate(buf=samples, sample_rate=44100)
            with self._lock:
                self._freq = freq

        self._stream = sd.InputStream(
            samplerate=44100,
            channels=1,
            blocksize=4096,
            callback=_callback,
            device=self._device,
        )
        self._stream.start()

    def stop(self) -> None:
        """Stop the microphone stream and reset the detected frequency."""
        self._running = False
        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()
        with self._lock:
            self._freq = -1.0

    def restart(self, device: int) -> None:
        """Switch to a different input device.

        Stops the current stream (if running), updates the device index,
        and starts a new stream immediately.

        Args:
            device (int): New sounddevice device index.

        Raises:
            ImportError: If sounddevice or numpy is not installed.
            RuntimeError: If the new device cannot be opened.
        """
        self.stop()
        self._device = device
        self.start()