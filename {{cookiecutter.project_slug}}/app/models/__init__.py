from sqlalchemy import MetaData

metadata = MetaData()

from . import user  # noqa: E402

__all__ = [
    'user',
]
