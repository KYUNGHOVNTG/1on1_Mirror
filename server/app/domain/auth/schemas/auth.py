"""
인증 관련 스키마

OAuth 로그인, 토큰 갱신 등의 요청/응답 스키마를 정의합니다.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class GoogleLoginRequest(BaseModel):
    """Google OAuth 로그인 요청"""

    id_token: str = Field(..., description="Google ID Token")

    class Config:
        json_schema_extra = {
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
            }
        }


class TokenResponse(BaseModel):
    """토큰 응답"""

    access_token: str = Field(..., description="JWT Access Token")
    refresh_token: str = Field(..., description="JWT Refresh Token")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="액세스 토큰 만료 시간 (초)")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 갱신 요청"""

    refresh_token: str = Field(..., description="Refresh Token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
            }
        }


class UserInfo(BaseModel):
    """사용자 정보"""

    id: int
    email: EmailStr
    name: str
    profile_image: Optional[str] = None
    role: str
    company_id: int
    department_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "홍길동",
                "profile_image": "https://example.com/avatar.jpg",
                "role": "member",
                "company_id": 1,
                "department_id": 1
            }
        }


class LoginResponse(BaseModel):
    """로그인 응답"""

    user: UserInfo
    tokens: TokenResponse

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "name": "홍길동",
                    "profile_image": "https://example.com/avatar.jpg",
                    "role": "member",
                    "company_id": 1,
                    "department_id": 1
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }
