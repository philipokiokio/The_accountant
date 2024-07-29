from fastapi import APIRouter, status, Depends, Body
from accountant.schemas.user_schemas import UserExtendedProfile
import accountant.services.will_service as will_service
import accountant.schemas.will_schemas as schemas
from accountant.services.service_utils.auth_utils import (
    get_current_user,
    get_user_group_uid,
)
from uuid import UUID


api_router = APIRouter(prefix="/v1/will", tags=["Will Management Service"])


@api_router.post(
    path="/{investment_uid}",
    response_model=schemas.WillProfile,
    status_code=status.HTTP_200_OK,
)
async def create_will_allotment(
    investment_uid: UUID,
    invitation_uid: UUID = Body(embed=True),
    user_group_uid: UUID = Depends(get_user_group_uid),
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.create_will_allotment(
        investment_uid=investment_uid,
        owner_uid=user_profile.user_uid,
        user_group_uid=user_group_uid,
        invitation_uid=invitation_uid,
    )


@api_router.get(
    path="s",
    response_model=schemas.PaginatedWillProfile,
    status_code=status.HTTP_200_OK,
)
async def get_user_wills(
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.get_user_wills(user_uid=user_profile.user_uid)


@api_router.get(
    path="s-assigned",
    response_model=schemas.PaginatedWillProfile,
    status_code=status.HTTP_200_OK,
)
async def get_assigned_wills(
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.get_user_allotments(user_uid=user_profile.user_uid)


@api_router.get(
    path="/{will_uid}",
    response_model=schemas.WillExtendedProfile,
    status_code=status.HTTP_200_OK,
)
async def get_will(
    will_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.get_will(will_uid=will_uid)


@api_router.patch(
    path="/{will_uid}",
    response_model=schemas.WillProfile,
    status_code=status.HTTP_200_OK,
)
async def update_will_allotment(
    will_uid: UUID,
    invitation_uid: UUID = Body(embed=True),
    user_group_uid: UUID = Depends(get_user_group_uid),
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.update_will_allotment(
        will_uid=will_uid,
        user_uid=user_profile.user_uid,
        invitation_uid=invitation_uid,
        user_group_uid=user_group_uid,
    )


@api_router.patch(
    path="-assigned/{will_uid}",
    response_model=schemas.WillProfile,
    status_code=status.HTTP_200_OK,
)
async def update_assigned_will(
    will_uid: UUID,
    is_claimed: bool = Body(embed=True),
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.update_assigned_will(
        will_uid=will_uid,
        user_uid=user_profile.user_uid,
        is_claimed=is_claimed,
    )


@api_router.delete(
    path="/{will_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_will(
    will_uid: UUID,
    user_profile: UserExtendedProfile = Depends(get_current_user),
):
    return await will_service.delete_will(
        will_uid=will_uid,
        owner_uid=user_profile.user_uid,
    )
