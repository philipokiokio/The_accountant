from accountant.root.utils.abstract_schema import AbstractModel
from pydantic import EmailStr, conint
from datetime import datetime
from uuid import UUID
from typing import Optional


class User(AbstractModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(AbstractModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserProfile(User):
    user_uid: UUID
    date_created_utc: datetime


class UserExtendedProfile(UserProfile):
    dependents: Optional[list[UserProfile]] = []


class UserGroup(AbstractModel):
    owner_uid: UUID
    user_group_uid: UUID


class UserGroupMember(AbstractModel):
    user_uid: UUID
    user_group_uid: UUID


class UserGroupMemberProfile(AbstractModel):
    user: Optional[UserProfile] = None


class PaginatedUserGroupProfile(AbstractModel):
    result_set: list[UserGroupMemberProfile] = []
    result_size: conint(ge=0) = 0


class UserGroupInvitationCreation(AbstractModel):
    email: EmailStr
    user_group_uid: UUID


class UserGroupInvitation(AbstractModel):
    email: EmailStr
    user_group_uid: UUID


class UserGroupIVProfile(UserGroupInvitation):
    uid: UUID
    date_created_utc: datetime


class PaginatedUserGroupIVProfile(AbstractModel):
    result_set: list[UserGroupIVProfile] = []
    result_size: conint(ge=0) = 0


class TokenData(AbstractModel):
    user_uid: UUID
