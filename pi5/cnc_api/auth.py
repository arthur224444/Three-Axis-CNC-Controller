"""Shared-passphrase authentication for machine-control endpoints."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Header, Request

from cnc_api.config import Settings
from cnc_api.exceptions import UnauthorizedError


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def _extract_passphrase(
    x_cnc_passphrase: str | None,
    authorization: str | None,
) -> str | None:
    if x_cnc_passphrase is not None and x_cnc_passphrase != "":
        return x_cnc_passphrase
    if authorization is None:
        return None
    scheme, separator, token = authorization.partition(" ")
    if separator and scheme.lower() == "bearer" and token:
        return token
    return None


def _passphrase_matches(provided: str, expected: str) -> bool:
    provided_b = provided.encode("utf-8")
    expected_b = expected.encode("utf-8")
    if len(provided_b) != len(expected_b):
        secrets.compare_digest(expected_b, expected_b)
        return False
    return secrets.compare_digest(provided_b, expected_b)


def require_passphrase(
    x_cnc_passphrase: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    """Accept X-CNC-Passphrase or Authorization: Bearer <pass>. Never query-string."""
    provided = _extract_passphrase(x_cnc_passphrase, authorization)
    if provided is None or not _passphrase_matches(provided, settings.passphrase):
        raise UnauthorizedError(
            "Missing or invalid passphrase. Send header X-CNC-Passphrase "
            "or Authorization: Bearer <passphrase>."
        )
