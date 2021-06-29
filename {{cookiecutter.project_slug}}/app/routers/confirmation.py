from pathlib import Path
from urllib.parse import urlencode

from email_validator import EmailNotValidError, validate_email
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
)
from fastapi_mail import MessageSchema
from loguru import logger
from pydantic import EmailStr

from .. import config
from ..mailer import mailer, templates
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
    email: EmailStr,
    background_tasks: BackgroundTasks,
    language: str = Query('en'),
):
    """
    Send an email with a link to create a new password
    """
    user = await get_user_by_email(email)
    if not user:
        logger.warning(f'email {email} non-existent in the database')
        return

    if await session_exists(f'{email}:*'):
        raise HTTPException(429)

    session_id = await create_session(email, str(user.id), lifetime=3600)
    if language == 'pt-BR':
        subject = f'Redefina a senha para {config.APP_NAME}'
        app_name = config.APP_NAME
    else:
        subject = f'Reset your {config.APP_NAME} password'
        app_name = config.APP_NAME

    params = {
        'name': user.name,
        'app_name': app_name,
        'app_url': config.APP_URL,
        'email': email,
        'reset_password_link': str(
            Path(
                config.APP_URL,
                'reset_password',
                urlencode(dict(session_id=session_id)),
            )
        ),
    }
    template = templates.get_template(f'reset_password.{language.lower()}.txt')
    text = template.render(params)
    template = templates.get_template(f'reset_password.{language.lower()}.html')
    html = template.render(params)
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=text,
        html=html,
    )
    background_tasks.add_task(mailer.send_message, message)
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
    email: EmailStr,
    background_tasks: BackgroundTasks,
    language: str = Query('en'),
):
    user = await get_user_by_email(email)
    if user:
        logger.warning(f'email {email} already exists in the database')
        return

    if await session_exists(f'{email}:*'):
        raise HTTPException(429)

    session_id = await create_session(email, lifetime=3600)
    if language == 'pt-BR':
        subject = f'Confirme seu endereço de email para {config.APP_NAME}'
        app_name = config.APP_NAME
    else:
        subject = f'Confirm your email address to {config.APP_NAME}'
        app_name = config.APP_NAME

    params = {
        'app_name': app_name,
        'app_url': config.APP_URL,
        'email': email,
        'register_user_link': str(
            Path(
                config.APP_URL,
                'register_user',
                urlencode(dict(session_id=session_id)),
            )
        ),
    }
    template = templates.get_template(
        f'email_confirmation.{language.lower()}.txt'
    )
    text = template.render(params)
    template = templates.get_template(
        f'email_confirmation.{language.lower()}.html'
    )
    html = template.render(params)
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=text,
        html=html,
    )
    background_tasks.add_task(mailer.send_message, message)
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
