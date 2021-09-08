from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel, EmailStr

from ..models.user import get_user_by_login
from ..schemas.user import UserInfo
from ..sessions import create_csrf, create_session, delete_session

router = APIRouter()


class LoginInfo(BaseModel):
    email: EmailStr
    password: str


@router.post('/login', response_model=UserInfo)
async def login(
    rec: LoginInfo, response: Response, session_id: str = Cookie(None)
) -> UserInfo:
    if session_id:
        await delete_session(session_id)
    user = await get_user_by_login(rec.email, rec.password)
    if user is None:
        raise HTTPException(status_code=404, detail='invalid email or password')
    session_id = await create_session(f'user:{user.id}')
    response.set_cookie(
        key='session_id', value=session_id, httponly=True, secure=True
    )
    response.headers['x-csrf-token'] = create_csrf(session_id)
    return user


@router.post('/logout', status_code=204)
async def logout(response: Response, session_id: str = Cookie(None)) -> None:
    if session_id is not None:
        await delete_session(session_id)
    response.status_code = 204
    response.delete_cookie(key='session_id')
    return
