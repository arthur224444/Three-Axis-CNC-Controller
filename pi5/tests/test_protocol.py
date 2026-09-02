"""Unit tests for framing and command validation (no HTTP)."""

from __future__ import annotations

import pytest

from cnc_api.protocol import (
    InvalidCommandError,
    encode_frame,
    original_command_count,
    split_into_frames,
    validate_commands,
)


def test_validate_accepts_full_alphabet() -> None:
    validate_commands("XxYyZzAaBbCcSsERn")


def test_validate_rejects_unknown_character_with_index() -> None:
    with pytest.raises(InvalidCommandError) as exc_info:
        validate_commands("XYQzz")
    assert exc_info.value.character == "Q"
    assert exc_info.value.index == 2


def test_split_single_command_pads_to_ten() -> None:
    assert split_into_frames("X") == ["Xnnnnnnnnn"]


def test_split_exactly_ten_is_one_unpadded_frame() -> None:
    commands = "XYzzxxxZZZ"
    assert split_into_frames(commands) == [commands]


def test_split_long_string_chunks_and_pads_remainder() -> None:
    commands = "XYzzxxxZZZZZ"
    frames = split_into_frames(commands)
    assert frames == ["XYzzxxxZZZ", "ZZnnnnnnnn"]
    assert all(len(frame) == 10 for frame in frames)


def test_encode_frame_rejects_wrong_length() -> None:
    with pytest.raises(ValueError):
        encode_frame("X")


def test_original_command_count_excludes_padding() -> None:
    assert original_command_count(12, 0) == 10
    assert original_command_count(12, 1) == 2
    assert original_command_count(12, 2) == 0
