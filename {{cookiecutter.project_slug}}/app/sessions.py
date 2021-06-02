import hmac
from base64 import b64encode
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any, Optional

import orjson as json

from . import config
from . import resources as res


async def create_session(data: dict[str, Any]) -> str:
    """
    Creates a random session_id and stores the related data into Redis.
    """
    session_id: str = token_urlsafe(config.SESSION_ID_LENGTH)
    await res.redis.set(session_id, json.dumps(data))
    await res.redis.expire(session_id, config.SESSION_LIFETIME)
    return session_id


async def get_session(session_id: str) -> Optional[dict[str, Any]]:
    payload = await res.redis.get(session_id)
    data = None
    if payload is not None:
        data = json.loads(payload)
        await res.redis.expire(
            session_id, config.SESSION_LIFETIME
        )  # renew expiration date
    return data


async def delete_session(session_id: str) -> None:
    await res.redis.delete(session_id)


async def session_exists(session_id: str) -> bool:
    return await res.redis.exists(session_id)


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
