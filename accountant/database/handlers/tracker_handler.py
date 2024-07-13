from uuid import UUID

from sqlalchemy import delete, func, insert, select, update

import accountant.schemas.tracker_schemas as schemas
from accountant.database.orms.tracker_orm import Tracker as TrackerDB
from accountant.root.database import async_session
from accountant.services.service_utils.accountant_exceptions import (
    DeleteError,
    NotFoundError,
    UpdateError,
)


async def create_record(track_set: list[schemas.TrackerExtended]):

    async with async_session() as session:

        stmt = (
            insert(TrackerDB)
            .values(*[tracker.model_dump() for tracker in track_set])
            .returning(TrackerDB)
        )

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:
            await session.rollback()

            return schemas.PaginatedTrackerProfile()

        await session.commit()

        return schemas.PaginatedTrackerProfile(
            result_set=[schemas.TrackerProfile(**x.as_dict()) for x in result],
            result_size=len(result),
        )


async def get_trackings(user_uid: UUID, **kwargs):

    async with async_session() as session:
        stmt = select(TrackerDB).filter(TrackerDB.user_uid == user_uid)

        result = (await session.execute(statement=stmt)).scalars().all()

        if not result:
            return schemas.PaginatedTrackerProfile()

        result_size = (
            await session.execute(
                statement=select(func.count(TrackerDB.user_uid)).filter(
                    TrackerDB.user_uid == user_uid
                )
            )
        ).scalar()

        return schemas.PaginatedTrackerProfile(
            result_set=[schemas.TrackerProfile(**x.as_dict()) for x in result],
            result_size=result_size,
        )


async def get_tracking(user_uid: UUID, tracker_uid: UUID):

    async with async_session() as session:
        stmt = select(TrackerDB).filter(
            TrackerDB.user_uid == user_uid, TrackerDB.tracker_uid == tracker_uid
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:

            raise NotFoundError

        return schemas.TrackerProfile(**result.as_dict())


async def update_tracking(tracker_uid: UUID, tracking_update: schemas.TrackerUpdate):

    async with async_session() as session:
        stmt = (
            update(TrackerDB)
            .filter(TrackerDB.tracker_uid == tracker_uid)
            .values(tracking_update.model_dump(exclude_none=True))
            .returning(TrackerDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise UpdateError

        await session.commit()
        return schemas.TrackerProfile(**result.as_dict())


async def delete_tracking(tracker_uid: UUID):

    async with async_session() as session:
        stmt = (
            delete(TrackerDB)
            .filter(TrackerDB.tracker_uid == tracker_uid)
            .returning(TrackerDB)
        )

        result = (await session.execute(statement=stmt)).scalar_one_or_none()

        if result is None:
            await session.rollback()
            raise DeleteError

        await session.commit()
        return schemas.TrackerProfile(**result.as_dict())


async def tracking_dashboard(user_uid: UUID):

    async with async_session() as session:
        summary_stmt = select(TrackerDB).filter(TrackerDB.user_uid == user_uid)

        summary_result = (await session.execute(statement=summary_stmt)).scalars().all()

        summary = {}
        year_trend = {}
        for result in summary_result:

            amount, month, year, currency = (
                result.amount,
                result.month,
                result.year,
                result.currency,
            )

            if currency not in summary:
                summary[currency] = {year: amount}
            elif currency in summary:
                if summary[currency].get(year) is None:
                    summary[currency][year] = amount
                else:
                    summary[currency][year] += amount

            if year not in year_trend:
                year_trend = {year: {currency: {month: {"amount": amount}}}}

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

        return schemas.TrackingDashBoard(summary=summary, yearly_chart=year_trend)

        return schemas.TrackingDashBoard(summary=summary, yearly_chart=year_trend)
