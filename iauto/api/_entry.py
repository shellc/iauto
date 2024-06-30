from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Mount

from ._api import api


@asynccontextmanager
async def lifespan(app: Starlette):
    try:
        ...
    finally:
        yield

# Routes
routes = [
    Mount(
        '/api',
        name='api',
        app=api
    ),
]

entry = Starlette(debug=False, routes=routes, lifespan=lifespan)
