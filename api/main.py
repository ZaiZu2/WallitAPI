from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/")
def main() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=status.HTTP_308_PERMANENT_REDIRECT)
