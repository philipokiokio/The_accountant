import logging
from uuid import UUID

from fastapi import HTTPException, status

import accountant.database.handlers.user_handler as user_db_handler
import accountant.schemas.user_schemas as schemas
import accountant.services.service_utils.auth_utils as auth_utils
import accountant.services.service_utils.redis_utils as redis_utils
from accountant.root.utils.mailer import send_mail
from accountant.services.service_utils.accountant_exceptions import NotFoundError
from accountant.services.service_utils.token_utils import gr_token_gen

LOGGER = logging.getLogger(__name__)


async def check_user(**kwargs):
    try:
        return await user_db_handler.check_user(**kwargs)

    except NotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    ...


async def create_user(user: schemas.User, user_group_token: str = None):
    try:
        user_profile = await user_db_handler.check_user(**{"email": user.email})

        if user_profile:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="account exists"
            )

    except NotFoundError:

        user.password = auth_utils.hash_password(plain_password=user.password)
        user_profile = await user_db_handler.create_user(user=user)

        await user_db_handler.create_user_group(user_uid=user_profile.user_uid)

        # TODO Notification

        user_profile_dict = {"user_uid": str(user_profile.user_uid)}
        access_token, refresh_token = (
            auth_utils.create_access_token(data=user_profile_dict),
            auth_utils.create_refresh_token(data=user_profile_dict),
        )

        if user_group_token:
            try:
                # TODO DECODE THIS TOKEN
                user_group_uid = None
                try:
                    user_group_uid = auth_utils.resolve_token(
                        signed_token=user_group_token
                    )
                except Exception:
                    pass

                if user_group_uid:
                    user_group_uid = UUID(user_group_uid)
                    dependent_profile = await dependent_check(
                        email=user_profile.email, user_group_uid=user_group_uid
                    )
                    await update_dependent(
                        uid=dependent_profile.uid,
                        user_group_uid=dependent_profile.user_group_uid,
                        dependent_invitation=schemas.UserGroupInvitationUpdate(
                            is_accepted=True
                        ),
                    )

                    await add_to_user_group(
                        user_uid=user_profile.user_uid,
                        user_group_uid=dependent_profile.user_group_uid,
                    )
                    await user_db_handler.update_user(
                        user_uid=user_profile.user_uid,
                        user_update=schemas.UserUpdate(
                            added_to_user_group_uid=user_group_uid
                        ),
                    )

            except NotFoundError:
                # TODO RESOLVER
                pass
        else:
            # User GROUP
            await create_user_group(user_uid=user_profile.user_uid)

        user_token = gr_token_gen()
        redis_utils.add_user_verification_token(
            user_uid=user_profile.user_uid, token=user_token
        )
        await send_mail(
            subject="Verify your account on The Accountant",
            reciepients=[user_profile.email],
            payload={"token": user_token},
            template="user_auth/token_email_template.html",
        )

        return schemas.AccessRefreshPayload(
            access_token=access_token, refresh_token=refresh_token
        )


async def get_user(user_uid: UUID):

    try:
        return await user_db_handler.get_user(user_uid=user_uid)

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )


async def verify_user(token: str):

    user_uid = redis_utils.get_verification_token_user(token=token)

    if user_uid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="token is invalid"
        )

    stored_token = redis_utils.get_user_verification_token(user_uid=user_uid)

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="token is invalid"
        )

    if stored_token == token:
        await get_user(user_uid=UUID(user_uid))
        redis_utils.remove_user_verification_token(user_uid=user_uid)
        redis_utils.remove_verification_token_user(token=token)
        return await user_db_handler.update_user(
            user_uid=UUID(user_uid), user_update=schemas.UserUpdate(is_verified=True)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="token is invalid/expired"
        )


