from uuid import UUID
from fastapi import APIRouter, Body, status, Depends
from accountant.schemas.user_schemas import UserExtendedProfile
import accountant.services.investment_service as investment_service
import accountant.schemas.investment_schemas as schemas
from accountant.services.service_utils.auth_utils import (
    get_current_user,
    get_user_group_uid,
)


api_router = APIRouter(prefix="/v1/investment", tags=["Investment"])


@api_router.post(
    path="/platform",
    response_model=schemas.PlatformProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_platform(
    platform: schemas.Platform,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.create_platform(
        platform=platform, user_group_uid=user_group_uid
    )


@api_router.get(
    path="/platform",
    response_model=schemas.PaginatedPlatformProfile,
    status_code=status.HTTP_200_OK,
)
async def get_platforms(
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.get_platforms(user_group_uid=user_group_uid)


@api_router.get(
    path="/platform/{platform_uid}",
    response_model=schemas.PlatformProfile,
    status_code=status.HTTP_200_OK,
)
async def get_platform(
    platform_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.get_platform(
        user_group_uid=user_group_uid, platform_uid=platform_uid
    )


@api_router.patch(
    path="/platform/{platform_uid}",
    response_model=schemas.PlatformProfile,
    status_code=status.HTTP_200_OK,
)
async def update_platform(
    platform_uid: UUID,
    platform_update: schemas.PlatformUpdate,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.update_platform(
        user_group_uid=user_group_uid,
        platform_uid=platform_uid,
        platform_update=platform_update,
    )


@api_router.patch(
    path="/platform/{platform_uid}/decode",
    response_model=schemas.PlatformProfile,
    status_code=status.HTTP_200_OK,
)
async def decode_platform(
    platform_uid: UUID,
    user_password: str = Body(embed=True),
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):

    return await investment_service.decode_platform(
        user_group_uid=user_group_uid,
        user_password=user_password,
        platform_uid=platform_uid,
        user_uid=user_profile.user_uid,
    )


@api_router.delete(
    path="/platform/{platform_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_platform(
    platform_uid: UUID,
    user_group_uid: UUID = Depends(get_user_group_uid),
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await investment_service.delete_platform(
        user_group_uid=user_group_uid,
        platform_uid=platform_uid,
    )


####################### Investment #############################################


@api_router.post(
    path="s/{platform_uid}",
    response_model=schemas.InvestmentProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_investment(
    platform_uid: UUID,
    investment: schemas.Investment,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.create_investment(
        platform_uid=platform_uid,
        investment=investment,
        user_group_uid=user_group_uid,
    )


@api_router.get(
    path="s/{platform_uid}",
    response_model=schemas.PaginatedInvestmentProfile,
    status_code=status.HTTP_200_OK,
)
async def get_investments(
    platform_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.get_investments(
        platform_uid=platform_uid,
        user_group_uid=user_group_uid,
    )


@api_router.get(
    path="s/{platform_uid}/inv/{investment_uid}",
    response_model=schemas.InvestmentProfile,
    status_code=status.HTTP_200_OK,
)
async def get_investment(
    investment_uid: UUID,
    platform_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.get_investment(
        platform_uid=platform_uid,
        investment_uid=investment_uid,
        user_group_uid=user_group_uid,
    )


@api_router.patch(
    path="s/{platform_uid}/inv/{investment_uid}",
    response_model=schemas.InvestmentProfile,
    status_code=status.HTTP_200_OK,
)
async def update_investment(
    investment_uid: UUID,
    platform_uid: UUID,
    investment_update: schemas.InvestmentUpdate,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.update_investment(
        platform_uid=platform_uid,
        investment_uid=investment_uid,
        investment_update=investment_update,
        user_group_uid=user_group_uid,
    )


@api_router.delete(
    path="s/{platform_uid}/inv/{investment_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_investment(
    investment_uid: UUID,
    platform_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.delete_investment(
        platform_uid=platform_uid,
        investment_uid=investment_uid,
        user_group_uid=user_group_uid,
    )


########################## Investment Tracker ###########################################################


@api_router.post(
    path="-trackers/{platform_uid}/inv/{investment_uid}",
    response_model=schemas.InvestmentTrackerProfile,
    status_code=status.HTTP_201_CREATED,
)
async def create_investment_tracker(
    platform_uid: UUID,
    investment_uid: schemas.UUID,
    investment_tracker: schemas.InvestmentTracker,
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await investment_service.create_investment_tracker(
        platform_uid=platform_uid,
        investment_uid=investment_uid,
        investment_tracker=investment_tracker,
        user_group_uid=user_group_uid,
    )


@api_router.get(
    path="-trackers/{platform_uid}/inv/{investment_uid}",
    response_model=schemas.PaginatedInvestmentTrackerProfile,
    status_code=status.HTTP_200_OK,
)
async def get_investment_trackers(
    platform_uid: UUID,
    investment_uid: UUID,
    user_group_uid: UUID = Depends(get_user_group_uid),
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await investment_service.get_investment_trackers(
        platform_uid=platform_uid,
        investment_uid=investment_uid,
        user_group_uid=user_group_uid,
    )


@api_router.get(
    path="-tracker/{investment_uid}/track/{tracker_uid}",
    response_model=schemas.InvestmentTrackerProfile,
    status_code=status.HTTP_200_OK,
)
async def get_investment_tracker(
    investment_uid: UUID,
    tracker_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await investment_service.get_investment_tracker(
        investment_uid=investment_uid,
        tracker_uid=tracker_uid,
    )


@api_router.patch(
    path="-tracker/{investment_uid}/track/{tracker_uid}",
    response_model=schemas.InvestmentTrackerProfile,
    status_code=status.HTTP_200_OK,
)
async def update_investment_tracker(
    investment_uid: UUID,
    tracker_uid: UUID,
    tracker_update: schemas.InvestmentTrackerUpdate,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await investment_service.update_investment_tracker(
        investment_uid=investment_uid,
        tracker_uid=tracker_uid,
        investment_tracker_update=tracker_update,
    )


@api_router.delete(
    path="-tracker/{investment_uid}/track/{tracker_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_investment_tracker(
    investment_uid: UUID,
    tracker_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await investment_service.delete_invest_tracker(
        investment_uid=investment_uid,
        tracker_uid=tracker_uid,
    )
