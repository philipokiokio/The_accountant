import logging
from uuid import UUID

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.orm import joinedload

import accountant.schemas.user_schemas as schemas
from accountant.database.orms.user_orm import User as UserDB
from accountant.database.orms.user_orm import UserGroup as UserGroupDB
from accountant.database.orms.user_orm import UserGroupInvitation as UserGroupIVDB
from accountant.database.orms.user_orm import UserUGroup as UserUGroupDB
from accountant.root.database import async_session
from accountant.services.service_utils.accountant_exceptions import (
    CreateError,
    DeleteError,
    NotFoundError,
    UpdateError,
)

LOGGER = logging.getLogger(__name__)


async def create_user(user: schemas.User):
    async with async_session() as session:

        stmt = insert(UserDB).values(**user.model_dump()).returning(UserDB)
        try:
            result = (await session.execute(statement=stmt)).scalar_one_or_none()

            if result is None:
                await session.rollback()
                raise CreateError

        except Exception:
            await session.rollback()
            raise CreateError
        await session.commit()

    return schemas.UserExtendedProfile(**result.as_dict())


async def check_user(**kwargs):
    email = kwargs.get("email")
    user_uid = kwargs.get("user_uid")

    filter_array = []
    if email:
        email = email.lower()
        filter_array.append(UserDB.email == email)
    if user_uid:
        filter_array.append(UserDB.user_uid == user_uid)
    async with async_session() as session:
        stmt = select(UserDB).filter(*filter_array)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.UserProfile(**result.as_dict())


async def get_user(user_uid: UUID):

    async with async_session() as session:
        stmt = (
            select(UserDB)
            .options(joinedload(UserDB.user_group))
            .filter(UserDB.user_uid == user_uid)
        )

        result = (await session.execute(statement=stmt)).unique().scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.UserExtendedProfile(
            **result.as_dict(),
            user_group=result.user_group[0] if result.user_group else None
        )


