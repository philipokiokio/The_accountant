from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from accountant.root.utils.abstract_base import AbstractBase


class User(AbstractBase):
    __tablename__ = "users"
    user_uid = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, server_default=str(False))
    is_alive = Column(Boolean, nullable=True)
    user_group = relationship("UserGroup", back_populates="user")


class UserGroup(AbstractBase):
    __tablename__ = "user_group"
    user_group_uid = Column(UUID, primary_key=True, default=uuid4)
    owner_uid = Column(
        UUID, ForeignKey("users.user_uid", ondelete="CASCADE"), nullable=False
    )
    user_ugroup = relationship("UserUGroup", back_populates="user_group")
    user = relationship("User")


class UserUGroup(AbstractBase):
    __tablename__ = "user_user_group"

    user_group_uid = Column(
        UUID,
        ForeignKey("user_group.user_group_uid", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    user_uid = Column(
        UUID,
        ForeignKey("users.user_uid", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    user_group = relationship("UserGroup")
    user = relationship("User")


class UserGroupInvitation(AbstractBase):
    __tablename__ = "user_group_invitation"
    uid = Column(UUID, primary_key=True, default=uuid4)
    user_group_uid = Column(
        UUID, ForeignKey("user_group.user_group_uid"), default=uuid4
    )
    email = Column(String, nullable=False)
    is_accepted = Column(
        Boolean,
        nullable=False,
    )
