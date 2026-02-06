from .videos import router as videos_router
from .fragments import router as fragments_router
from .tags import router as tags_router
from .auth import router as auth_router

__all__ = ['videos_router', 'fragments_router', 'tags_router', 'auth_router']
