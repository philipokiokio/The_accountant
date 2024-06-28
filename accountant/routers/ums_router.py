from fastapi import APIRouter, status, Depends, Body
import accountant.services.auth_service as ums_service
import accountant.schemas.user_schemas as schemas
from accountant.services.service_utils.auth_utils import get_current_user


api_router = APIRouter(prefix="/v1/ums", tags=["User Management Service"])


@api_router.patch(
    path="", response_model=schemas.UserExtendedProfile, status_code=status.HTTP_200_OK
)
async def update_user(
    user_update: schemas.UserUpdate,
    user_profile: schemas.UserExtendedProfile = Depends(get_current_user),
):

    return await ums_service.update_user(
        user_uid=user_profile.user_uid, user_update=user_update
    )


@api_router.patch(
    path="/change-password",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserExtendedProfile,
)
async def change_password(
    old_password: str = Body(embed=True),
    new_password: str = Body(embed=True),
    user_profile: schemas.UserExtendedProfile = Depends(get_current_user),
):
    return await ums_service.change_password(
        old_password=old_password,
        new_password=new_password,
        user_uid=user_profile.user_uid,
    )
