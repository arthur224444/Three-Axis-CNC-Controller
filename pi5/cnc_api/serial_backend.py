"""Serial port backends: real USB CDC and an in-process simulator."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections import deque

from cnc_api.config import Settings
from cnc_api.exceptions import SerialUnavailableError
from cnc_api.protocol import MESSAGE_LENGTH

logger = logging.getLogger("cnc_api.serial")


class SerialBackend(ABC):
    """Common interface for talking to the Pico (or a fake)."""

    @abstractmethod
    def open(self) -> None:
        """Open the port. The Pico resets on open; real backends must wait."""

    @abstractmethod
    def close(self) -> None:
        """Close the port. Called once at process shutdown."""

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """Whether the port is currently open."""

    @property
    @abstractmethod
    def port_label(self) -> str:
        """Human-readable port name for /health."""

    @abstractmethod
    def write_frame(self, data: bytes) -> None:
        """Write exactly one 10-byte frame. Must not be called concurrently."""

    @abstractmethod
    def read_reply(self) -> bytes:
        """Block until one reply byte arrives, or return empty bytes on timeout."""

    @abstractmethod
    def reset_input_buffer(self) -> None:
        """Discard unread input so a late reply cannot poison the next request."""


def _require_ten_bytes(data: bytes) -> None:
    if len(data) != MESSAGE_LENGTH:
        raise ValueError(
            f"refusing to write a frame of {len(data)} bytes; must be {MESSAGE_LENGTH}"
        )


class PyserialBackend(SerialBackend):
    """USB CDC serial connection to the Pico 2 W, held open for process lifetime."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._ser: object | None = None

    @property
    def port_label(self) -> str:
        return self._settings.serial_port

    @property
    def is_open(self) -> bool:
        ser = self._ser
        return bool(ser is not None and getattr(ser, "is_open", False))

    def open(self) -> None:
        if self.is_open:
            return
        try:
            import serial
        except ImportError as exc:
            raise SerialUnavailableError(
                "pyserial is not installed; cannot open the CNC serial port"
            ) from exc

        try:
            self._ser = serial.Serial(
                port=self._settings.serial_port,
                baudrate=self._settings.serial_baud,
                timeout=self._settings.frame_timeout_seconds,
            )
        except serial.SerialException as exc:
            self._ser = None
            raise SerialUnavailableError(
                f"Could not open serial port {self._settings.serial_port}: {exc}"
            ) from exc

        logger.info(
            "Opened %s at %s baud; waiting %.1fs for Pico reset",
            self._settings.serial_port,
            self._settings.serial_baud,
            self._settings.serial_open_delay_seconds,
        )
        time.sleep(self._settings.serial_open_delay_seconds)

    def close(self) -> None:
        ser = self._ser
        self._ser = None
        if ser is not None:
            try:
                ser.close()  # type: ignore[union-attr]
            except Exception:
                logger.exception("Error closing serial port")

    def write_frame(self, data: bytes) -> None:
        _require_ten_bytes(data)
        if not self.is_open:
            raise SerialUnavailableError("Serial port is not open")
        assert self._ser is not None
        self._ser.write(data)  # type: ignore[union-attr]

    def read_reply(self) -> bytes:
        if not self.is_open:
            raise SerialUnavailableError("Serial port is not open")
        assert self._ser is not None
        return self._ser.read(1)  # type: ignore[union-attr]

    def reset_input_buffer(self) -> None:
        ser = self._ser
        if ser is not None and getattr(ser, "is_open", False):
            ser.reset_input_buffer()  # type: ignore[union-attr]


class SimulatedSerial(SerialBackend):
    """Drop-in serial fake: logs frames and replies '1' unless replies are queued."""

    def __init__(self) -> None:
        self._open = False
        self.frames_written: list[bytes] = []
        self.reply_queue: deque[bytes] = deque()

    @property
    def port_label(self) -> str:
        return "simulator"

    @property
    def is_open(self) -> bool:
        return self._open

    def open(self) -> None:
        self._open = True
        logger.info("CNC serial simulator opened (no Pico attached)")

    def close(self) -> None:
        self._open = False

    def write_frame(self, data: bytes) -> None:
        _require_ten_bytes(data)
        if not self._open:
            raise SerialUnavailableError("Simulator serial port is not open")
        self.frames_written.append(data)
        logger.info("Simulator received frame %r", data.decode("ascii"))

    def read_reply(self) -> bytes:
        if not self._open:
            raise SerialUnavailableError("Simulator serial port is not open")
        if self.reply_queue:
            return self.reply_queue.popleft()
        return b"1"

    def reset_input_buffer(self) -> None:
        self.reply_queue.clear()

    def queue_reply(self, reply: bytes) -> None:
        """Test helper: next read_reply() returns this instead of b'1'."""
        self.reply_queue.append(reply)


def create_backend(settings: Settings) -> SerialBackend:
    if settings.simulator:
        return SimulatedSerial()
    return PyserialBackend(settings)
