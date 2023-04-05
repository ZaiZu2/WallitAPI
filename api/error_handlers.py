from fastapi import APIRouter, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

router = APIRouter()


async def request_validation_handler(
    response: Response, exc: RequestValidationError
) -> Response:
    for error in exc.errors():
        body = {error["loc"][1]: error["msg"]}

    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse(
            {"details": body},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            headers=headers,
        )
    else:
        return JSONResponse(
            {"details": body}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
