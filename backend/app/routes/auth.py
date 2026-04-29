"""
Authentication routes for local login/signup and Google OAuth.
"""
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app import config
from app.dependencies.auth import get_auth_service, get_current_user
from app.models.auth_models import (
    AuthResponse,
    AuthUserResponse,
    LoginRequest,
    LogoutResponse,
    MeResponse,
    SignupRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _serialize_user(user) -> AuthUserResponse:
    return AuthUserResponse(**AuthService().serialize_user(user))


def _build_auth_response(user, message: str) -> AuthResponse:
    return AuthResponse(
        success=True,
        message=message,
        user=_serialize_user(user),
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(
    payload: SignupRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    user = await auth_service.create_local_user(payload.name, payload.email, payload.password)
    token = auth_service.create_access_token(str(user.id), user.email, user.provider)
    auth_service.set_auth_cookie(response, token)
    return _build_auth_response(user, "Account created successfully")


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    user = await auth_service.authenticate_local_user(payload.email, payload.password)
    token = auth_service.create_access_token(str(user.id), user.email, user.provider)
    auth_service.set_auth_cookie(response, token)
    return _build_auth_response(user, "Login successful")


@router.get("/google")
async def google_login(auth_service: AuthService = Depends(get_auth_service)):
    authorization_url, state = auth_service.get_google_authorization_url()
    response = RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=config.GOOGLE_OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        secure=config.AUTH_COOKIE_SECURE,
        samesite=config.AUTH_COOKIE_SAMESITE,
        max_age=600,
        path="/",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    error = request.query_params.get("error")
    if error:
        redirect_url = f"{config.FRONTEND_URL}/login?error={quote(error)}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    state = request.query_params.get("state")
    stored_state = request.cookies.get(config.GOOGLE_OAUTH_STATE_COOKIE)
    if not state or not stored_state or state != stored_state:
        redirect_url = f"{config.FRONTEND_URL}/login?error={quote('Google sign-in could not be verified')}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    try:
        user_info = await auth_service.fetch_google_user_info(str(request.url), state)
        user = await auth_service.create_or_update_google_user(user_info)
        token = auth_service.create_access_token(str(user.id), user.email, user.provider)

        redirect_response = RedirectResponse(
            url=f"{config.FRONTEND_URL}/auth/callback?status=success",
            status_code=status.HTTP_302_FOUND,
        )
        auth_service.set_auth_cookie(redirect_response, token)
        redirect_response.delete_cookie(config.GOOGLE_OAUTH_STATE_COOKIE, path="/")
        return redirect_response
    except HTTPException as exc:
        redirect_url = f"{config.FRONTEND_URL}/login?error={quote(str(exc.detail))}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/me", response_model=MeResponse)
async def me(current_user=Depends(get_current_user)) -> MeResponse:
    return MeResponse(success=True, user=_serialize_user(current_user))


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response, auth_service: AuthService = Depends(get_auth_service)) -> LogoutResponse:
    auth_service.clear_auth_cookie(response)
    response.delete_cookie(config.GOOGLE_OAUTH_STATE_COOKIE, path="/")
    return LogoutResponse(success=True, message="Logged out successfully")