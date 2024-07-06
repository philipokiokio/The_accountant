import accountant.schemas.tracker_schemas as schemas

import accountant.database.handlers.tracker_handler as tracker_handler
from fastapi import HTTPException, status
from accountant.services.service_utils.accountant_exceptions import NotFoundError
from datetime import date
from uuid import UUID


async def create_tracker_records(user_uid: UUID, tracker_set: list[schemas.Tracker]):

    trackers = [
        schemas.TrackerExtended(
            **tracker.model_dump(),
            year=date.today().year,
            month=schemas.month_fetch(key=date.today().month),
            user_uid=user_uid
        )
        for tracker in tracker_set
    ]

    return await tracker_handler.create_record(track_set=trackers)


async def get_trackers(user_uid: UUID, **kwargs):

    return await tracker_handler.get_trackings(user_uid=user_uid, **kwargs)


async def get_tracker(user_uid: UUID, tracker_uid: UUID):

    try:
        return await tracker_handler.get_tracking(
            user_uid=user_uid, tracker_uid=tracker_uid
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tracker not found"
        )


async def update_tracker(
    user_uid: UUID, tracker_uid: UUID, tracker_update: schemas.TrackerUpdate
):

    await get_tracker(user_uid=user_uid, tracker_uid=tracker_uid)

    return await tracker_handler.update_tracking(
        tracker_uid=tracker_uid, tracking_update=tracker_update
    )


async def delete_tracker(user_uid: UUID, tracker_uid: UUID):
    await get_tracker(user_uid=user_uid, tracker_uid=tracker_uid)

    await tracker_handler.delete_tracking(tracker_uid=tracker_uid)
    return {}


async def tracker_dashboard(user_uid: UUID):

    return await tracker_handler.tracking_dashboard(user_uid=user_uid)
