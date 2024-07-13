from itsdangerous import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)
from uuid import UUID
import logging

import accountant.schemas.investment_schemas as schemas


LOGGER = logging.getLogger(__name__)


def sign_data(data: str, user_group_uid: UUID) -> str:
    token_signer = URLSafeTimedSerializer(secret_key=str(user_group_uid))
    token = token_signer.dumps(obj=data)
    return token


def resolve_token(signed_token: str, user_group_uid: UUID):
    token_signer = URLSafeTimedSerializer(secret_key=str(user_group_uid))
    try:
        return token_signer.loads(s=signed_token)
    except (BadTimeSignature, BadSignature, SignatureExpired) as e:
        LOGGER.exception(e)
        raise Exception


def platform_encoder(platform: schemas.Platform, user_group_uid: UUID):

    if platform.access_credential is not None:
        platform.access_credential = schemas.PlatformAccessCredential(
            **platform.access_credential.model_dump()
        )

        if platform.access_credential.email:

            platform.access_credential.email = sign_data(
                data=platform.access_credential.email, user_group_uid=user_group_uid
            )

        if platform.access_credential.access_username:
            platform.access_credential.access_username = sign_data(
                data=platform.access_credential.access_username,
                user_group_uid=user_group_uid,
            )

        if platform.access_credential.password:

            platform.access_credential.password = sign_data(
                data=platform.access_credential.password, user_group_uid=user_group_uid
            )

        if platform.access_credential.transaction_pin:
            platform.access_credential.transaction_pin = sign_data(
                data=platform.access_credential.transaction_pin,
                user_group_uid=user_group_uid,
            )
    return platform


def platform_decoder(platform: schemas.PlatformProfile):

    if platform.access_credential is not None:
        platform.access_credential = schemas.PlatformAccessCredential(
            **platform.access_credential.model_dump()
        )

        if platform.access_credential.email:

            platform.access_credential.email = resolve_token(
                signed_token=platform.access_credential.email,
                user_group_uid=platform.user_group_uid,
            )

        if platform.access_credential.access_username:
            platform.access_credential.access_username = resolve_token(
                signed_token=platform.access_credential.access_username,
                user_group_uid=platform.user_group_uid,
            )

        if platform.access_credential.password:

            platform.access_credential.password = resolve_token(
                signed_token=platform.access_credential.password,
                user_group_uid=platform.user_group_uid,
            )

        if platform.access_credential.transaction_pin:
            platform.access_credential.transaction_pin = resolve_token(
                signed_token=platform.access_credential.transaction_pin,
                user_group_uid=platform.user_group_uid,
            )

    return platform
