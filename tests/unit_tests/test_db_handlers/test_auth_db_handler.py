import uuid
import tests.utils as general_utils


import pytest

from accountant.database.handlers import user_handler
import tests.unit_tests.test_db_handlers.db_test_utils as seeder_db_handler
from accountant.services.service_utils.accountant_exceptions import (
    DeleteError,
    NotFoundError,
    UpdateError,
    CreateError,
)


async def test_create_user_happy_path(session):

    user = general_utils.get_user()

    user_profile = await user_handler.create_user(user=user)
    assert user.email == user_profile.email
    assert user.name == user_profile.name


async def test_create_user_sad_path(session):

    user = general_utils.get_user()

    user_profile = await seeder_db_handler.create_user()

    user.email = user_profile.email

    with pytest.raises(CreateError):
        await user_handler.create_user(user=user)
