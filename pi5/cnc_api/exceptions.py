"""HTTP-mapped application errors with a consistent JSON body."""

from __future__ import annotations


class ApiError(Exception):
    """Base class for errors that become JSON HTTP responses."""

    status_code: int = 500
    error: str = "internal_error"

    def __init__(
        self,
        message: str,
        *,
        frames_sent: list[str] | None = None,
        character: str | None = None,
        index: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.frames_sent = frames_sent or []
        self.character = character
        self.index = index

    def to_body(self) -> dict[str, object]:
        body: dict[str, object] = {
            "success": False,
            "error": self.error,
            "message": self.message,
            "frames_sent": self.frames_sent,
        }
        if self.character is not None:
            body["character"] = self.character
        if self.index is not None:
            body["index"] = self.index
        return body


class UnauthorizedError(ApiError):
    status_code = 401
    error = "unauthorized"


class SerialUnavailableError(ApiError):
    status_code = 503
    error = "serial_unavailable"


class SerialTimeoutError(ApiError):
    status_code = 504
    error = "serial_timeout"


class LockBusyError(ApiError):
    status_code = 409
    error = "busy"


class PayloadTooLongError(ApiError):
    status_code = 422
    error = "payload_too_long"


class RepeatLimitError(ApiError):
    status_code = 422
    error = "repeat_limit"
