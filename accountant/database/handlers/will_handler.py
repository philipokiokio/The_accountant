from uuid import UUID

from sqlalchemy import delete, select, insert, update, func
from sqlalchemy.orm import joinedload
import accountant.schemas.will_schemas as schemas
from accountant.root.database import async_session
from accountant.database.orms.will_orm import Will as WillDB
from accountant.services.service_utils.accountant_exceptions import (
    CreateError,
    DeleteError,
    NotFoundError,
    UpdateError,
)


async def create_will_allotment(will: schemas.Will):

    async with async_session() as session:

        stmt = insert(WillDB).values(**will.model_dump()).returning(WillDB)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise CreateError

        await session.commit()

        return schemas.WillProfile(**result.as_dict())
        ...


async def check_investment_will_allotment(investment_uid: UUID):

    async with async_session() as session:
        stmt = select(WillDB).filter(WillDB.investment_uid == investment_uid)

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.WillProfile(**result.as_dict())


async def get_wills(**kwargs):

    owner_uid = kwargs.get("owner_uid")
    assigned_uid = kwargs.get("assigned_uid")

    filter_case = []

    if owner_uid:
        filter_case.append(WillDB.owner_uid == owner_uid)

    if assigned_uid:
        filter_case.append(WillDB.assigned_uid == assigned_uid)

    async with async_session() as session:

        stmt = (
            select(WillDB).options(joinedload(WillDB.investment)).filter(*filter_case)
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:

            return schemas.PaginatedWillProfile()

        result_size = (
            await session.execute(
                statement=select(func.count(WillDB.will_uid)).filter(*filter_case)
            )
        ).scalar()

        return schemas.PaginatedWillProfile(
            result_set=[
                schemas.WillExtendedProfile(**x.as_dict(), investment=x.investment)
                for x in result
            ],
            result_size=result_size,
        )


async def get_will(will_uid: UUID):
    async with async_session() as session:
        stmt = (
            select(WillDB)
            .options(joinedload(WillDB.investment))
            .filter(WillDB.will_uid == will_uid)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.WillExtendedProfile(
            **result.as_dict(), investment=result.investment
        )


async def update_will(will_uid: UUID, will_update: schemas.WillUpdate):

    async with async_session() as session:
        stmt = (
            update(WillDB)
            .filter(will_uid == WillDB.will_uid)
            .values(**will_update.model_dump())
            .returning(WillDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise UpdateError

        await session.commit()
        return schemas.WillProfile(**result.as_dict())


async def delete_will(will_uid: UUID, owner_uid: UUID):

    async with async_session() as session:
        stmt = (
            delete(WillDB)
            .filter(WillDB.will_uid == will_uid, WillDB.owner_uid == owner_uid)
            .returning(WillDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()

        return schemas.WillProfile(**result.as_dict())
