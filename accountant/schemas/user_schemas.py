from accountant.root.utils.abstract_schema import AbstractModel
from pydantic import EmailStr, conint
from datetime import datetime
from uuid import UUID
from typing import ClassVar, Optional


class Login(AbstractModel):
    email: str
    password: str


class User(Login):
    name: str


class UserUpdate(AbstractModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_verified: Optional[bool] = None
    is_alive: Optional[bool] = None
    added_to_user_group_uid: Optional[UUID] = None


class UserProfile(User):
    user_uid: UUID
    is_verified: bool
    date_created_utc: datetime
    added_to_user_group_uid: Optional[UUID] = None


class UserGroup(AbstractModel):
    owner_uid: UUID
    user_group_uid: UUID


class UserExtendedProfile(UserProfile):
    dependents: Optional[list[UserProfile]] = []
    password: ClassVar[str]
    user_group: Optional[UserGroup] = None


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


class UserGroupInvitationUpdate(AbstractModel):

    email: Optional[EmailStr] = None
    is_accepted: Optional[bool] = None


class UserGroupIVProfile(UserGroupInvitation):
    uid: UUID
    date_created_utc: datetime
    is_accepted: bool


class PaginatedUserGroupIVProfile(AbstractModel):
    result_set: list[UserGroupIVProfile] = []
    result_size: conint(ge=0) = 0


class TokenData(AbstractModel):
    user_uid: UUID


class AccessRefreshPayload(AbstractModel):
    access_token: str
    refresh_token: str
