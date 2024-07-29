from uuid import UUID

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.orm import joinedload

import accountant.schemas.investment_schemas as schemas
from accountant.database.orms.investments_orm import Investment as InvestmentDB
from accountant.database.orms.investments_orm import (
    InvestmentTracker as InvestmentTrackerDB,
)
from accountant.database.orms.investments_orm import Platform as PlatformDB
from accountant.root.database import async_session
from accountant.services.service_utils.accountant_exceptions import (
    CreateError,
    DeleteError,
    NotFoundError,
    UpdateError,
)


async def check_platform(name: str, user_group_uid: UUID):

    async with async_session() as session:

        stmt = select(PlatformDB).filter(
            PlatformDB.user_group_uid == user_group_uid,
            PlatformDB.name == name,
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.PlatformProfile(**result.as_dict())


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


async def get_platforms(user_group_uid: UUID):

    async with async_session() as session:

        stmt = (
            select(PlatformDB)
            .options(
                joinedload(PlatformDB.investment).joinedload(InvestmentDB.trackers)
            )
            .filter(PlatformDB.user_group_uid == user_group_uid)
        )

        result = (await session.execute(statement=stmt)).unique().scalars().all()
        if result is None:

            return schemas.PaginatedPlatformProfile()

        result_size = (
            await session.execute(
                statement=select(func.count(PlatformDB.user_group_uid)).filter(
                    PlatformDB.user_group_uid == user_group_uid
                )
            )
        ).scalar()

        return schemas.PaginatedPlatformProfile(
            result_set=[
                schemas.PlatformProfile(
                    **x.as_dict(),
                    investment_plans=[
                        schemas.InvestmentProfile(**y.as_dict(), activities=y.trackers)
                        for y in x.investment
                    ],
                )
                for x in result
            ],
            result_size=result_size,
        )


async def get_platform(user_group_uid: UUID, platform_uid: UUID):

    async with async_session() as session:

        stmt = (
            select(PlatformDB)
            .options(
                joinedload(PlatformDB.investment).joinedload(InvestmentDB.trackers)
            )
            .filter(
                PlatformDB.user_group_uid == user_group_uid,
                PlatformDB.platform_uid == platform_uid,
            )
        )

        result = (await session.execute(statement=stmt)).unique().scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.PlatformProfile(
            **result.as_dict(),
            investment_plans=[
                schemas.InvestmentProfile(**y.as_dict(), activities=y.trackers)
                for y in result.investment
            ],
        )


async def update_platform(platform_uid: UUID, platform_update: schemas.PlatformUpdate):

    async with async_session() as session:

        stmt = (
            update(PlatformDB)
            .filter(
                PlatformDB.platform_uid == platform_uid,
            )
            .values(**platform_update.model_dump(exclude_none=True))
            .returning(PlatformDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise UpdateError

        await session.commit()
        return schemas.PlatformProfile(**result.as_dict())


async def delete_platform(platform_uid: UUID):
    async with async_session() as session:

        stmt = (
            delete(PlatformDB)
            .filter(
                PlatformDB.platform_uid == platform_uid,
            )
            .returning(PlatformDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()
        return schemas.PlatformProfile(**result.as_dict())


################################ Investment #################################


async def check_investment(platform_uid: UUID, user_group_uid: UUID, plan_name: str):

    async with async_session() as session:
        stmt = select(InvestmentDB).filter(
            InvestmentDB.user_group_uid == user_group_uid,
            InvestmentDB.platform_uid == platform_uid,
            InvestmentDB.plan_name == plan_name,
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.InvestmentProfile(**result.as_dict())


async def create_investment(
    platform_uid: UUID, user_group_uid: UUID, investment: schemas.Investment
):
    async with async_session() as session:

        stmt = (
            insert(InvestmentDB)
            .values(
                user_group_uid=user_group_uid,
                platform_uid=platform_uid,
                **investment.model_dump(),
            )
            .returning(InvestmentDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()

            raise CreateError

        await session.commit()
        return schemas.InvestmentProfile(**result.as_dict())


async def get_investments(platform_uid: UUID):

    async with async_session() as session:

        stmt = (
            select(InvestmentDB)
            .options(joinedload(InvestmentDB.trackers))
            .filter(InvestmentDB.platform_uid == platform_uid)
        )

        result = (await session.execute(statement=stmt)).unique().scalars().all()

        if not result:

            return schemas.PaginatedInvestmentProfile()

        result_size = (
            await session.execute(
                statement=select(func.count(InvestmentDB.platform_uid)).filter(
                    InvestmentDB.platform_uid == platform_uid
                )
            )
        ).scalar()

        return schemas.PaginatedInvestmentProfile(
            result_set=[
                schemas.InvestmentProfile(**x.as_dict(), activities=x.trackers)
                for x in result
            ],
            result_size=result_size,
        )


async def get_investment_via_investment_uid(investment_uid: UUID):
    async with async_session() as session:

        stmt = (
            select(InvestmentDB)
            .options(joinedload(InvestmentDB.platform))
            .filter(
                InvestmentDB.investment_uid == investment_uid,
            )
        )

        result = (await session.execute(statement=stmt)).unique().scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.InvestmentExtendedProfile(
            **result.as_dict(), platform=result.platform
        )


async def get_investment(platform_uid: UUID, investment_uid: UUID):
    async with async_session() as session:

        stmt = (
            select(InvestmentDB)
            .options(joinedload(InvestmentDB.trackers))
            .filter(
                InvestmentDB.platform_uid == platform_uid,
                InvestmentDB.investment_uid == investment_uid,
            )
        )

        result = (await session.execute(statement=stmt)).unique().scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.InvestmentProfile(**result.as_dict(), activities=result.trackers)

    ...


async def update_investment(
    investment_uid: UUID, investment_update: schemas.InvestmentUpdate
):

    async with async_session() as session:

        stmt = (
            update(InvestmentDB)
            .filter(InvestmentDB.investment_uid == investment_uid)
            .values(**investment_update.model_dump(exclude_none=True))
            .returning(InvestmentDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.InvestmentProfile(**result.as_dict())


async def delete_investment(investment_uid: UUID, user_group_uid: UUID):
    async with async_session() as session:

        stmt = (
            delete(InvestmentDB)
            .filter(
                InvestmentDB.investment_uid == investment_uid,
                InvestmentDB.user_group_uid == user_group_uid,
            )
            .returning(InvestmentDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise DeleteError

        await session.commit()

        return schemas.InvestmentProfile(**result.as_dict())


#######################  Investment Tracker ##################################


async def create_investment_tracker(
    investment_uid: UUID, investment_tracker: schemas.InvestmentTracker
):

    async with async_session() as session:
        stmt = (
            insert(InvestmentTrackerDB)
            .values(
                **investment_tracker.model_dump(),
                investment_uid=investment_uid,
            )
            .returning(InvestmentTrackerDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()

            raise CreateError

        await session.commit()
        return schemas.InvestmentTracker(**result.as_dict())


async def get_investment_trackers(investment_uid: UUID):

    async with async_session() as session:

        stmt = select(InvestmentTrackerDB).filter(
            InvestmentTrackerDB.investment_uid == investment_uid
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:

            return schemas.PaginatedInvestmentTrackerProfile()

        result_size = (
            await session.execute(
                statement=select(func.count(InvestmentTrackerDB.investment_uid)).filter(
                    InvestmentTrackerDB.investment_uid == investment_uid
                )
            )
        ).scalar()

        return schemas.PaginatedInvestmentTrackerProfile(
            result_set=[
                schemas.InvestmentTrackerProfile(**x.as_dict()) for x in result
            ],
            result_size=result_size,
        )


async def get_investment_tracker(investment_uid: UUID, uid: UUID):
    async with async_session() as session:
        stmt = select(InvestmentTrackerDB).filter(
            InvestmentTrackerDB.investment_uid == investment_uid,
            InvestmentTrackerDB.uid == uid,
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        return schemas.InvestmentTrackerProfile(**result.as_dict())


async def update_investment_tracker(
    uid: UUID, investment_tracker_update: schemas.InvestmentTrackerUpdate
):

    async with async_session() as session:
        stmt = (
            update(InvestmentTrackerDB)
            .filter(InvestmentTrackerDB.uid == uid)
            .values(**investment_tracker_update.model_dump(exclude_none=True))
            .returning(InvestmentTrackerDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.InvestmentTrackerProfile(**result.as_dict())


async def delete_investment_tracker(uid: UUID):

    async with async_session() as session:
        stmt = (
            delete(InvestmentTrackerDB)
            .filter(InvestmentTrackerDB.uid == uid)
            .returning(InvestmentTrackerDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()

        return schemas.InvestmentTrackerProfile(**result.as_dict())
        return schemas.InvestmentTrackerProfile(**result.as_dict())
