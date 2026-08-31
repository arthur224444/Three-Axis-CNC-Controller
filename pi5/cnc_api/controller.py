"""Owns the serial port and serialises all request/response frames."""

from __future__ import annotations

import logging
import threading

from cnc_api.config import Settings
from cnc_api.exceptions import (
    LockBusyError,
    PayloadTooLongError,
    SerialTimeoutError,
    SerialUnavailableError,
)
from cnc_api.models import CommandResponse
from cnc_api.protocol import (
    encode_frame,
    original_command_count,
    split_into_frames,
    validate_commands,
)
from cnc_api.serial_backend import SerialBackend

logger = logging.getLogger("cnc_api.controller")


class CncController:
    """Translate validated command strings into serial frames.

    pyserial is blocking, so callers should be sync FastAPI ``def`` endpoints
    (run in the threadpool). All access is serialised with a ``threading.Lock``:
    overlapping writes would corrupt the strictly request/response protocol.
    """

    def __init__(self, backend: SerialBackend, settings: Settings) -> None:
        self.backend = backend
        self.settings = settings
        self._lock = threading.Lock()

    def send_commands(self, commands: str) -> CommandResponse:
        validate_commands(commands)
        if len(commands) > self.settings.max_command_length:
            raise PayloadTooLongError(
                f"Command string length {len(commands)} exceeds "
                f"CNC_MAX_COMMAND_LENGTH ({self.settings.max_command_length})"
            )

        frames = split_into_frames(commands)
        acquired = self._lock.acquire(timeout=self.settings.lock_wait_seconds)
        if not acquired:
            raise LockBusyError(
                "Another command is using the serial port; retry after it finishes "
                f"(waited {self.settings.lock_wait_seconds:.0f}s)"
            )

        try:
            self._ensure_open()
            return self._send_frames(commands, frames)
        finally:
            self._lock.release()

    def _ensure_open(self) -> None:
        if self.backend.is_open:
            return
        try:
            self.backend.open()
        except SerialUnavailableError:
            raise
        except Exception as exc:
            raise SerialUnavailableError(
                f"Could not open serial port {self.backend.port_label}: {exc}"
            ) from exc
        if not self.backend.is_open:
            raise SerialUnavailableError(
                f"Serial port {self.backend.port_label} is not connected"
            )

    def _send_frames(self, commands: str, frames: list[str]) -> CommandResponse:
        sent: list[str] = []
        executed = 0
        last_reply: str | None = None

        for frame_index, frame in enumerate(frames):
            data = encode_frame(frame)
            logger.info("Sending frame %s/%s: %s", frame_index + 1, len(frames), frame)
            self.backend.write_frame(data)
            sent.append(frame)

            reply = self.backend.read_reply()
            if not reply:
                self.backend.reset_input_buffer()
                raise SerialTimeoutError(
                    "Timed out waiting for the Pico's 1-byte reply after sending "
                    f"frame {frame_index} ({frame!r}). Input buffer flushed.",
                    frames_sent=sent,
                )

            last_reply = reply.decode("ascii", errors="replace")
            if reply == b"1":
                executed += original_command_count(len(commands), frame_index)
                continue

            if reply == b"0":
                return CommandResponse(
                    success=False,
                    frames_sent=sent,
                    message=(
                        f"Pico replied '0' for frame {frame_index} ({frame!r}). "
                        f"{executed} command(s) from earlier frames succeeded. "
                        "No further frames were sent."
                    ),
                    commands_executed=executed,
                    failing_frame_index=frame_index,
                    machine_reply="0",
                )

            self.backend.reset_input_buffer()
            return CommandResponse(
                success=False,
                frames_sent=sent,
                message=(
                    f"Unexpected reply {reply!r} for frame {frame_index} ({frame!r}). "
                    f"{executed} command(s) from earlier frames succeeded. "
                    "Input buffer flushed; no further frames were sent."
                ),
                commands_executed=executed,
                failing_frame_index=frame_index,
                machine_reply=last_reply,
            )

        return CommandResponse(
            success=True,
            frames_sent=sent,
            message=(
                f"All {len(frames)} frame(s) acknowledged by the Pico "
                f"({executed} command(s) executed)."
            ),
            commands_executed=executed,
            failing_frame_index=None,
            machine_reply=last_reply,
        )
