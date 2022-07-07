from typing import Callable, Any
from fastapi import APIRouter as FastAPIRouter

from app.api.api_v1.endpoints import bets, items, login, users, utils

class APIRouter(FastAPIRouter):
    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable:
        if path.endswith("/"):
            path = path[:-1]

        add_path = super().api_route(
            path, include_in_schema=include_in_schema, **kwargs
        )

        alternate_path = path + "/"
        add_alternate_path = super().api_route(
            alternate_path, include_in_schema=False, **kwargs
        )

        def decorator(func: Callable) -> Callable:
            add_alternate_path(func)
            return add_path(func)

        return decorator

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(bets.router, prefix="/bets", tags=["bets"])
