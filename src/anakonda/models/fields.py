import datetime

from sqlalchemy.orm import Mapped, mapped_column


def IntField(**kwargs) -> Mapped[int]:
    return mapped_column(int, **kwargs)


def CharField(length: int = 255, **kwargs) -> Mapped[str]:
    return mapped_column(str, length=length, **kwargs)


def TextField(**kwargs) -> Mapped[str]:
    return mapped_column(str, **kwargs)


def DateTimeField(
    default=datetime.datetime.utcnow, **kwargs
) -> Mapped[datetime.datetime]:
    return mapped_column(datetime.datetime, default=default, **kwargs)


def BoolField(default=False, **kwargs) -> Mapped[bool]:
    return mapped_column(bool, default=default, **kwargs)
