from accountant.root.database import async_session
from accountant.database.orms.earnings_orm import Earning as EarningDB
import logging
from sqlalchemy import select, insert, update, delete, and_, func
import accountant.schemas.earning_schemas as schemas
from accountant.services.service_utils.accountant_exceptions import (
    CreateError,
    DeleteError,
    NotFoundError,
    UpdateError,
)
from uuid import UUID


LOGGER = logging.getLogger(__name__)


async def create_earning(earnings: list[schemas.EarningExtended]):

    async with async_session() as session:

        stmt = (
            insert(EarningDB)
            .values(*[earning.model_dump() for earning in earnings])
            .returning(EarningDB)
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:
            await session.rollback()
            return schemas.PaginatedEarningProfile()

        await session.commit()

        return schemas.PaginatedEarningProfile(
            result_set=[schemas.EarningProfile(**x.as_dict()) for x in result],
            result_size=len(result),
        )


async def get_earnings(user_uid: UUID, **kwargs):

    async with async_session() as session:
        stmt = select(EarningDB).filter(EarningDB.user_uid == user_uid)

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:

            return schemas.PaginatedEarningProfile()

        result_size = (
            await session.execute(
                statement=select(func.count(EarningDB.user_uid)).filter(
                    EarningDB.user_uid == user_uid
                )
            )
        ).scalar()

        return schemas.PaginatedEarningProfile(
            result_set=[schemas.EarningProfile(**x.as_dict()) for x in result],
            result_size=result_size,
        )


async def get_earning(user_uid: UUID, earning_uid: UUID):
    async with async_session() as session:

        stmt = select(EarningDB).filter(
            EarningDB.user_uid == user_uid, EarningDB.earning_uid == earning_uid
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.EarningProfile(**result.as_dict())


async def update_earning(earning_uid: UUID, earn_update: schemas.EarningUpdate):
    async with async_session() as session:
        stmt = (
            update(EarningDB)
            .filter(EarningDB.earning_uid == earning_uid)
            .values(**earn_update.model_dump(exclude_none=True))
            .returning(EarningDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise UpdateError

        await session.commit()

        return schemas.EarningProfile(**result.as_dict())


async def delete_earning(earning_uid: UUID):

    async with async_session() as session:
        stmt = (
            delete(EarningDB)
            .filter(EarningDB.earning_uid == earning_uid)
            .returning(EarningDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            await session.rollback()
            raise DeleteError

        await session.commit()

        return schemas.EarningProfile(**result.as_dict())


async def earning_dashboard(user_uid: UUID, **kwargs):
    async with async_session() as session:

        summary_stmt = (
            select(EarningDB)
            .filter(
                EarningDB.user_uid == user_uid,
            )
            .order_by(EarningDB.year.asc())
        )

        summary_result = (await session.execute(statement=summary_stmt)).scalars().all()

    summary = {}
    year_trend = {}

    for row in summary_result:
        amount, month, year, currency = row.amount, row.month, row.year, row.currency
        if currency not in summary:
            summary[currency] = {year: amount}

        elif currency in summary:
            if summary[currency].get(year) is None:
                summary[currency] = {year: amount}
            else:
                summary[currency][year] += amount

        if year not in year_trend:
            year_trend = {
                year: {currency: {month: {"amount": amount, "percentage_change": 0}}}
            }

        elif year in year_trend:
            if year_trend[year].get(currency) is None:

                year_trend[year][currency] = {
                    month: {
                        "amount": amount,
                    }
                }

            elif year_trend[year].get(currency):
                if year_trend[year][currency].get(month):

                    year_trend[year][currency][month]["amount"] += amount

                else:

                    year_trend[year][currency][month] = {
                        "amount": amount,
                    }

    return schemas.EarningDashBoard(summary=summary, yearly_chart=year_trend)
