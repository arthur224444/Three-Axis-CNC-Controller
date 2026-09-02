"""HTTP routes: machine control (authenticated) and health/introspection."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from cnc_api.auth import require_passphrase
from cnc_api.controller import CncController
from cnc_api.exceptions import RepeatLimitError
from cnc_api.models import (
    BatchRequest,
    CommandInfo,
    CommandRequest,
    CommandResponse,
    CommandsCatalogResponse,
    HealthResponse,
)
from cnc_api.protocol import COMMAND_SPECS, MESSAGE_LENGTH, MESSAGE_PADDING, VALID_CHARACTERS


def get_controller(request: Request) -> CncController:
    return request.app.state.controller


machine_router = APIRouter(dependencies=[Depends(require_passphrase)])
public_router = APIRouter()


def _repeat_or_default(body: CommandRequest | None) -> int:
    if body is None:
        return 1
    return body.repeat


def _send_repeated(
    controller: CncController,
    character: str,
    body: CommandRequest | None,
) -> CommandResponse:
    repeat = _repeat_or_default(body)
    max_repeat = min(controller.settings.max_repeat, controller.settings.max_command_length)
    if repeat > max_repeat:
        raise RepeatLimitError(
            f"repeat={repeat} exceeds the configured limit ({max_repeat})"
        )
    return controller.send_commands(character * repeat)


@machine_router.post(
    "/axis/x/forward",
    response_model=CommandResponse,
    summary="X axis +1 step (protocol X)",
)
def axis_x_forward(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "X", body)


@machine_router.post(
    "/axis/x/backward",
    response_model=CommandResponse,
    summary="X axis -1 step (protocol x)",
)
def axis_x_backward(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "x", body)


@machine_router.post(
    "/axis/x/forward/forced",
    response_model=CommandResponse,
    summary="X axis +1 forced step (protocol A)",
)
def axis_x_forward_forced(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "A", body)


@machine_router.post(
    "/axis/x/backward/forced",
    response_model=CommandResponse,
    summary="X axis -1 forced step (protocol a)",
)
def axis_x_backward_forced(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "a", body)


@machine_router.post(
    "/axis/y/forward",
    response_model=CommandResponse,
    summary="Y axis +1 step (protocol Y)",
)
def axis_y_forward(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "Y", body)


@machine_router.post(
    "/axis/y/backward",
    response_model=CommandResponse,
    summary="Y axis -1 step (protocol y)",
)
def axis_y_backward(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "y", body)


@machine_router.post(
    "/axis/y/forward/forced",
    response_model=CommandResponse,
    summary="Y axis +1 forced step (protocol B)",
)
def axis_y_forward_forced(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "B", body)


@machine_router.post(
    "/axis/y/backward/forced",
    response_model=CommandResponse,
    summary="Y axis -1 forced step (protocol b)",
)
def axis_y_backward_forced(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "b", body)


@machine_router.post(
    "/axis/z/forward",
    response_model=CommandResponse,
    summary="Z axis +1 step (protocol Z)",
)
def axis_z_forward(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "Z", body)


@machine_router.post(
    "/axis/z/backward",
    response_model=CommandResponse,
    summary="Z axis -1 step (protocol z)",
)
def axis_z_backward(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "z", body)


@machine_router.post(
    "/axis/z/forward/forced",
    response_model=CommandResponse,
    summary="Z axis +1 forced step (protocol C)",
)
def axis_z_forward_forced(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "C", body)


@machine_router.post(
    "/axis/z/backward/forced",
    response_model=CommandResponse,
    summary="Z axis -1 forced step (protocol c)",
)
def axis_z_backward_forced(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "c", body)


@machine_router.post(
    "/spindle/on",
    response_model=CommandResponse,
    summary="Spindle on (protocol S)",
)
def spindle_on(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "S", body)


@machine_router.post(
    "/spindle/off",
    response_model=CommandResponse,
    summary="Spindle off (protocol s)",
)
def spindle_off(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "s", body)


@machine_router.post(
    "/emergency-stop",
    response_model=CommandResponse,
    summary="Emergency stop (protocol E)",
)
def emergency_stop(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "E", body)


@machine_router.post(
    "/emergency-stop/reset",
    response_model=CommandResponse,
    summary="Reset emergency stop (protocol R)",
)
def emergency_stop_reset(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "R", body)


@machine_router.post(
    "/noop",
    response_model=CommandResponse,
    summary="No-op (protocol n)",
)
def noop(
    controller: Annotated[CncController, Depends(get_controller)],
    body: CommandRequest | None = None,
) -> CommandResponse:
    return _send_repeated(controller, "n", body)


@machine_router.post(
    "/commands",
    response_model=CommandResponse,
    summary="Send an arbitrary protocol string, split into 10-byte frames",
)
def batch_commands(
    body: BatchRequest,
    controller: Annotated[CncController, Depends(get_controller)],
) -> CommandResponse:
    return controller.send_commands(body.commands)


@public_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Serial-port liveness (no auth)",
)
def health(request: Request) -> HealthResponse:
    controller: CncController = request.app.state.controller
    open_ = controller.backend.is_open
    simulator = controller.settings.simulator
    if simulator:
        status = "ok"
        message = "Simulator backend is active; no Pico is required."
    elif open_:
        status = "ok"
        message = f"Serial port {controller.backend.port_label} is open."
    else:
        status = "degraded"
        message = (
            f"Serial port {controller.backend.port_label} is not open. "
            "Machine-control endpoints will return 503 until the Pico is connected."
        )
    return HealthResponse(
        status=status,
        serial_open=open_,
        simulator=simulator,
        port=controller.backend.port_label,
        message=message,
    )


@public_router.get(
    "/commands",
    response_model=CommandsCatalogResponse,
    summary="Supported protocol characters and HTTP paths (no auth)",
)
def list_commands() -> CommandsCatalogResponse:
    alphabet = "".join(spec.character for spec in COMMAND_SPECS)
    # Keep a stable unique alphabet listing matching VALID_CHARACTERS membership.
    assert set(alphabet) == VALID_CHARACTERS
    return CommandsCatalogResponse(
        message_length=MESSAGE_LENGTH,
        padding=MESSAGE_PADDING,
        alphabet=alphabet,
        commands=[
            CommandInfo(
                character=spec.character,
                path=spec.path,
                summary=spec.summary,
                description=spec.description,
            )
            for spec in COMMAND_SPECS
        ],
    )
