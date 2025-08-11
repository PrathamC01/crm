from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import HTTPException as FastAPIHTTPException
import traceback


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except (FastAPIHTTPException, StarletteHTTPException) as http_exc:
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "status": False,
                    "message": (
                        http_exc.detail if hasattr(http_exc, "detail") else "HTTP Error"
                    ),
                    "data": None,
                    "error": str(http_exc),
                },
            )

        except Exception as e:
            # Log traceback (optional for debugging)
            traceback.print_exc()

            return JSONResponse(
                status_code=500,
                content={
                    "status": False,
                    "message": "Internal server error",
                    "data": None,
                    "error": str(e),
                },
            )
