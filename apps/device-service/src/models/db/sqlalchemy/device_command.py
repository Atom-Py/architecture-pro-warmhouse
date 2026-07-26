import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.db.sqlalchemy.base import Base
from models.enums.command_status import CommandStatus


class DeviceCommand(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", name="fk_device_commands_device_id", ondelete="CASCADE"),
        nullable=False,
    )
    command: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[CommandStatus] = mapped_column(
        Enum(CommandStatus, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        server_default=CommandStatus.PENDING.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __tablename__ = "device_commands"
    __table_args__ = (Index("ix_device_commands_device_id", device_id),)
