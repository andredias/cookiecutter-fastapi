import hmac
from base64 import b64encode
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any, Optional

import orjson as json

from . import config
from .resources import redis


async def create_session(
    prefix: str, data: dict[str, Any], lifetime: Optional[int] = None
) -> str:
    """
    Creates a random session_id and stores the related data into Redis.
    """
    session_id: str = f'{prefix}:{token_urlsafe(config.SESSION_ID_LENGTH)}'
    lifetime = lifetime or config.SESSION_LIFETIME
    await redis.set(session_id, json.dumps(data), ex=lifetime)
    return session_id


async def get_session(
    session_id: str, expire: Optional[int] = None
) -> dict[str, Any]:
    payload = await redis.get(session_id)
    if payload is None:
        return {}
    data = json.loads(payload)
    expire = expire or config.SESSION_LIFETIME
    await redis.expire(session_id, expire)  # renew expiration date
    return data


async def delete_session(*args) -> None:
    await redis.delete(*args)


async def session_exists(session_id: str) -> bool:
    return await redis.exists(session_id)


def create_csrf(session_id: str) -> str:
    """
    Based on
    https://www.jokecamp.com/blog/examples-of-creating-base64-hashes-using-hmac-sha256-in-different-languages/#python3  # noqa: E501
    """
    message = bytes(session_id, 'utf-8')
    token = b64encode(hmac.new(config.SECRET_KEY, message, sha256).digest())
    return token.decode('utf-8')


def is_valid_csrf(session_id: str, csrf: str) -> bool:
    return create_csrf(session_id) == csrf
