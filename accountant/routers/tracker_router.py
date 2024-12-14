from uuid import UUID

from fastapi import APIRouter, Depends, status

import accountant.schemas.tracker_schemas as schemas
import accountant.services.tracker_service as tracker_service
from accountant.schemas.user_schemas import UserExtendedProfile
from accountant.services.service_utils.auth_utils import get_current_user

api_router = APIRouter(prefix="/v1/tracker", tags=["Tracker"])


@api_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PaginatedTrackerProfile,
)
async def create_tracker(
    tracker_set: list[schemas.Tracker],
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await tracker_service.create_tracker_records(
        user_uid=user_profile.user_uid, tracker_set=tracker_set
    )


@api_router.get(
    path="s",
    status_code=status.HTTP_200_OK,
    response_model=schemas.PaginatedTrackerProfile,
)
async def get_trackers(
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await tracker_service.get_trackers(
        user_uid=user_profile.user_uid,
    )


@api_router.get(
    path="/{tracker_uid}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TrackerProfile,
)
async def get_tracker(
    tracker_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await tracker_service.get_tracker(
        user_uid=user_profile.user_uid, tracker_uid=tracker_uid
    )


@api_router.patch(
    path="/{tracker_uid}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TrackerProfile,
)
async def update_tracker(
    tracker_uid: UUID,
    tracker_update: schemas.TrackerUpdate,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await tracker_service.update_tracker(
        user_uid=user_profile.user_uid,
        tracker_uid=tracker_uid,
        tracker_update=tracker_update,
    )


@api_router.delete(
    path="/{tracker_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_tracker(
    tracker_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await tracker_service.delete_tracker(
        user_uid=user_profile.user_uid, tracker_uid=tracker_uid
    )


@api_router.get(
    path="s/dashboard",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TrackingDashBoard,
)
async def get_tracker_dashboard(
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await tracker_service.tracker_dashboard(user_uid=user_profile.user_uid)
