from sqlalchemy.dialects.postgresql import insert

from infra.db.session_maker import session_maker
from models.db.sqlalchemy import DeviceType

DEFAULT_DEVICE_TYPES = [
    {"name": "temperature_sensor", "capabilities": [], "description": "Temperature sensor"},
    {"name": "heating_relay", "capabilities": ["turn_on", "turn_off"], "description": "Heating relay"},
    {"name": "light_relay", "capabilities": ["turn_on", "turn_off"], "description": "Light relay"},
    {"name": "gate", "capabilities": ["open", "close"], "description": "Automatic gate"},
    {"name": "camera", "capabilities": ["turn_on", "turn_off"], "description": "Surveillance camera"},
]


async def seed_device_types() -> None:
    async with session_maker() as session:
        statement = (
            insert(DeviceType)
            .values(DEFAULT_DEVICE_TYPES)
            .on_conflict_do_nothing(index_elements=[DeviceType.name])
        )
        await session.execute(statement)
        await session.commit()
