import uuid
from datetime import datetime

from msgspec import Struct

from models.enums.command_status import CommandStatus


class CommandRequest(Struct, forbid_unknown_fields=True, gc=False):
    command: str
    payload: dict | None = None


class CommandResponse(Struct, gc=False):
    id: uuid.UUID
    device_id: int
    command: str
    payload: dict | None
    status: CommandStatus
    created_at: datetime
