from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Learner email address")
    password: Optional[str] = Field(None, description="Learner password")


class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = Field(None, description="Google OpenID Connect ID token from Google Identity Services")
    code: Optional[str] = Field(None, description="Google OAuth2 authorization code")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI if exchanging authorization code")


class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    message: str = "Authentication successful"
    is_new_user: bool = False
    needs_onboarding: bool = False


class LogoutResponse(BaseModel):
    success: bool = True
    message: str = "Logged out successfully"


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: Optional[str] = None
    experience_level: Optional[str] = "Intermediate"
    target_role_id: Optional[int] = None
    weekly_learning_hours: Optional[int] = 10
    learning_goal: Optional[str] = None
