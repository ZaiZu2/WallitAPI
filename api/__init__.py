from fastapi import FastAPI

from api import users


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(users.router)

    return app
