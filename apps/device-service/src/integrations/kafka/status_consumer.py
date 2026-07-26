import asyncio
import logging

import msgspec
from aiokafka import AIOKafkaConsumer
from sqlalchemy import update

from config.settings import settings
from infra.db.session_maker import session_maker
from models.db.sqlalchemy import Device, DeviceCommand
from models.enums.command_status import CommandStatus
from models.schemas.events import DeviceStatusEvent

logger = logging.getLogger(__name__)

_task: asyncio.Task | None = None


async def _apply(event: DeviceStatusEvent) -> None:
    async with session_maker() as session:
        await session.execute(
            update(Device).where(Device.id == event.device_id).values(status=event.status),
        )
        if event.command_id is not None:
            await session.execute(
                update(DeviceCommand)
                .where(DeviceCommand.id == event.command_id)
                .values(status=CommandStatus.CONFIRMED),
            )
        await session.commit()


async def _consume() -> None:
    consumer = AIOKafkaConsumer(
        settings.KAFKA.STATUS_TOPIC,
        bootstrap_servers=settings.KAFKA.BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA.CONSUMER_GROUP,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    logger.info("device-status consumer started")
    try:
        async for message in consumer:
            try:
                event = msgspec.json.decode(message.value, type=DeviceStatusEvent, strict=False)
                await _apply(event)
            except Exception:
                logger.exception("failed to process device-status message")
    finally:
        await consumer.stop()


def start() -> None:
    # Robyn runs one persistent event loop per process (see robyn.processpool.spawn_process),
    # so a plain background task survives for the lifetime of the service
    global _task
    _task = asyncio.create_task(_consume(), name="device-status-consumer")


async def stop() -> None:
    global _task
    if _task is None:
        return
    _task.cancel()
    try:
        await _task
    except asyncio.CancelledError:
        pass
    _task = None
