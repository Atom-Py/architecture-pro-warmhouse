from enum import StrEnum


class CommandStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    CONFIRMED = "confirmed"
    FAILED = "failed"
