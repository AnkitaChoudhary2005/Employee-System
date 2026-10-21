from sqlalchemy import Column, ForeignKey, Integer, String

from src.utlis.db import Base


class ManagerModel(Base):
    __tablename__ = "manager"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String(120),
        nullable=False
    )

    department = Column(
        String(100),
        nullable=False,
        default="General"
    )
