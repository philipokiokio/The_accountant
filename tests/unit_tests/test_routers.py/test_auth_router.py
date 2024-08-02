from unittest.mock import patch, AsyncMock

from fastapi import HTTPException, status
from accountant.root.app import app
import tests.utils as general_utils

from uuid import uuid4
from fastapi.testclient import TestClient
import accountant.schemas.user_schemas as schemas


TEST_CLIENT = TestClient(app=app)


@patch("accountant.routers.auth_router.auth_service")
async def test_sign_up_happy_path(mock_auth_service):

    user = general_utils.get_user()

    access_token = str(uuid4())
    refresh_token = str(uuid4())

    expected_resp = schemas.AccessRefreshPayload(
        access_token=access_token, refresh_token=refresh_token
    )
    mock_auth_service.create_user = AsyncMock(return_value=expected_resp.model_dump())

    response = TEST_CLIENT.post(url="/v1/auth/sign-up", json=user.model_dump())
    response_json = response.json()
    assert response.status_code == 201
    assert response_json == expected_resp.model_dump()

    mock_auth_service.create_user.assert_awaited_once_with(
        user=user, user_group_token=None
    )


@patch("accountant.routers.auth_router.auth_service")
async def test_sign_up_sad_path(mock_auth_service):

    user = general_utils.get_user()

    mock_auth_service.create_user.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="account exists"
    )

    response = TEST_CLIENT.post(url="/v1/auth/sign-up", json=user.model_dump())
    response_json = response.json()
    assert response.status_code == 400
    assert response_json == {"detail": "account exists"}
