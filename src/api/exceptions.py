from typing import Any

from litestar import MediaType
from litestar import Request
from litestar import Response


class BaseResponseError(Exception):
    status_code: int
    error_message: str
    extra_meta_data: dict | None

    def __init__(self, *args: Any, extra_meta_data: dict | None = None) -> None:
        super().__init__(*args)
        self.extra_meta_data = extra_meta_data


class DynamicResponseError(BaseResponseError):
    def __init__(self, *args: Any, error_message: str, extra_meta_data: dict) -> None:
        super().__init__(*args, extra_meta_data=extra_meta_data)
        self.error_message = error_message


def response_exception_handler(_: Request, exc: BaseResponseError) -> Response:
    if not exc.extra_meta_data:
        return Response(
            content=exc.extra_meta_data,
            media_type=MediaType.TEXT,
            status_code=exc.status_code,
        )
    return Response(
        content={"error_message": exc.error_message, "details": exc.extra_meta_data},
        media_type=MediaType.JSON,
        status_code=exc.status_code,
    )
