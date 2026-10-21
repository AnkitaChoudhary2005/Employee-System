from sqlalchemy import Boolean, Column, Integer, String

from src.utlis.db import Base


class UserModel(Base):
    __tablename__ = "user"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    name = Column(String(120), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(String(255), nullable=False)

    role = Column(
        String(20),
        nullable=False,
        default="employee"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )