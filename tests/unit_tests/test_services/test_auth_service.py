from unittest.mock import patch, AsyncMock, Mock
import pytest
from fastapi import HTTPException
from accountant.services.service_utils.accountant_exceptions import NotFoundError
from accountant.services.service_utils.token_utils import gr_token_gen
import tests.utils as general_utils
from uuid import uuid4
import accountant.services.auth_service as auth_service


@patch("accountant.services.auth_service.send_mail")
@patch("accountant.services.auth_service.user_db_handler", new_callable=AsyncMock)
@patch("accountant.services.auth_service")
@patch("accountant.services.auth_service.redis_utils")
@patch("accountant.services.auth_service.gr_token_gen")
@patch("accountant.services.auth_service.auth_utils")
async def test_create_user_happy_path(
    mock_auth_utils,
    mock_token_gen,
    mock_redis,
    mock_auth_service,
    mock_auth_db,
    mock_mailer,
):

    token = gr_token_gen()
    user_uid = uuid4()
    access_uid = str(uuid4())
    refresh_uid = str(uuid4())

    user = general_utils.get_user()
    user_extended_profile = general_utils.get_user_extended_profile(
        user=user, user_uid=user_uid
    )
    mock_auth_db.create_user.return_value = user_extended_profile

    mock_auth_db.create_user_group.return_value = None
    mock_auth_db.check_user.side_effect = NotFoundError
    mock_auth_service.create_user_group = AsyncMock(return_value=None)

    mock_token_gen.return_value = token
    mock_redis.add_user_verification_token = Mock(return_value=None)

    mock_mailer.return_value = None

    mock_auth_utils.hash_password = Mock(return_value=user.password)
    mock_auth_utils.create_access_token = Mock(return_value=access_uid)
    mock_auth_utils.create_refresh_token = Mock(return_value=refresh_uid)

    user_access_cred = await auth_service.create_user(user=user, user_group_token=None)

    mock_auth_db.create_user.assert_awaited_once_with(user=user)
    assert user_access_cred.access_token == access_uid
    assert user_access_cred.refresh_token == refresh_uid


@patch("accountant.services.auth_service.user_db_handler", new_callable=AsyncMock)
async def test_create_user_sad_path(
    mock_auth_db,
):

    user_uid = uuid4()

    user = general_utils.get_user()
    user_extended_profile = general_utils.get_user_extended_profile(
        user=user, user_uid=user_uid
    )
    mock_auth_db.create_user.return_value = user_extended_profile

    mock_auth_db.check_user.return_value = user_extended_profile

    with pytest.raises(HTTPException):

        await auth_service.create_user(user=user, user_group_token=None)
