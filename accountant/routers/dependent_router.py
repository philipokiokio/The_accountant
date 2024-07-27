from uuid import UUID

from fastapi import APIRouter, Body, Depends, status

import accountant.schemas.user_schemas as schemas
import accountant.services.auth_service as dependent_service
from accountant.services.service_utils.auth_utils import (
    get_current_user,
    get_user_group_uid,
)

api_router = APIRouter(prefix="/v1/dependent", tags=["Dependent Management"])


@api_router.post(
    path="",
    response_model=schemas.PaginatedUserGroupIVProfile,
    status_code=status.HTTP_201_CREATED,
)
async def add_dependent(
    emails: list[str] = Body(embed=True),
    current_user_profile: schemas.UserProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):

    return await dependent_service.add_dependent(
        emails=emails, user_group_uid=user_group_uid
    )


@api_router.get(
    path="s",
    response_model=schemas.PaginatedUserGroupIVProfile,
    status_code=status.HTTP_200_OK,
)
async def get_dependents(
    current_user_profile: schemas.UserProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await dependent_service.get_dependents(user_group_uid=user_group_uid)


@api_router.get(
    path="/{dependent_uid}",
    response_model=schemas.UserGroupIVProfile,
    status_code=status.HTTP_200_OK,
)
async def get_dependent(
    dependent_uid: UUID,
    current_user_profile: schemas.UserProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await dependent_service.get_dependent(
        user_group_uid=user_group_uid, uid=dependent_uid
    )


@api_router.patch(
    path="/{dependent_uid}",
    response_model=schemas.UserGroupIVProfile,
    status_code=status.HTTP_200_OK,
)
async def update_dependent(
    dependent_uid: UUID,
    dependent_update: schemas.UserGroupInvitationUpdate,
    current_user_profile: schemas.UserProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await dependent_service.update_dependent(
        user_group_uid=user_group_uid,
        uid=dependent_uid,
        dependent_invitation=dependent_update,
    )


@api_router.delete(
    path="/{dependent_uid}",
    status_code=status.HTTP_200_OK,
)
async def delete_dependent(
    dependent_uid: UUID,
    current_user_profile: schemas.UserProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):
    return await dependent_service.delete_dependent(
        user_group_uid=user_group_uid,
        uid=dependent_uid,
    )
