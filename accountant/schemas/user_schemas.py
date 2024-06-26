from accountant.root.utils.abstract_schema import AbstractModel
from pydantic import EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class User(AbstractModel):
    name: str
    email: EmailStr
    password: str


class UserProfile(User):
    user_uid: UUID
    date_created_utc: datetime


class UserExtendedProfile(UserProfile):
    dependents: Optional[list[UserProfile]] = []


class UserGroup(AbstractModel):
    user_uid: UUID
    user_group_uid: UUID


class UserGroupInvitationCreation(AbstractModel):
    email: list[EmailStr]
    user_group_uid: UUID


class UserGroupInvitation(AbstractModel):
    email: EmailStr
    user_group_uid: UUID


class UserGroupIVProfile(UserGroupInvitation):
    uid: UUID
    date_created_utc: datetime
