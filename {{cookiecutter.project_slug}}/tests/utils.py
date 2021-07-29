from httpx import AsyncClient, Cookies, Headers

from app.sessions import create_csrf, create_session  # isort:skip


async def logged_session(client: AsyncClient, user_id: int = None) -> None:
    cookies = Cookies()
    headers = Headers()
    if user_id:
        prefix = f'user:{user_id}'
        session_id = await create_session(prefix)
        cookies.set('session_id', session_id)
        headers['content-type'] = 'application/json'
        headers['x-csrf-token'] = create_csrf(session_id)
    client.cookies = cookies
    client.headers = headers
    return
