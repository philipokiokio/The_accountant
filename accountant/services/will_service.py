from uuid import UUID

from fastapi import HTTPException, status


import accountant.database.handlers.will_handler as will_handler
import accountant.services.investment_service as investment_service
import accountant.services.auth_service as invitation_service
import accountant.schemas.will_schemas as schemas
from accountant.services.service_utils.accountant_exceptions import NotFoundError


async def check_investment_will_alotment(investment_uid: UUID):
    try:

        return await will_handler.check_investment_will_allotment(
            investment_uid=investment_uid
        )
    except NotFoundError as e:

        raise e


async def create_will_allotment(
    user_group_uid: UUID, owner_uid: UUID, investment_uid: UUID, invitation_uid: UUID
):

    try:
        investment_profile = await investment_service.get_investment_via_investment_uid(
            investment_uid=investment_uid
        )

        if investment_profile.platform.user_group_uid != user_group_uid:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user does not have will access to this investment",
            )
    except NotFoundError:
        raise HTTPException(
            detail="investment data not found", status_code=status.HTTP_404_NOT_FOUND
        )

    invitation_profile = await invitation_service.get_dependent(
        user_group_uid=user_group_uid, uid=invitation_uid
    )

    try:

        check_will = await check_investment_will_alotment(investment_uid=investment_uid)
        if check_will:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Investment have been willed out",
            )
    except NotFoundError:

        will = schemas.Will(
            investment_uid=investment_uid,
            invitation_uid=invitation_uid,
            owner_uid=owner_uid,
        )

        try:
            user_profile = await invitation_service.check_user(
                email=invitation_profile.email
            )

            will.assigned_uid = user_profile.user_uid
        except HTTPException:
            ...

        return will_handler.create_will_allotment(will=will)


async def get_user_wills(user_uid: UUID):

    return will_handler.get_wills(owner_uid=user_uid)


async def get_user_allotments(user_uid: UUID):

    return will_handler.get_wills(assigned_uid=user_uid)


async def get_will(will_uid: UUID):

    try:
        return await will_handler.get_will(will_uid=will_uid)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="will allotments not found"
        )


async def update_will(will_uid: UUID, will_update: schemas.WillUpdate):

    return await will_handler.update_will(will_uid=will_uid, will_update=will_update)
    ...


async def delete_will(will_uid: UUID, owner_uid: UUID):
    await will_handler.delete_will(will_uid=will_uid, owner_uid=owner_uid)

    return {}


async def update_assigned_will(will_uid: UUID, user_uid: UUID, is_claimed: bool = None):

    will_profile = await get_will(will_uid=will_uid)

    if will_profile.assigned_uid != user_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user does not have the right access for this action",
        )

    if will_profile.is_claimed is True:

        return will_profile

    return await will_handler.update_will(
        will_uid=will_uid,
        will_update=schemas.WillUpdate(is_claimed=is_claimed, assigned_uid=user_uid),
    )


async def update_will_allotment(
    will_uid: UUID, user_uid: UUID, user_group_uid: UUID, invitation_uid: UUID
):

    will_profile = await get_will(will_uid=will_uid)

    if will_profile.owner_uid != user_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user does not have the right access for this action",
        )

    if will_profile.invitation_uid == invitation_uid:
        return will_profile

    if will_profile.is_claimed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="will has been claimed by the assigned",
        )

    await invitation_service.get_dependent(
        uid=invitation_uid, user_group_uid=user_group_uid
    )

    return await update_will(
        will_uid=will_uid, will_update=schemas.WillUpdate(invitation_uid=invitation_uid)
    )
