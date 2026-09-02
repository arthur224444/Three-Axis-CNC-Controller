"""Static UI serving: GET / returns the Vite build when present."""

from __future__ import annotations

from fastapi.testclient import TestClient

import cnc_api.app as app_module
from cnc_api.app import create_app


def test_get_root_serves_html_when_index_present(
    tmp_path, monkeypatch, settings, simulator
) -> None:
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text(
        "<!DOCTYPE html><html><body>CNC UI</body></html>",
        encoding="utf-8",
    )
    monkeypatch.setattr(app_module, "STATIC_DIR", static)

    application = create_app(settings=settings, backend=simulator)
    with TestClient(application) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "CNC UI" in response.text

        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["status"] == "ok"
        assert body["simulator"] is True
        assert body["serial_open"] is True

        catalog = client.get("/commands")
        assert catalog.status_code == 200
        assert set(catalog.json()["alphabet"]) == set("XxYyZzAaBbCcSsERn")

        docs = client.get("/docs")
        assert docs.status_code == 200


def test_api_starts_when_static_ui_is_missing(
    tmp_path, monkeypatch, settings, simulator
) -> None:
    monkeypatch.setattr(app_module, "STATIC_DIR", tmp_path / "missing-static")

    application = create_app(settings=settings, backend=simulator)
    with TestClient(application) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        assert client.get("/").status_code == 404


def test_ui_assets_are_served_when_present(
    tmp_path, monkeypatch, settings, simulator
) -> None:
    static = tmp_path / "static"
    assets = static / "assets"
    assets.mkdir(parents=True)
    (static / "index.html").write_text("<html></html>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('cnc')", encoding="utf-8")
    monkeypatch.setattr(app_module, "STATIC_DIR", static)

    application = create_app(settings=settings, backend=simulator)
    with TestClient(application) as client:
        response = client.get("/assets/app.js")
        assert response.status_code == 200
        assert "console.log" in response.text
        assert client.get("/health").status_code == 200

