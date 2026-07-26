import msgspec
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.db.sqlalchemy import Device, DeviceType
from models.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate


def to_response(device: Device) -> DeviceResponse:
    return msgspec.convert(device, DeviceResponse, from_attributes=True)


async def get_type(session: AsyncSession, type_id: int) -> DeviceType | None:
    return await session.get(DeviceType, type_id)


async def get_device(session: AsyncSession, device_id: int) -> Device | None:
    return await session.get(Device, device_id)


async def get_device_with_type(session: AsyncSession, device_id: int) -> Device | None:
    result = await session.execute(
        select(Device).where(Device.id == device_id).options(selectinload(Device.type)),
    )
    return result.scalar_one_or_none()


async def list_devices(session: AsyncSession) -> list[Device]:
    result = await session.execute(select(Device).order_by(Device.id))
    return list(result.scalars())


async def create_device(session: AsyncSession, data: DeviceCreate) -> Device:
    device = Device(**msgspec.structs.asdict(data))
    session.add(device)
    await session.commit()
    await session.refresh(device)
    return device


async def update_device(session: AsyncSession, device: Device, data: DeviceUpdate) -> Device:
    for field, value in msgspec.structs.asdict(data).items():
        if value is not None:
            setattr(device, field, value)
    await session.commit()
    await session.refresh(device)
    return device
