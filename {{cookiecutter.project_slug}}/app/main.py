from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .resources import shutdown, startup
from .routers import login, user

routers = [
    login.router,
    user.router,
]

app = FastAPI(default_response_class=ORJSONResponse)
for router in routers:
    app.include_router(router)


@app.on_event('startup')
async def startup_event():
    await startup()


@app.on_event('shutdown')
async def shutdown_event():
    await shutdown()
