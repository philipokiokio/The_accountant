from uuid import UUID
from fastapi import APIRouter, status, Depends
from accountant.schemas.user_schemas import UserExtendedProfile
import accountant.services.earning_service as earning_service
import accountant.schemas.earning_schemas as schemas
from accountant.services.service_utils.auth_utils import get_current_user


api_router = APIRouter(prefix="/v1/earning", tags=["Earnings"])


@api_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PaginatedEarningProfile,
)
async def create_earning(
    earning_set: list[schemas.Earning],
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await earning_service.create_earning_records(
        user_uid=user_profile.user_uid, earning_set=earning_set
    )


@api_router.get(
    path="s",
    status_code=status.HTTP_200_OK,
    response_model=schemas.PaginatedEarningProfile,
)
async def get_earnings(
    user_profile: UserExtendedProfile = Depends(get_current_user),
):

    return await earning_service.get_earnings(user_uid=user_profile.user_uid)


@api_router.get(
    path="/{earning_uid}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EarningProfile,
)
async def get_earning(
    earning_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):

    return await earning_service.get_earning(
        user_uid=user_profile.user_uid, earning_uid=earning_uid
    )


@api_router.patch(
    path="/{earning_uid}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EarningProfile,
)
async def update_earning(
    earning_uid: UUID,
    earning_update: schemas.EarningUpdate,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):

    return await earning_service.update_earning(
        user_uid=user_profile.user_uid,
        earning_uid=earning_uid,
        earning_update=earning_update,
    )


@api_router.delete(
    path="/{earning_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_earning(
    earning_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):

    return await earning_service.delete_earning(
        user_uid=user_profile.user_uid,
        earning_uid=earning_uid,
    )


@api_router.get(
    path="s/dashboard",
    status_code=status.HTTP_200_OK,
    # response_model=schemas.EarningDashBoard
)
async def earning_dashboards(
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await earning_service.earning_dashboard(user_uid=user_profile.user_uid)
