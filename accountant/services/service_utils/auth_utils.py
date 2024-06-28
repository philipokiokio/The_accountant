import logging
from datetime import datetime, timedelta
from uuid import UUID
import jwt
from jwt.exceptions import InvalidTokenError, InvalidSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)
from passlib.context import CryptContext
import accountant.services.auth_service as user_service

import accountant.services.service_utils.redis_utils as redis_utils
from accountant.root.settings import Settings
from accountant.schemas.user_schemas import TokenData

LOGGER = logging.getLogger(__name__)
settings = Settings()

# PASSWORD HASHING AND VALIDATOR
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


# AUTHENTICATION
bearer = HTTPBearer()
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 60 * 24 * 7
REFRESH_SECRET_KEY = settings.ref_jwt_secret_key
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 24 * 14


# TOP_LEVEL_SIGNER
ITS_DANGEROUS_TOKEN_KEY = settings.second_signer_key


def sign_token(jwt_token: str) -> str:
    token_signer = URLSafeTimedSerializer(secret_key=ITS_DANGEROUS_TOKEN_KEY)
    token = token_signer.dumps(obj=jwt_token)
    return token


def resolve_token(signed_token: str, max_age: int = None):
    token_signer = URLSafeTimedSerializer(secret_key=ITS_DANGEROUS_TOKEN_KEY)
    try:
        return token_signer.loads(s=signed_token, max_age=max_age)
    except (BadTimeSignature, BadSignature, SignatureExpired) as e:
        LOGGER.exception(e)
        raise Exception


def create_access_token(data: dict):
    expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)
    dangerous_access_token = sign_token(jwt_token=encoded_jwt)

    return dangerous_access_token


def create_refresh_token(data: dict):
    expire = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=data, key=REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    # add signed_token
    dangerous_refresh_token = sign_token(jwt_token=encoded_jwt)
    return dangerous_refresh_token


async def verify_access_token(token: str):
    cache_token = redis_utils.get_token_blacklist(token=token)
    if cache_token:
        raise HTTPException(detail="access has been revoked, login", status_code=401)
    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")

        credentials_exception()

    try:
        payload = jwt.decode(token=jwt_token, key=SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_uid")
        if id is None:
            LOGGER.error(f"Decrypted JWT has not id in payload. {payload}")
            credentials_exception()

        token_data = TokenData(user_uid=UUID(id))
    except (InvalidTokenError, InvalidSignatureError) as e:
        LOGGER.exception(e)
        LOGGER.error("JWT Decryption Error")
        credentials_exception()

    return token_data


async def ws_access_token(token: str):
    token_data = await verify_access_token(token=token)
    return token_data.user_uid


async def verify_refresh_token(token: str):
    cache_token = redis_utils.get_token_blacklist(token=token)
    if cache_token:
        raise HTTPException(detail="access has been revoked, login", status_code=401)
    try:
        jwt_token = resolve_token(
            signed_token=token, max_age=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    except Exception:
        LOGGER.error("Access_token top level signer decrypt failed")

        credentials_exception()

    try:
        payload = jwt.decode(
            token=jwt_token, key=REFRESH_SECRET_KEY, algorithms=ALGORITHM
        )
        id: str = payload.get("user_uid")
        if id is None:
            credentials_exception()

        token_data = TokenData(user_uid=id)
    except (InvalidTokenError, InvalidSignatureError) as e:
        LOGGER.exception(e)
        credentials_exception()

    return token_data


async def get_new_access_token(token: str):
    token_data = await verify_refresh_token(token=token)
    token_dict = {
        "user_uid": str(token_data.user_uid),
    }
    return create_access_token(data=token_dict)


def credentials_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def abstract_token(
    auth_credential: HTTPAuthorizationCredentials = Depends(bearer),
):
    if not auth_credential.credentials:
        credentials_exception()

    return await verify_access_token(token=auth_credential.credentials)


async def get_current_user(
    token: TokenData = Depends(abstract_token),
):
    user = await user_service.get_user(user_uid=token.user_uid)
    if user.is_verified is False:
        raise HTTPException(
            detail="account is not verified",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return user
