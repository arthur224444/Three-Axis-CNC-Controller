"""Serial command alphabet and 10-byte framing helpers.

Matches pico2_w/main.c: the firmware reads exactly SEQUENCE_LENGTH (10) bytes,
executes each character in order, then writes a single ASCII reply byte.
"""

from __future__ import annotations

from dataclasses import dataclass

MESSAGE_LENGTH = 10
MESSAGE_PADDING = "n"

# Characters the firmware recognises. Anything else is rejected by the API
# before it reaches the serial port (unrecognised chars also drop the spindle).
VALID_CHARACTERS = frozenset("XxYyZzAaBbCcSsRn")


@dataclass(frozen=True)
class CommandSpec:
    character: str
    path: str
    summary: str
    description: str


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        "X",
        "/axis/x/forward",
        "X axis +1 step",
        "Emergency-stop-aware: +1 step on X. Refused by firmware while emergency stop is active.",
    ),
    CommandSpec(
        "x",
        "/axis/x/backward",
        "X axis -1 step",
        "Emergency-stop-aware: -1 step on X. Refused by firmware while emergency stop is active.",
    ),
    CommandSpec(
        "A",
        "/axis/x/forward/forced",
        "X axis +1 forced step",
        "Forced: +1 step on X even while emergency stop is active (jog off a tripped limit).",
    ),
    CommandSpec(
        "a",
        "/axis/x/backward/forced",
        "X axis -1 forced step",
        "Forced: -1 step on X even while emergency stop is active (jog off a tripped limit).",
    ),
    CommandSpec(
        "Y",
        "/axis/y/forward",
        "Y axis +1 step",
        "Emergency-stop-aware: +1 step on Y. Refused by firmware while emergency stop is active.",
    ),
    CommandSpec(
        "y",
        "/axis/y/backward",
        "Y axis -1 step",
        "Emergency-stop-aware: -1 step on Y. Refused by firmware while emergency stop is active.",
    ),
    CommandSpec(
        "B",
        "/axis/y/forward/forced",
        "Y axis +1 forced step",
        "Forced: +1 step on Y even while emergency stop is active (jog off a tripped limit).",
    ),
    CommandSpec(
        "b",
        "/axis/y/backward/forced",
        "Y axis -1 forced step",
        "Forced: -1 step on Y even while emergency stop is active (jog off a tripped limit).",
    ),
    CommandSpec(
        "Z",
        "/axis/z/forward",
        "Z axis +1 step",
        "Emergency-stop-aware: +1 step on Z. Refused by firmware while emergency stop is active.",
    ),
    CommandSpec(
        "z",
        "/axis/z/backward",
        "Z axis -1 step",
        "Emergency-stop-aware: -1 step on Z. Refused by firmware while emergency stop is active.",
    ),
    CommandSpec(
        "C",
        "/axis/z/forward/forced",
        "Z axis +1 forced step",
        "Forced: +1 step on Z even while emergency stop is active (jog off a tripped limit).",
    ),
    CommandSpec(
        "c",
        "/axis/z/backward/forced",
        "Z axis -1 forced step",
        "Forced: -1 step on Z even while emergency stop is active (jog off a tripped limit).",
    ),
    CommandSpec(
        "S",
        "/spindle/on",
        "Spindle on",
        "Turn the spindle on. Ignored by firmware if emergency stop is active.",
    ),
    CommandSpec(
        "s",
        "/spindle/off",
        "Spindle off",
        "Turn the spindle off.",
    ),
    CommandSpec(
        "R",
        "/emergency-stop/reset",
        "Reset emergency stop",
        "Clear the firmware emergency-stop latch so normal moves can resume.",
    ),
    CommandSpec(
        "n",
        "/noop",
        "No-op",
        "No-op / padding character. The firmware does nothing for this step.",
    ),
)

PATH_TO_CHARACTER: dict[str, str] = {spec.path: spec.character for spec in COMMAND_SPECS}


class InvalidCommandError(Exception):
    """A command string contained a character the firmware does not accept."""

    def __init__(self, character: str, index: int) -> None:
        self.character = character
        self.index = index
        super().__init__(
            f"Invalid command character {character!r} at index {index}"
        )


def validate_commands(commands: str) -> None:
    """Reject any character outside the firmware alphabet, naming index."""
    for index, character in enumerate(commands):
        if character not in VALID_CHARACTERS:
            raise InvalidCommandError(character, index)


def split_into_frames(commands: str) -> list[str]:
    """Split a command string into consecutive 10-character frames.

    The final frame is right-padded with ``n`` so every frame is exactly
    MESSAGE_LENGTH characters, matching ``message.ljust(10, "n")[:10]``.
    """
    if not commands:
        raise ValueError("command string must not be empty")

    frames: list[str] = []
    for start in range(0, len(commands), MESSAGE_LENGTH):
        chunk = commands[start : start + MESSAGE_LENGTH]
        frames.append(chunk.ljust(MESSAGE_LENGTH, MESSAGE_PADDING)[:MESSAGE_LENGTH])
    return frames


def encode_frame(frame: str) -> bytes:
    """Encode a 10-character ASCII frame. Raises if the length is wrong."""
    if len(frame) != MESSAGE_LENGTH:
        raise ValueError(
            f"frame must be exactly {MESSAGE_LENGTH} characters, got {len(frame)}"
        )
    if any(ch not in VALID_CHARACTERS for ch in frame):
        raise ValueError(f"frame contains an invalid character: {frame!r}")
    return frame.encode("ascii")


def original_command_count(total_commands: int, frame_index: int) -> int:
    """How many characters of the original string sit in this frame."""
    start = frame_index * MESSAGE_LENGTH
    remaining = total_commands - start
    if remaining <= 0:
        return 0
    return min(MESSAGE_LENGTH, remaining)
