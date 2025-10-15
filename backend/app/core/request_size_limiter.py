"""
Request size limiter middleware.
Prevents DoS attacks via large request bodies.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request


class RequestSizeLimiter(BaseHTTPMiddleware):
    """Middleware to limit request body size."""

    def __init__(self, app, max_size: int = 10_000_000):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > self.max_size:
                return Response(
                    content="Request body too large",
                    status_code=413,
                    headers={
                        "Content-Type": "text/plain",
                        "Retry-After": "3600"
                    }
                )

        return await call_next(request)
