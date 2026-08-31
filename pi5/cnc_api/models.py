"""Pydantic request and response bodies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """Optional body for single-command endpoints."""

    repeat: int = Field(
        default=1,
        ge=1,
        description="How many times to send this command. Frames of 10 are used automatically.",
    )


class BatchRequest(BaseModel):
    """Arbitrary-length protocol string, split into 10-byte frames by the server."""

    commands: str = Field(
        min_length=1,
        description="String of protocol characters, e.g. 'XYzzxxxZZZZZ'.",
    )


class CommandResponse(BaseModel):
    """Result of sending one or more frames to the Pico."""

    success: bool = Field(
        description="True only if every frame came back as ASCII '1' from the machine."
    )
    frames_sent: list[str] = Field(
        description="Exact 10-character ASCII frames written to the serial port, in order."
    )
    message: str
    commands_executed: int = Field(
        description=(
            "Count of original (unpadded) command characters in frames that the "
            "machine acknowledged with '1'."
        )
    )
    failing_frame_index: int | None = Field(
        default=None,
        description="0-based index of the first frame that returned '0', if any.",
    )
    machine_reply: str | None = Field(
        default=None,
        description="Last single-byte reply from the Pico ('1' or '0'), if one was received.",
    )


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    frames_sent: list[str] = Field(default_factory=list)
    character: str | None = None
    index: int | None = None


class HealthResponse(BaseModel):
    status: str
    serial_open: bool
    simulator: bool
    port: str
    message: str


class CommandInfo(BaseModel):
    character: str
    path: str
    method: str = "POST"
    summary: str
    description: str


class CommandsCatalogResponse(BaseModel):
    message_length: int
    padding: str
    alphabet: str
    commands: list[CommandInfo]
    batch_path: str = "/commands"
    batch_method: str = "POST"
