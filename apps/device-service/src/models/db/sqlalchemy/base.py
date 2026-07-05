from sqlalchemy.orm import DeclarativeBase

from models.db.sqlalchemy.mixins.repr import ReprMixin


class Base(ReprMixin, DeclarativeBase):
    pass
