from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.db.sqlalchemy.base import Base


class DeviceType(Base):
    id: Mapped[int] = mapped_column(BigInteger, nullable=False, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor: Mapped[str] = mapped_column(String(100), nullable=False, server_default="warmhouse")
    protocol: Mapped[str] = mapped_column(String(50), nullable=False, server_default="mqtt")
    capabilities: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default="[]")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    __tablename__ = "device_types"
    __table_args__ = (Index("uq_device_types_name", name, unique=True),)
