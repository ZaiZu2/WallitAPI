from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from api import categories, tags_metadata, transactions, user
from api.error_handlers import request_validation_handler
from config import LOGGING_CONFIG


def create_app() -> FastAPI:
    app = FastAPI(openapi_tags=tags_metadata)

    app.include_router(user.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)

    app.add_exception_handler(RequestValidationError, request_validation_handler)

    Path("./logs").mkdir(exist_ok=True)

    return app


app = create_app()
if __name__ == "__main__":
    uvicorn.run(app, log_config=LOGGING_CONFIG)
