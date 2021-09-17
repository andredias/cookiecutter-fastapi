from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from . import config
from .middlewares import dispatch
from .resources import shutdown, startup
from .routers import confirmation, login, user

routers = [
    confirmation.router,
    login.router,
    user.router,
]

origins = [
    '*',
]

app = FastAPI(
    title='{{cookiecutter.project_name}}',
    debug=config.DEBUG,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['x-csrf-token'],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=dispatch)

for router in routers:
    app.include_router(router)


@app.on_event('startup')
async def startup_event():
    await startup()


@app.on_event('shutdown')
async def shutdown_event():
    await shutdown()
