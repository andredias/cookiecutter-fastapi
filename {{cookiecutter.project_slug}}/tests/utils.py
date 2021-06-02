from httpx import AsyncClient, Cookies, Headers

from app.sessions import create_csrf, create_session  # isort:skip


async def logged_session(client: AsyncClient, user_id: int = None) -> None:
    cookies = Cookies()
    headers = Headers()
    if user_id:
        session_id = await create_session(dict(id=user_id))
        csrf_token = create_csrf(session_id)
        cookies.set('session_id', session_id)
        headers['x-csrf-token'] = csrf_token
    client.cookies = cookies
    client.headers = headers
    return
