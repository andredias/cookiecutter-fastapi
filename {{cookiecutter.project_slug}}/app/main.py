from fastapi import FastAPI

from .resources import shutdown, startup
from .routers import user

routers = [
    user.router,
]


app = FastAPI()

for router in routers:
    app.include_router(router)


@app.on_event('startup')
async def startup_event():
    await startup()


@app.on_event('shutdown')
async def shutdown_event():
    await shutdown()