async def resend_verification_token(email: str):

    user_profile = await check_user(email=email)
    if user_profile.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user is already verified"
        )
    user_token = gr_token_gen()
    redis_utils.add_user_verification_token(
        user_uid=user_profile.user_uid, token=user_token
    )

    await send_mail(
        subject="Verify your account on The Accountant",
        reciepients=[user_profile.email],
        payload={"token": user_token},
        template="user_auth/token_email_template.html",
    )

    return {"message": "verification email sent"}


async def logout(access_token: str, refresh_token: str):

    redis_utils.add_token_blacklist(
        access_token=access_token, refresh_token=refresh_token
    )

    return {}


async def login(login_cred: schemas.Login):
    login_cred.email = login_cred.email.lower()

    user_profile = await check_user(email=login_cred.email)

    if (
        auth_utils.verify_password(
            plain_password=login_cred.password, hashed_password=user_profile.password
        )
        is False
    ):

        raise HTTPException(
            status=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password credential",
        )

    if user_profile.is_verified is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user is not verified"
        )

    user_profile_dict = {"user_uid": str(user_profile.user_uid)}
    access_token, refresh_token = (
        auth_utils.create_access_token(data=user_profile_dict),
        auth_utils.create_refresh_token(data=user_profile_dict),
    )

    return schemas.AccessRefreshPayload(
        access_token=access_token, refresh_token=refresh_token
    )


async def update_user(user_uid: UUID, user_update: schemas.UserUpdate):

    await get_user(user_uid=user_uid)

    return await user_db_handler.update_user(user_uid=user_uid, user_update=user_update)


async def delete_user(user_uid: UUID):
    await get_user(user_uid=user_uid)

    await user_db_handler.delete_user(user_uid=user_uid)

    return {}


# forget password
async def forgot_password(email: str):
    await check_user(email=email)

    # Create a Token 4 OTP
    token = gr_token_gen()

    redis_utils.add_forget_token(token=token, email=email)
    # send mail
    await send_mail(
        subject="Forgot Password",
        reciepients=[email],
        payload={"token": token},
        template="user_auth/token_email_template.html",
    )
    return {"message": "mail sent"}


async def reset_password(token: str, new_password: str):
    email = redis_utils.get_forget_token(token=token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="token expired or not valid"
        )

    user_profile = await check_user(email=email)

    new_password = auth_utils.hash_password(plain_password=new_password)
    updated_user_profile = await update_user(
        user_update=schemas.UserUpdate(password=new_password),
        user_uid=user_profile.user_uid,
    )

    redis_utils.delete_forget_token(token=token)
    return updated_user_profile


async def all_user_update(user_uids: UUID):

    return await user_db_handler.all_user_update(
        user_uids=user_uids,
        user_updates=[schemas.UserUpdate(is_alive=False)] * len(user_uids),
    )


########################################## User Group ##########################################################


async def get_user_group(user_uid: UUID):

    try:

        return await user_db_handler.get_user_group(user_uid=user_uid)

    except NotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user group not found"
        )


async def create_user_group(user_uid: UUID):

    try:
        return await get_user_group(user_uid=user_uid)

    except HTTPException:
        user_group_profile = await user_db_handler.create_user_group(user_uid=user_uid)
        return user_group_profile


async def get_user_in_u_group(user_group_uid: UUID, user_uid: UUID):

    try:
        await user_db_handler.get_user_in_user_group(
            user_group_uid=user_group_uid, user_uid=user_uid
        )

    except NotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found in the user group",
        )


async def get_users_in_U_group(user_group_uid: UUID):

    return await user_db_handler.get_users_in_user_group(user_group_uid=user_group_uid)


async def add_to_user_group(user_uid: UUID, user_group_uid: UUID):
    try:
        user_ug_profile = await get_user_in_u_group(
            user_group_uid=user_group_uid, user_uid=user_uid
        )
    except HTTPException:
        if user_ug_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user is a member of this user_group",
            )

        return await user_db_handler.add_user_to_group(
            user_group_memb=schemas.UserGroupMember(
                user_group_uid=user_group_uid, user_uid=user_uid
            )
        )


