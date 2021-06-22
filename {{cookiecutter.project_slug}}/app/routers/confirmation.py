from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from loguru import logger
from pydantic import EmailStr

from ..models.user import (
    UserInfo,
    UserInsert,
    UserPatch,
    db,
    get_user_by_email,
    update,
)
from ..schemas.user import check_password
from ..sessions import (
    create_session,
    delete_session,
    get_session_payload,
    session_exists,
)
from .user import create_user

router = APIRouter()


def valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


async def confirm_email_session(session_id: str = Body(...)) -> str:
    try:
        email, _ = session_id.split(':')
    except ValueError:
        raise HTTPException(422)
    if not (valid_email(email) and await session_exists(session_id)):
        raise HTTPException(404)
    return email


def validate_password(password: str = Body(...)) -> str:
    try:
        check_password(password)
    except ValueError as error:
        raise HTTPException(422, str(error))
    return password


@router.get('/send_reset_password_instructions')
async def send_reset_password_instructions(
    email: EmailStr, language: str = Query('en')
):
    """
    Send an email with a link to create a new password
    """
    user = await get_user_by_email(email)
    if not user:
        logger.warning(f'email {email} non-existent in the database')
        return
    await create_session(email, str(user.id), lifetime=3600)
    # TODO: send email in the background
    return


@router.post('/reset_password')
@db.transaction()
async def reset_password(
    session_id: str = Body(...),
    email: EmailStr = Depends(confirm_email_session),
    password: str = Depends(validate_password),
):
    payload = await get_session_payload(session_id)
    if not payload:
        logger.error(f'{session_id} should have a user_id as payload')
        raise HTTPException(500)
    user_id = int(payload)
    await update(user_id, UserPatch(password=password))
    await delete_session(session_id)
    return


@router.get('/send_register_user_instructions')
async def send_register_user_instructions(
    email: EmailStr, language: str = Query('en')
):
    user = await get_user_by_email(email)
    if user:
        logger.warning(f'email {email} already exists in the database')
        return
    await create_session(email, lifetime=3600)
    # TODO: send email confirmation in background
    return


@router.post('/register_user', response_model=UserInfo, status_code=201)
async def register_user(
    user: UserInsert,
    session_id: str = Body(...),
    email: str = Depends(confirm_email_session),
):
    if user.email != email:
        raise HTTPException(422)
    await delete_session(session_id)
    return await create_user(user)
