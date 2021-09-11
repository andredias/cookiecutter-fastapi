from fastapi import Request, Response

from .config import TESTING
from .resources import db


async def _dispatch(request: Request, call_next) -> Response:
    """
    Wraps all routes within a DB transaction
    """
    async with db.connection() as conn:  # uses the current connection
        transaction = await conn.transaction(force_rollback=TESTING)
        try:
            response = await call_next(request)
            if response.status_code < 500:
                await transaction.commit()
            else:
                await transaction.rollback()
            return response
        except Exception:
            await transaction.rollback()
            raise


async def dispatch(request: Request, call_next) -> Response:
    """
    The way BaseHTTPMiddleware works, using self.dispatch_func indirection,
    makes it very difficult to mock this function,
    but it is possible to include another indirection and mock _dispatch instead.
    """
    return await _dispatch(request, call_next)
