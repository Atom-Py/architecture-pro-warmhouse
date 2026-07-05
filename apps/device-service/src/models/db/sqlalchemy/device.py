from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.db.sqlalchemy.base import Base
from models.enums.device_status import DeviceStatus

if TYPE_CHECKING:
    from models.db.sqlalchemy.device_type import DeviceType


class Device(Base):
    id: Mapped[int] = mapped_column(BigInteger, nullable=False, primary_key=True, autoincrement=True)

    serial_number: Mapped[str] = mapped_column(String(100), nullable=False)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("device_types.id", name="fk_devices_type_id", ondelete="RESTRICT"),
        nullable=False,
    )
    house_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sensor_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # monolith sensors.id, transition period only

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        server_default=DeviceStatus.OFFLINE.value,
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    type: Mapped["DeviceType"] = relationship(lazy="raise")

    __tablename__ = "devices"
    __table_args__ = (
        Index("uq_devices_serial_number", serial_number, unique=True),
        Index("ix_devices_house_id", house_id),
    )
