from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from api import user
from api.error_handlers import request_validation_handler


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(user.router)

    app.add_exception_handler(RequestValidationError, request_validation_handler)

    return app
