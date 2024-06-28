from fastapi import APIRouter, status, Depends, Body
import accountant.services.auth_service as auth_service
import accountant.schemas.user_schemas as schemas
from accountant.services.service_utils.auth_utils import get_current_user
from pydantic import EmailStr

api_router = APIRouter(prefix="/v1/auth", tags=["User Authentication"])


@api_router.post(
    path="/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserProfile,
)
async def sign_up(user_cred: schemas.User, user_group_token: str = None):

    return await auth_service.create_user(
        user=user_cred, user_group_token=user_group_token
    )


@api_router.post(
    path="/login",
    response_model=schemas.AccessRefreshPayload,
    status_code=status.HTTP_200_OK,
)
async def login(login_cred: schemas.Login):

    return await auth_service.login(login_cred=login_cred)


@api_router.get(
    path="/me",
    response_model=schemas.UserExtendedProfile,
    status_code=status.HTTP_200_OK,
)
async def me(user_profile: schemas.UserExtendedProfile = Depends(get_current_user)):

    return user_profile


@api_router.patch(
    path="/re-verify",
    status_code=status.HTTP_200_OK,
)
async def re_verify_account(email: EmailStr = Body(embed=True)):

    return await auth_service.resend_verification_token(email=email)


@api_router.patch(path="/verify-account", status_code=status.HTTP_200_OK)
async def verify_account(token: str):
    return await auth_service.verify_user(token=token)


@api_router.patch(path="/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(email: EmailStr = Body(embed=True)):

    return await auth_service.forgot_password(email=email)


@api_router.patch(path="/re-forgot-password", status_code=status.HTTP_200_OK)
async def reset_password(
    token: str = Body(embed=True), new_password: str = Body(embed=True)
):

    return await auth_service.reset_password(token=token, new_password=new_password)
