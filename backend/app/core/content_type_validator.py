"""
Content-Type validation middleware.
Ensures POST/PUT requests have proper Content-Type.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request


class ContentTypeValidator(BaseHTTPMiddleware):
    """Middleware to validate Content-Type header."""

    ALLOWED_TYPES = {
        "application/json",
        "multipart/form-data",
        "application/x-www-form-urlencoded"
    }

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            base_type = content_type.split(";")[0].strip()

            if request.headers.get("content-length") == "0":
                return await call_next(request)

            if base_type and base_type not in self.ALLOWED_TYPES:
                return JSONResponse(
                    status_code=415,
                    content={
                        "type": "validation/content-type",
                        "title": "Unsupported Media Type",
                        "status": 415,
                        "detail": f"Content-Type '{base_type}' not supported. Use application/json."
                    }
                )

        return await call_next(request)
