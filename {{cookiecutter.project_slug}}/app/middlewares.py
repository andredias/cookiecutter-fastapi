from fastapi import Request, Response

from .resources import db


async def _dispatch(request: Request, call_next) -> Response:
    """
    Wraps all routes within a DB transaction
    """
    async with db.connection() as conn:  # uses the current connection
        async with conn.transaction():
            return await call_next(request)


async def dispatch(request: Request, call_next) -> Response:
    """
    The way BaseHTTPMiddleware works, using self.dispatch_func indirection,
    makes it very difficult to mock this function,
    but it is possible to include another indirection and mock that one instead.
    """
    return await _dispatch(request, call_next)
