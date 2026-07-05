import msgspec
from robyn import Headers, Request, Response, SubRouter
from sqlalchemy.exc import IntegrityError

from infra.db.session_maker import session_maker
from models.schemas.command import CommandRequest
from models.schemas.device import DeviceCreate, DeviceUpdate
from models.schemas.errors import ErrorResponse
from services import commands, devices
from services.commands import UnsupportedCommandError

devices_router = SubRouter(prefix="/api/v1/devices")

_JSON = {"Content-Type": "application/json"}


def _parse_device_id(request: Request) -> int | None:
    try:
        return int(request.path_params["device_id"])
    except (KeyError, ValueError):
        return None


@devices_router.post("")
async def register_device(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]

    try:
        data = msgspec.json.decode(request.body, type=DeviceCreate, strict=False)
    except msgspec.ValidationError as error:
        return Response(
            status_code=400,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(code="validation_error", message=str(error))),
        )

    async with session_maker() as session:
        if await devices.get_type(session, data.type_id) is None:
            return Response(
                status_code=400,
                headers=Headers(_JSON),
                body=encoder.encode(
                    ErrorResponse(code="unknown_device_type", message=f"device type {data.type_id} not found"),
                ),
            )
        try:
            device = await devices.create_device(session, data)
        except IntegrityError:
            return Response(
                status_code=409,
                headers=Headers(_JSON),
                body=encoder.encode(
                    ErrorResponse(code="already_registered", message=f"device {data.serial_number} is already registered"),
                ),
            )

    return Response(
        status_code=201,
        headers=Headers(_JSON),
        body=encoder.encode(devices.to_response(device)),
    )


@devices_router.get("")
async def list_devices(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]

    async with session_maker() as session:
        items = await devices.list_devices(session)

    return Response(
        status_code=200,
        headers=Headers(_JSON),
        body=encoder.encode([devices.to_response(device) for device in items]),
    )


@devices_router.get("/:device_id")
async def get_device(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]

    device_id = _parse_device_id(request)
    if device_id is None:
        return Response(
            status_code=400,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(code="validation_error", message="invalid device id")),
        )

    async with session_maker() as session:
        device = await devices.get_device(session, device_id)
        if device is None:
            return Response(
                status_code=404,
                headers=Headers(_JSON),
                body=encoder.encode(ErrorResponse(code="device_not_found", message=f"device {device_id} not found")),
            )

    return Response(
        status_code=200,
        headers=Headers(_JSON),
        body=encoder.encode(devices.to_response(device)),
    )


@devices_router.patch("/:device_id")
async def update_device(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]

    device_id = _parse_device_id(request)
    if device_id is None:
        return Response(
            status_code=400,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(code="validation_error", message="invalid device id")),
        )

    try:
        data = msgspec.json.decode(request.body, type=DeviceUpdate, strict=False)
    except msgspec.ValidationError as error:
        return Response(
            status_code=400,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(code="validation_error", message=str(error))),
        )

    async with session_maker() as session:
        device = await devices.get_device(session, device_id)
        if device is None:
            return Response(
                status_code=404,
                headers=Headers(_JSON),
                body=encoder.encode(ErrorResponse(code="device_not_found", message=f"device {device_id} not found")),
            )
        device = await devices.update_device(session, device, data)

    return Response(
        status_code=200,
        headers=Headers(_JSON),
        body=encoder.encode(devices.to_response(device)),
    )


@devices_router.post("/:device_id/commands")
async def send_command(request: Request, global_dependencies) -> Response:
    encoder = global_dependencies["msgspec_json_encoder"]

    device_id = _parse_device_id(request)
    if device_id is None:
        return Response(
            status_code=400,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(code="validation_error", message="invalid device id")),
        )

    try:
        data = msgspec.json.decode(request.body, type=CommandRequest, strict=False)
    except msgspec.ValidationError as error:
        return Response(
            status_code=400,
            headers=Headers(_JSON),
            body=encoder.encode(ErrorResponse(code="validation_error", message=str(error))),
        )

    async with session_maker() as session:
        device = await devices.get_device_with_type(session, device_id)
        if device is None:
            return Response(
                status_code=404,
                headers=Headers(_JSON),
                body=encoder.encode(ErrorResponse(code="device_not_found", message=f"device {device_id} not found")),
            )
        try:
            command = await commands.create_and_publish(session, device, data)
        except UnsupportedCommandError as error:
            return Response(
                status_code=422,
                headers=Headers(_JSON),
                body=encoder.encode(ErrorResponse(code="unsupported_command", message=str(error))),
            )

    return Response(
        status_code=202,
        headers=Headers(_JSON),
        body=encoder.encode(commands.to_response(command)),
    )
