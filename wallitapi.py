import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from api import user, transactions, categories, tags_metadata
from api.error_handlers import request_validation_handler


def create_app() -> FastAPI:
    app = FastAPI(openapi_tags=tags_metadata)

    app.include_router(user.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)
    
    app.add_exception_handler(RequestValidationError, request_validation_handler)

    return app


app = create_app()
if __name__ == "__main__":
    uvicorn.run(app)
