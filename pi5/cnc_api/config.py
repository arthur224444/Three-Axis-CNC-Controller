"""Application settings loaded from environment variables and an optional .env file."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PI5_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """CNC API configuration.

    All fields are prefixed with ``CNC_`` in the environment
    (e.g. ``passphrase`` is read from ``CNC_PASSPHRASE``).
    """

    model_config = SettingsConfigDict(
        env_prefix="CNC_",
        env_file=(_PI5_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    passphrase: str = Field(min_length=1)
    serial_port: str = "/dev/ttyACM0"
    serial_baud: int = 115200
    serial_open_delay_seconds: float = Field(default=2.0, ge=0.0)
    message_timeout_per_command: float = Field(default=1.0, gt=0.0)
    max_command_length: int = Field(default=500, ge=1)
    max_repeat: int = Field(default=100, ge=1)
    simulator: bool = False
    lock_wait_seconds: float = Field(default=60.0, ge=0.0)

    @property
    def frame_timeout_seconds(self) -> float:
        """Read timeout for one 10-byte frame (~1s per command in the frame)."""
        return self.message_timeout_per_command * 10