async def delete_user_from_user_group(user_uid: UUID, user_group_uid: UUID):

    await get_user_in_u_group(user_group_uid=user_group_uid, user_uid=user_uid)

    await user_db_handler.delete_from_user_group(
        user_uid=user_uid, user_group_uid=user_group_uid
    )

    return {}


async def change_password(old_password: str, new_password: str, user_uid: UUID):

    user_profile = await check_user(user_uid=user_uid)

    if (
        auth_utils.verify_password(
            plain_password=old_password, hashed_password=user_profile.password
        )
        is False
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="incorrect information"
        )

    user_profile.password = auth_utils.hash_password(plain_password=new_password)
    return await update_user(
        user_uid=user_uid,
        user_update=schemas.UserUpdate(password=user_profile.password),
    )


################################################## DEPENDENT INVITATION #######################################


async def dependent_check(email: str, user_group_uid: UUID):

    try:
        email = email.lower()
        return await user_db_handler.check_dependent(
            email=email, user_group_uid=user_group_uid
        )

    except NotFoundError as e:

        raise e


async def add_dependent(emails: str, user_group_uid: UUID):

    uninvited = []
    for email in emails:

        try:
            await dependent_check(emai=email, user_group_uid=user_group_uid)
        except NotFoundError:

            uninvited.append(
                schemas.UserGroupInvitation(email=email, user_group_uid=user_group_uid)
            )

    return await user_db_handler.create_dependent(user_g_iv=uninvited)


async def get_dependents(user_group_uid: UUID):

    return await user_db_handler.get_all_dependents(user_group_uid=user_group_uid)


async def get_dependent(user_group_uid: UUID, uid: UUID):

    try:
        return await user_db_handler.get_dependent(
            user_group_uid=user_group_uid, uid=uid
        )

    except NotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="record of invitation not found",
        )


async def update_dependent(
    uid: UUID,
    user_group_uid: UUID,
    dependent_invitation: schemas.UserGroupInvitationUpdate,
):

    await get_dependent(user_group_uid=user_group_uid, uid=uid)

    return await user_db_handler.update_dependent(
        user_group_uid=user_group_uid,
        uid=uid,
        dependent_invitation_update=dependent_invitation,
    )


async def delete_dependent(uid: UUID, user_group_uid: UUID):

    await get_dependent(user_group_uid=user_group_uid, uid=uid)

    await user_db_handler.delete_dependent(user_group_uid=user_group_uid, uid=uid)
    return {}


##################################  ACTIONS #####################################################


async def send_invitation():

    user_profiles = await user_db_handler.get_all_user()

    for user_profile in user_profiles:

        # This can be lazy loaded to make this on true loop

        # user_dependents =
        await get_dependents(user_group_uid=user_profile.user_group.user_group_uid)

        # dependent_emails = [dependent.email for dependent in user_dependents.result_set]

        # ug_token = auth_utils.sign_token(jwt_token=str(user_profile.user_group_uid))

        # TODO Send to Mailer Job


async def update_all_to_non_alive_users():

    user_profiles = await user_db_handler.get_all_user(is_alive=True)
    user_uids = []
    user_emails = []

    for user in user_profiles:
        user_uids.append(user.user_uid)
        user_emails.append(user.email)

    await all_user_update(user_uids=user_uids)

    # send to Mail JOB

    # Send PUSH NOTIFICATION


async def i_am_alive(token: str):
    try:
        user_uid = auth_utils.resolve_token(
            signed_token=token, max_age=60 * 60 * 24 * 30
        )
        await update_user(
            user_uid=user_uid, user_update=schemas.UserUpdate(is_alive=True)
        )

    except Exception as e:

        LOGGER.exception(e)


# FUNC To Send Renminder to Users and another Fuction to Send email to Dependents to Join
# FUNC To Send Renminder to Users and another Fuction to Send email to Dependents to Join
