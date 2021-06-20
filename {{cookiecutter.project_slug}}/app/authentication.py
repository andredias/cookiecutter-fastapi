import re

from fastapi import Cookie, Depends, Header, HTTPException

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
        and session_exists(session_id)
    ):
        raise HTTPException(status_code=401)
    user_id = int(match.group(1))
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user


async def admin_user(
    user: UserInfo = Depends(authenticated_user),
) -> UserInfo:
    if not user.is_admin:
        raise HTTPException(status_code=403)
    return user


async def resource_owner(
    id: int,
    current_user: UserInfo = Depends(authenticated_user),
) -> UserInfo:
    if id == current_user.id:
        return current_user
    if not current_user.is_admin:
        raise HTTPException(403)
    user = await get_user(id)
    if not user:
        raise HTTPException(404)
    return user
