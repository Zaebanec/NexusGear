from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import BigInteger

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )