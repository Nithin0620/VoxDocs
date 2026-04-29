"""
JWT authentication middleware.
Attaches the authenticated user to request.state when a valid token is present.
"""
from typing import Set

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app import config
from app.services.auth_service import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    public_paths: Set[str] = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        f"{config.API_V1_PREFIX}/auth/signup",
        f"{config.API_V1_PREFIX}/auth/login",
        f"{config.API_V1_PREFIX}/auth/google",
        f"{config.API_V1_PREFIX}/auth/google/callback",
        f"{config.API_V1_PREFIX}/auth/logout",
    }

    async def dispatch(self, request: Request, call_next):
        auth_service = AuthService()
        path = request.url.path
        token = auth_service.get_token_from_request(request)

        if token:
            try:
                payload = auth_service.decode_access_token(token)
                user_id = payload.get("sub")
                if user_id:
                    request.state.current_user = await auth_service.get_user_by_id(user_id)
            except Exception:
                request.state.current_user = None

        protected_path = path.startswith(config.API_V1_PREFIX) and path not in self.public_paths
        if protected_path and getattr(request.state, "current_user", None) is None:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Authentication required"},
            )

        return await call_next(request)