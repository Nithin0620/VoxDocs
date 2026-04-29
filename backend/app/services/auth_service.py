"""
Authentication service for local and Google OAuth flows.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import bcrypt
from fastapi import HTTPException, Request, Response, status
from google_auth_oauthlib.flow import Flow
from jose import JWTError, jwt
from pydantic import EmailStr

from app import config
from app.db.models import User


class AuthService:
    """Encapsulates password hashing, JWTs, and Google OAuth logic."""

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, password_hash: Optional[str]) -> bool:
        if not password_hash:
            return False
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))

    def create_access_token(self, user_id: str, email: str, provider: str) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "email": email,
            "provider": provider,
            "iat": datetime.now(timezone.utc),
            "exp": expires_at,
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
            ) from exc

    def get_client_config(self) -> Dict[str, Dict[str, str]]:
        if not config.GOOGLE_CLIENT_ID or not config.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth is not configured",
            )

        return {
            "web": {
                "client_id": config.GOOGLE_CLIENT_ID,
                "project_id": "voxdocs",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [config.GOOGLE_REDIRECT_URI],
            }
        }

    def build_google_flow(self, state: Optional[str] = None) -> Flow:
        flow = Flow.from_client_config(
            self.get_client_config(),
            scopes=config.GOOGLE_SCOPES,
            state=state,
        )
        flow.redirect_uri = config.GOOGLE_REDIRECT_URI
        return flow

    def get_google_authorization_url(self) -> Tuple[str, str]:
        flow = self.build_google_flow()
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return authorization_url, state

    async def fetch_google_user_info(self, request_url: str, state: str) -> Dict[str, Any]:
        flow = self.build_google_flow(state=state)
        flow.fetch_token(authorization_response=request_url)

        if not flow.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google authentication failed",
            )

        session = flow.authorized_session()
        response = session.get("https://www.googleapis.com/oauth2/v2/userinfo", timeout=15)
        response.raise_for_status()
        return response.json()

    async def create_or_update_google_user(self, user_info: Dict[str, Any]) -> User:
        email = str(user_info.get("email", "")).lower().strip()
        name = str(user_info.get("name") or user_info.get("given_name") or email.split("@")[0]).strip()
        profile_pic = user_info.get("picture")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account did not return an email address",
            )

        user = await User.find_one(User.email == email)
        if user:
            if profile_pic and not user.profile_pic:
                user.profile_pic = profile_pic
            if name and not user.name:
                user.name = name
            await user.save()
            return user

        user = User(
            name=name,
            email=email,
            password=None,
            provider="google",
            profile_pic=profile_pic,
            created_at=datetime.utcnow(),
        )
        await user.save()
        return user

    async def create_local_user(self, name: str, email: EmailStr, password: str) -> User:
        normalized_email = str(email).lower().strip()
        existing_user = await User.find_one(User.email == normalized_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        user = User(
            name=name.strip(),
            email=normalized_email,
            password=self.hash_password(password),
            provider="local",
            profile_pic=None,
            created_at=datetime.utcnow(),
        )
        await user.save()
        return user

    async def authenticate_local_user(self, email: EmailStr, password: str) -> User:
        normalized_email = str(email).lower().strip()
        user = await User.find_one(User.email == normalized_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if user.provider == "google" and not user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account uses Google sign-in. Continue with Google.",
            )

        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return user

    async def get_user_by_id(self, user_id: str) -> User:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        return user

    def get_token_from_request(self, request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.removeprefix("Bearer ").strip()
        return request.cookies.get(config.AUTH_COOKIE_NAME)

    async def get_current_user(self, request: Request) -> User:
        cached_user = getattr(request.state, "current_user", None)
        if cached_user is not None:
            return cached_user

        token = self.get_token_from_request(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        payload = self.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user = await self.get_user_by_id(user_id)
        request.state.current_user = user
        return user

    def set_auth_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=config.AUTH_COOKIE_NAME,
            value=token,
            httponly=True,
            secure=config.AUTH_COOKIE_SECURE,
            samesite=config.AUTH_COOKIE_SAMESITE,
            max_age=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )

    def clear_auth_cookie(self, response: Response) -> None:
        response.delete_cookie(config.AUTH_COOKIE_NAME, path="/")

    def serialize_user(self, user: User) -> Dict[str, Any]:
        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "provider": user.provider,
            "profilePic": user.profile_pic,
            "createdAt": user.created_at,
        }