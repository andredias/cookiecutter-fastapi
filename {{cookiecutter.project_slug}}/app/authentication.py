import re

from fastapi import Cookie, Header, HTTPException

from .models.user import get_user
from .schemas.user import UserInfo
from .sessions import is_valid_csrf, session_exists


async def authenticated_user(
    session_id: str = Cookie(None), x_csrf_token: str = Header(None)
) -> UserInfo:
    """
    FastAPI Dependency to verify session_id and its correspondent csrf_token.

    Obs: Cookie(...) and Header(...) would raise 'field required' errors
         instead of 401 errors.
         So, we must use Cookie(None) instead of Cookie(...)
    """
    if not (
        session_id
        and x_csrf_token
        and (match := re.match(r'user:(\d+):', session_id))
        and is_valid_csrf(session_id, x_csrf_token)
        and await session_exists(session_id)
    ):
        raise HTTPException(status_code=401)
    user_id = int(match.group(1))
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user