async def update_user(user_uid: UUID, user_update: schemas.UserUpdate):

    async with async_session() as session:

        stmt = (
            update(UserDB)
            .filter(UserDB.user_uid == user_uid)
            .values(**user_update.model_dump(exclude_none=True))
            .returning(UserDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.UserExtendedProfile(**result.as_dict())


async def all_user_update(user_uids, user_updates: list[schemas.UserUpdate]):

    async with async_session() as session:

        stmt = (
            update(UserDB)
            .filter(UserDB.user_uid.in_(user_uids))
            .values(
                *[
                    user_update.model_dump(exclude_none=True)
                    for user_update in user_updates
                ]
            )
            .returning(UserDB)
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if result is None:
            await session.rollback()
            raise UpdateError

        await session.commit()

        return [schemas.UserExtendedProfile(**x.as_dict()) for x in result]


async def delete_user(user_uid: UUID):
    async with async_session() as session:
        stmt = delete(UserDB).filter(UserDB.user_uid == user_uid).returning(UserDB)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()

        return schemas.UserExtendedProfile(**result.as_dict())


async def get_all_user(is_alive: bool = None):
    async with async_session() as session:
        stmt = (
            select(UserDB)
            .options(joinedload(UserDB.user_group))
            .filter(UserDB.is_alive == is_alive)
        )

        result = (await session.execute(statement=stmt)).unique().scalars().all()

        if result is None:
            return []

        return [schemas.UserExtendedProfile(**x.as_dict()) for x in result]


# UserGroup


async def create_user_group(user_uid: UUID):
    async with async_session() as session:
        stmt = (
            insert(UserGroupDB).values(**{"owner_uid": user_uid}).returning(UserGroupDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise CreateError

        await session.commit()

        return schemas.UserGroup(**result.as_dict())


async def get_user_group(user_uid: UUID):
    async with async_session() as session:
        stmt = select(UserGroupDB).filter(UserGroupDB.owner_uid == user_uid)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.UserGroup(**result.as_dict())


async def add_user_to_group(user_group_memb: schemas.UserGroupMember):
    async with async_session() as session:
        stmt = (
            insert(UserUGroupDB)
            .values(**user_group_memb.model_dump())
            .returning(UserUGroupDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise CreateError

        await session.commit()
        return schemas.UserGroupMemberProfile(**result.as_dict())


async def delete_from_user_group(user_uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(UserUGroupDB)
            .filter(UserUGroupDB.user_uid == user_uid)
            .returning(UserUGroupDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()
        return schemas.UserGroupMemberProfile(**result.as_dict())


async def get_users_in_user_group(user_group_uid: UUID):
    async with async_session() as session:
        stmt = select(UserUGroupDB).filter(
            UserUGroupDB.user_group_uid == user_group_uid
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:

            return schemas.PaginatedUserGroupProfile()

        return schemas.PaginatedUserGroupProfile(
            result_set=[schemas.UserGroupMemberProfile(**x.as_dict()) for x in result],
            result_size=len(result),
        )


async def get_user_in_user_group(user_group_uid: UUID, user_uid: UUID):
    async with async_session() as session:
        stmt = select(UserUGroupDB).filter(
            and_(
                UserUGroupDB.user_group_uid == user_group_uid,
                UserUGroupDB.user_uid == user_uid,
            )
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.UserGroupMemberProfile(**result.as_dict())


# User Invitation
async def check_dependent(email: str, user_group_uid: UUID):

    async with async_session() as session:
        stmt = select(UserGroupIVDB).filter(
            and_(
                UserGroupIVDB.user_group_uid == user_group_uid,
                UserGroupIVDB.email == email,
            )
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.UserGroupIVProfile(**result.as_dict())


async def create_dependent(user_g_iv: list[schemas.UserGroupInvitation]):
    async with async_session() as session:

        stmt = (
            insert(UserGroupIVDB)
            .values([u_g_iv.model_dump() for u_g_iv in user_g_iv])
            .returning(UserGroupIVDB)
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:
            await session.rollback()
            return schemas.PaginatedUserGroupIVProfile()

        await session.commit()

        return schemas.PaginatedUserGroupIVProfile(
            result_size=len(result),
            result_set=[schemas.UserGroupIVProfile(**x.as_dict()) for x in result],
        )


async def get_all_dependents(user_group_uid: UUID):
    async with async_session() as session:
        stmt = select(UserGroupIVDB).filter(
            UserGroupIVDB.user_group_uid == user_group_uid
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:
            return schemas.PaginatedUserGroupIVProfile()

        return schemas.PaginatedUserGroupIVProfile(
            result_size=len(result),
            result_set=[schemas.UserGroupIVProfile(**x.as_dict()) for x in result],
        )


async def get_dependent(user_group_uid: UUID, uid: UUID):
    async with async_session() as session:
        stmt = select(UserGroupIVDB).filter(
            UserGroupIVDB.user_group_uid == user_group_uid, UserGroupIVDB.uid == uid
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.UserGroupIVProfile(**result.as_dict())


async def update_dependent(
    user_group_uid: UUID,
    uid: UUID,
    dependent_invitation_update: schemas.UserGroupInvitationUpdate,
):
    async with async_session() as session:
        stmt = (
            update(UserGroupIVDB)
            .filter(
                UserGroupIVDB.user_group_uid == user_group_uid, UserGroupIVDB.uid == uid
            )
            .values(**dependent_invitation_update.model_dump(exclude_none=True))
            .returning(UserGroupIVDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise UpdateError

        await session.commit()
        return schemas.UserGroupIVProfile(**result.as_dict())


async def delete_dependent(user_group_uid: UUID, uid: UUID):
    async with async_session() as session:
        stmt = (
            delete(UserGroupIVDB)
            .filter(
                UserGroupIVDB.user_group_uid == user_group_uid, UserGroupIVDB.uid == uid
            )
            .returning(UserGroupIVDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()
        return schemas.UserGroupIVProfile(**result.as_dict())
