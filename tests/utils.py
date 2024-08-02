from decimal import Decimal
from faker import Faker
from accountant.schemas import (
    user_schemas,
)
import random
from uuid import UUID, uuid4
from random import randint
from datetime import date, datetime, timedelta

faker = Faker()


faker["en_US"]


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def get_user():
    return user_schemas.User(
        name=f"{faker.first_name(), faker.last_name()}",
        email=faker.email(),
        password=faker.company(),
    )


def get_user_extended_profile(user: user_schemas.User, user_uid: UUID):

    return user_schemas.UserExtendedProfile(
        **user.model_dump(),
        user_uid=user_uid,
        is_verified=True,
        date_created_utc=datetime.utcnow(),
    )


def get_user_group(user_uid: UUID, user_group_uid: UUID):

    return user_schemas.UserGroup(owner_uid=user_uid, user_group_uid=user_group_uid)
