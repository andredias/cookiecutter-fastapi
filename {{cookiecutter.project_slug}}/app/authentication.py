from typing import Any

from fastapi import Cookie, Depends, Header, HTTPException

from .models.user import get_user
from .schemas.user import UserInfo
from .sessions import get_session, is_valid_csrf


async def authenticated_session(
    session_id: str = Cookie(None), x_csrf_token: str = Header(None)
) -> dict[str, Any]:
    """
    FastAPI Dependency to get authenticated session data.
    If no valid session is found, it raises an HTTP Error 401
    """
    if (
        session_id
        and x_csrf_token
        and is_valid_csrf(session_id, x_csrf_token)
        and (data := await get_session(session_id))
    ):
        return data
    else:
        raise HTTPException(status_code=401)


async def authenticated_user(
    data: dict[str, Any] = Depends(authenticated_session)
) -> UserInfo:
    user = await get_user(data['id'])
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
