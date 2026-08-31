"""FastAPI application factory."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from cnc_api.config import Settings
from cnc_api.controller import CncController
from cnc_api.exceptions import ApiError
from cnc_api.protocol import InvalidCommandError
from cnc_api.routes import machine_router, public_router
from cnc_api.serial_backend import SerialBackend, create_backend

logger = logging.getLogger("cnc_api")

# pi5/static — resolved from this package, not the process working directory.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _load_settings(settings: Settings | None) -> Settings:
    if settings is not None:
        return settings
    try:
        return Settings()
    except ValidationError as exc:
        sys.stderr.write(
            "CNC API refused to start: required settings are missing or invalid.\n"
            "Set CNC_PASSPHRASE (and copy pi5/.env.example to pi5/.env if needed).\n"
            f"{exc}\n"
        )
        raise SystemExit(1) from exc


def create_app(
    settings: Settings | None = None,
    backend: SerialBackend | None = None,
) -> FastAPI:
    """Build the API. Pass settings/backend in tests; production loads from the env."""

    resolved_settings = _load_settings(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        serial = backend if backend is not None else create_backend(resolved_settings)
        controller = CncController(serial, resolved_settings)
        app.state.settings = resolved_settings
        app.state.controller = controller
        try:
            serial.open()
        except Exception:
            logger.exception(
                "Failed to open serial backend at startup; "
                "machine-control endpoints will return 503 until it is available"
            )
        yield
        serial.close()

    application = FastAPI(
        title="Three Axis CNC Controller",
        description=(
            "HTTP API on the Raspberry Pi 5 that translates requests into "
            "10-byte USB-serial command frames for the Pico 2 W firmware."
        ),
        lifespan=lifespan,
    )

    @application.exception_handler(ApiError)
    async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_body())

    @application.exception_handler(InvalidCommandError)
    async def invalid_command_handler(
        _request: Request, exc: InvalidCommandError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "invalid_command",
                "message": str(exc),
                "frames_sent": [],
                "character": exc.character,
                "index": exc.index,
            },
        )

    application.include_router(public_router)
    application.include_router(machine_router)
    _mount_ui(application)
    return application


def _mount_ui(application: FastAPI) -> None:
    """Serve the Vite production build from pi5/static, if it has been built.

    API routes are registered first so /health, /commands, /docs, and the
    machine-control paths are never swallowed. Missing index.html is a no-op
    so a laptop without a frontend build can still run the API and tests.
    """
    static_dir = STATIC_DIR.resolve()
    index = static_dir / "index.html"
    if not index.is_file():
        logger.info(
            "Control UI not found at %s; GET / will not serve the frontend. "
            "From frontend/, run npm run build.",
            index,
        )
        return

    @application.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        return FileResponse(index, media_type="text/html")

    assets = static_dir / "assets"
    if assets.is_dir():
        application.mount("/assets", StaticFiles(directory=assets), name="frontend_assets")
