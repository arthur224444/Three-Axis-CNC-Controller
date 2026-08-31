"""Run with: python -m cnc_api  (from the pi5/ directory)."""

from __future__ import annotations

import logging

import uvicorn

from cnc_api.app import create_app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    uvicorn.run(
        create_app(),
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
