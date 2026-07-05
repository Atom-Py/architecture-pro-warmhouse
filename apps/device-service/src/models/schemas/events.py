import uuid
from datetime import datetime

from msgspec import Struct

from models.enums.device_status import DeviceStatus


class DeviceCommandEvent(Struct, gc=False):
    command_id: uuid.UUID
    device_id: int
    sensor_id: int | None
    command: str
    payload: dict | None = None


class DeviceStatusEvent(Struct, gc=False):
    device_id: int
    status: DeviceStatus
    command_id: uuid.UUID | None = None
    occurred_at: datetime | None = None
