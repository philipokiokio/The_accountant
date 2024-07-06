import accountant.schemas.earning_schemas as schemas
import accountant.database.handlers.earning_handler as earning_handler
from fastapi import HTTPException, status
from accountant.services.service_utils.accountant_exceptions import NotFoundError
from datetime import date
from uuid import UUID


async def create_earning_records(user_uid: UUID, earning_set: list[schemas.Earning]):
    date_ = date.today()
    earnings = [
        schemas.EarningExtended(
            **earning.model_dump(), year=date_.year, user_uid=user_uid
        )
        for earning in earning_set
    ]

    return await earning_handler.create_earning(earnings=earnings)


async def get_earnings(user_uid: UUID, **kwargs):

    return await earning_handler.get_earnings(user_uid=user_uid, **kwargs)


async def get_earning(user_uid: UUID, earning_uid: UUID):

    try:
        return await earning_handler.get_earning(
            user_uid=user_uid, earning_uid=earning_uid
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="earning not found"
        )


async def update_earning(
    user_uid: UUID, earning_uid: UUID, earning_update: schemas.EarningUpdate
):

    await get_earning(user_uid=user_uid, earning_uid=earning_uid)

    return await earning_handler.update_earning(
        earning_uid=earning_uid, earn_update=earning_update
    )


async def delete_earning(user_uid: UUID, earning_uid: UUID):
    await get_earning(user_uid=user_uid, earning_uid=earning_uid)
    await earning_handler.delete_earning(earning_uid=earning_uid)

    return {}


async def earning_dashboard(user_uid: UUID, **kwargs):

    return await earning_handler.earning_dashboard(user_uid=user_uid, **kwargs)
