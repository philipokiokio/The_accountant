from uuid import UUID

import accountant.root.redis_manager as redis_bq


# AUTH TOKEN


FORGET_PASSWORD_EXPIRE = 60 * 60 * 5


def forget_key_generator(token: int):
    return f"Forget-Key-{token}"


def add_forget_token(token: int, email: str):
    key = forget_key_generator(token=token)

    return redis_bq.acc_redis.set(name=key, value=email, ex=FORGET_PASSWORD_EXPIRE)


def get_forget_token(token: int):
    key = forget_key_generator(token=token)

    return redis_bq.acc_redis.get(name=key)


def delete_forget_token(token: int):
    key = forget_key_generator(token=token)
    return redis_bq.acc_redis.delete(key)


def black_list_bearer_tokens(access_token: str):
    return f"black-list-token-{access_token}"


def add_token_blacklist(access_token: str, refresh_token: str):
    for token in [access_token, refresh_token]:
        key = black_list_bearer_tokens(access_token=token)
        redis_bq.acc_redis.set(name=key, value=token, ex=60 * 60 * 24 * 7)


def get_token_blacklist(token: str):
    key = black_list_bearer_tokens(access_token=token)
    return redis_bq.acc_redis.get(name=key)


# Vefication Token


# Verification Token Generator
def user_verification_token_generator(user_uid: UUID):
    return f"account_verification_token_{user_uid}"


# Token Key Generator
def verification_token_generator(token: str):
    return f"verification_token_{token}"


def add_token_to_store(token: str, user_uid: UUID):
    key = verification_token_generator(token=token)

    return redis_bq.acc_redis.set(name=key, value=str(user_uid), ex=1800)


def get_verification_token_user(token: str):
    key = verification_token_generator(token=token)
    return redis_bq.acc_redis.get(name=key)


def remove_verification_token_user(token: str):
    key = verification_token_generator(token=token)
    return redis_bq.acc_redis.delete(key)


def add_user_verification_token(user_uid: UUID, token: str):
    key = user_verification_token_generator(user_uid=user_uid)
    add_token_to_store(token=token, user_uid=user_uid)
    return redis_bq.acc_redis.set(name=key, value=token, ex=1800)


def get_user_verification_token(user_uid: UUID):
    key = user_verification_token_generator(user_uid=user_uid)
    return redis_bq.acc_redis.get(name=key)


def remove_user_verification_token(user_uid: UUID):
    key = user_verification_token_generator(user_uid=user_uid)
    return redis_bq.acc_redis.delete(key)
