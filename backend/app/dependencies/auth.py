"""
Authentication dependencies for protected routes.
"""
from fastapi import Depends, Request

from app.services.auth_service import AuthService


def get_auth_service() -> AuthService:
    return AuthService()


async def get_current_user(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.get_current_user(request)


async def require_current_user(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.get_current_user(request)