"""HTTP API tests against the simulated serial backend."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cnc_api.serial_backend import SimulatedSerial

TEST_PASSPHRASE = "test-secret"


def _frames(client: TestClient) -> list[str]:
    backend = client.app.state.controller.backend
    assert isinstance(backend, SimulatedSerial)
    return [frame.decode("ascii") for frame in backend.frames_written]


def test_health_requires_no_auth(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["serial_open"] is True
    assert body["simulator"] is True
    assert body["status"] == "ok"


def test_commands_catalog_requires_no_auth(client: TestClient) -> None:
    response = client.get("/commands")
    assert response.status_code == 200
    body = response.json()
    characters = {item["character"] for item in body["commands"]}
    assert characters == set("XxYyZzAaBbCcSsERn")
    assert body["message_length"] == 10
    assert body["padding"] == "n"


def test_auth_rejected_when_header_missing(client: TestClient) -> None:
    response = client.post("/axis/x/forward")
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"] == "unauthorized"
    assert _frames(client) == []


def test_auth_rejected_when_passphrase_wrong(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/axis/x/forward",
        headers={"X-CNC-Passphrase": "nope"},
    )
    assert response.status_code == 401
    assert _frames(client) == []


def test_auth_rejected_when_passphrase_only_in_query(client: TestClient) -> None:
    response = client.post(f"/axis/x/forward?passphrase={TEST_PASSPHRASE}")
    assert response.status_code == 401
    assert _frames(client) == []


def test_auth_accepted_via_header(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/axis/x/forward", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["frames_sent"] == ["Xnnnnnnnnn"]
    assert body["commands_executed"] == 1
    assert _frames(client) == ["Xnnnnnnnnn"]


def test_auth_accepted_via_bearer(client: TestClient) -> None:
    response = client.post(
        "/noop",
        headers={"Authorization": f"Bearer {TEST_PASSPHRASE}"},
    )
    assert response.status_code == 200
    assert response.json()["frames_sent"] == ["nnnnnnnnnn"]


def test_single_command_repeat_chunks_into_ten_byte_frames(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/axis/x/forward",
        headers=auth_headers,
        json={"repeat": 12},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["frames_sent"] == ["XXXXXXXXXX", "XXnnnnnnnn"]
    assert body["commands_executed"] == 12
    assert _frames(client) == ["XXXXXXXXXX", "XXnnnnnnnn"]


def test_batch_long_string_is_chunked_and_padded(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    commands = "XYzzxxxZZZZZ"
    response = client.post(
        "/commands",
        headers=auth_headers,
        json={"commands": commands},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["frames_sent"] == ["XYzzxxxZZZ", "ZZnnnnnnnn"]
    assert body["commands_executed"] == 12
    assert all(len(frame) == 10 for frame in body["frames_sent"])
    assert _frames(client) == body["frames_sent"]


def test_invalid_character_rejected_before_serial(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/commands",
        headers=auth_headers,
        json={"commands": "XYQzz"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "invalid_command"
    assert body["character"] == "Q"
    assert body["index"] == 2
    assert "index 2" in body["message"]
    assert _frames(client) == []


def test_emergency_stop_character_is_accepted_in_batch(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/commands",
        headers=auth_headers,
        json={"commands": "sE"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["frames_sent"] == ["sEnnnnnnnn"]
    assert body["commands_executed"] == 2
    assert _frames(client) == ["sEnnnnnnnn"]


def test_zero_reply_stops_and_reports_failing_frame(
    client: TestClient,
    auth_headers: dict[str, str],
    simulator: SimulatedSerial,
) -> None:
    simulator.queue_reply(b"1")
    simulator.queue_reply(b"0")
    response = client.post(
        "/commands",
        headers=auth_headers,
        json={"commands": "XXXXXXXXXXYYYY"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["machine_reply"] == "0"
    assert body["failing_frame_index"] == 1
    assert body["commands_executed"] == 10
    assert body["frames_sent"] == ["XXXXXXXXXX", "YYYYnnnnnn"]
    assert _frames(client) == ["XXXXXXXXXX", "YYYYnnnnnn"]


def test_zero_reply_on_first_frame_sends_nothing_further(
    client: TestClient,
    auth_headers: dict[str, str],
    simulator: SimulatedSerial,
) -> None:
    simulator.queue_reply(b"0")
    response = client.post(
        "/commands",
        headers=auth_headers,
        json={"commands": "XYzzxxxZZZZZ"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["failing_frame_index"] == 0
    assert body["commands_executed"] == 0
    assert body["frames_sent"] == ["XYzzxxxZZZ"]
    assert _frames(client) == ["XYzzxxxZZZ"]


def test_timeout_returns_504_and_flushes_buffer(
    client: TestClient,
    auth_headers: dict[str, str],
    simulator: SimulatedSerial,
) -> None:
    simulator.queue_reply(b"")
    simulator.queue_reply(b"1")
    response = client.post("/axis/y/forward", headers=auth_headers)
    assert response.status_code == 504
    body = response.json()
    assert body["error"] == "serial_timeout"
    assert body["frames_sent"] == ["Ynnnnnnnnn"]
    assert not simulator.reply_queue


def test_serial_unavailable_returns_503(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    backend = client.app.state.controller.backend
    assert isinstance(backend, SimulatedSerial)
    backend.close()

    original_open = backend.open

    def refuse_open() -> None:
        raise RuntimeError("device gone")

    backend.open = refuse_open  # type: ignore[method-assign]
    try:
        response = client.post("/spindle/off", headers=auth_headers)
    finally:
        backend.open = original_open  # type: ignore[method-assign]

    assert response.status_code == 503
    assert response.json()["error"] == "serial_unavailable"


def test_forced_and_spindle_paths_map_to_protocol_characters(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    expected = [
        ("/axis/x/forward/forced", "A"),
        ("/axis/x/backward/forced", "a"),
        ("/axis/y/forward/forced", "B"),
        ("/axis/z/backward/forced", "c"),
        ("/spindle/on", "S"),
        ("/emergency-stop", "E"),
        ("/emergency-stop/reset", "R"),
    ]
    for path, character in expected:
        client.app.state.controller.backend.frames_written.clear()
        response = client.post(path, headers=auth_headers)
        assert response.status_code == 200, path
        padded = character.ljust(10, "n")
        assert response.json()["frames_sent"] == [padded]
        assert _frames(client) == [padded]
