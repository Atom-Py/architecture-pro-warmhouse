from datetime import datetime

from msgspec import Struct

from models.enums.device_status import DeviceStatus


class DeviceCreate(Struct, forbid_unknown_fields=True, gc=False):
    serial_number: str
    type_id: int
    house_id: int
    name: str
    location: str | None = None
    sensor_id: int | None = None


class DeviceUpdate(Struct, forbid_unknown_fields=True, omit_defaults=True, gc=False):
    name: str | None = None
    location: str | None = None
    house_id: int | None = None


class DeviceResponse(Struct, gc=False):
    id: int
    serial_number: str
    type_id: int
    house_id: int
    sensor_id: int | None
    name: str
    location: str | None
    status: DeviceStatus
    registered_at: datetime
