"""Shared TestClient wired to the simulated serial backend."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cnc_api.app import create_app
from cnc_api.config import Settings
from cnc_api.serial_backend import SimulatedSerial

TEST_PASSPHRASE = "test-secret"


@pytest.fixture
def simulator() -> SimulatedSerial:
    return SimulatedSerial()


@pytest.fixture
def settings() -> Settings:
    return Settings(
        passphrase=TEST_PASSPHRASE,
        simulator=True,
        serial_port="/dev/null",
        max_command_length=50,
        max_repeat=30,
        lock_wait_seconds=1.0,
        serial_open_delay_seconds=0.0,
    )


@pytest.fixture
def client(settings: Settings, simulator: SimulatedSerial) -> TestClient:
    app = create_app(settings=settings, backend=simulator)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-CNC-Passphrase": TEST_PASSPHRASE}
