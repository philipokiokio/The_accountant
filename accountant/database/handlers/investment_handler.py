from accountant.root.database import async_session
from accountant.database.orms.investments_orm import Platform as PlatformDB
from accountant.database.orms.investments_orm import Investment as InvestmentDB
from accountant.database.orms.investments_orm import (
    InvestmentTracker as InvestmentTrackerDB,
)

from sqlalchemy import select, insert, update, delete, and_, func
import accountant.schemas.investment_schemas as schemas
from accountant.services.service_utils.accountant_exceptions import (
    CreateError,
    DeleteError,
    NotFoundError,
    UpdateError,
)
from uuid import UUID


async def create_platform_record(user_group_uid: UUID, platform: schemas.Platform):

    async with async_session() as session:

        stmt = (
            insert(PlatformDB)
            .values(**platform.model_dump(), user_group_uid=user_group_uid)
            .returning(PlatformDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise CreateError

        await session.commit()

        return schemas.PlatformProfile(**result.as_dict())

        ...


async def get_platforms(user_uid: UUID):

    async with async_session() as session:

        ...


async def get_platform(user_uid: UUID, platform_uid: UUID):

    async with async_session() as session:

        ...


async def update_platform(
    platform_uid: UUID,
):

    async with async_session() as session:

        ...


async def delete_platform(platform_uid: UUID):
    async with async_session() as session:

        ...
