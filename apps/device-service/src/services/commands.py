import msgspec
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from integrations.kafka.producer import producer
from models.db.sqlalchemy import Device, DeviceCommand
from models.enums.command_status import CommandStatus
from models.schemas.command import CommandRequest, CommandResponse
from models.schemas.events import DeviceCommandEvent


class UnsupportedCommandError(Exception):
    def __init__(self, type_name: str, command: str) -> None:
        super().__init__(f"device type '{type_name}' does not support command '{command}'")


def to_response(command: DeviceCommand) -> CommandResponse:
    return msgspec.convert(command, CommandResponse, from_attributes=True)


async def create_and_publish(session: AsyncSession, device: Device, data: CommandRequest) -> DeviceCommand:
    if data.command not in device.type.capabilities:
        raise UnsupportedCommandError(device.type.name, data.command)

    command = DeviceCommand(device_id=device.id, command=data.command, payload=data.payload)
    session.add(command)
    await session.commit()
    await session.refresh(command)

    await producer.publish(
        settings.KAFKA.COMMANDS_TOPIC,
        DeviceCommandEvent(
            command_id=command.id,
            device_id=device.id,
            sensor_id=device.sensor_id,
            command=command.command,
            payload=command.payload,
        ),
    )

    command.status = CommandStatus.SENT
    await session.commit()
    await session.refresh(command)
    return command
