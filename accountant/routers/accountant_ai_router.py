from uuid import UUID

from fastapi import APIRouter, Depends, status

# import accountant.schemas.investment_schemas as schemas
import accountant.services.fin_ai_service as accountant_ai_service
from accountant.schemas.user_schemas import UserExtendedProfile
from accountant.services.service_utils.auth_utils import (
    get_current_user,
    get_user_group_uid,
)

api_router = APIRouter(prefix="/v1/accountant-ai", tags=["Accountant AI"])


@api_router.get(path="", status_code=status.HTTP_200_OK)
async def accountant_llm_prompter(
    user_profile: UserExtendedProfile = Depends(get_current_user),
    user_group_uid: UUID = Depends(get_user_group_uid),
):

    return accountant_ai_service.proto_func(
        user_uid=user_profile.user_uid, user_group_uid=user_group_uid
    )
