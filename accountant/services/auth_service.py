import accountant.schemas.user_schemas as schemas
import accountant.database.handlers.user_handler as user_db_handler
from accountant.services.service_utils.accountant_exceptions import NotFoundError
from fastapi import HTTPException, status
import accountant.services.service_utils.auth_utils as auth_utils


async def check_user(**kwargs):
    try:
        return await user_db_handler.check_user(**kwargs)

    except NotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    ...


async def create_user(user: schemas.User):
    try:
        user_profile = await user_db_handler.check_user(**{"email": user.email})

        if user_profile:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="account exists"
            )

    except NotFoundError:

        user_profile.password = auth_utils.hash_password(plain_password=user.password)
        user_profile = await user_db_handler.create_user(user=user)

        await user_db_handler.create_user_group(user_uid=user_profile.user_uid)

        # TODO Notification

        user_profile_dict = {"user_uid": str(user_profile.user_uid)}
        access_token, refresh_token = (
            auth_utils.create_access_token(data=user_profile_dict),
            auth_utils.create_refresh_token(data=user_profile_dict),
        )

        ...
