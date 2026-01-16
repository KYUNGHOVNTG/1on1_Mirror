"""
인증 라우터

OAuth 로그인 및 토큰 관리 API 엔드포인트를 제공합니다.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.config import settings
from server.app.core.database import get_db
from server.app.core.dependencies import get_current_user
from server.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_google_token,
    verify_token,
)
from server.app.domain.auth.schemas.auth import (
    GoogleLoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserInfo,
)
from server.app.domain.company.models.company import Company
from server.app.domain.user.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def google_login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Google OAuth로 로그인합니다.

    클라이언트에서 받은 Google ID Token을 검증하고,
    사용자를 생성하거나 조회한 후 JWT 토큰을 발급합니다.

    Args:
        request: Google ID Token
        db: 데이터베이스 세션

    Returns:
        LoginResponse: 사용자 정보 및 토큰
    """
    # Google ID Token 디코딩
    google_user = decode_google_token(request.id_token)
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    # Google 사용자 정보 추출
    google_id = google_user.get("sub")
    email = google_user.get("email")
    name = google_user.get("name")
    picture = google_user.get("picture")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google user data",
        )

    # 이메일 도메인 추출
    email_domain = email.split("@")[1] if "@" in email else None
    if not email_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    # 회사 조회 (도메인으로)
    company_result = await db.execute(
        select(Company).where(Company.domain == email_domain)
    )
    company = company_result.scalar_one_or_none()

    # 회사가 없으면 생성
    if not company:
        company = Company(
            name=email_domain,
            domain=email_domain,
            is_active=True,
        )
        db.add(company)
        await db.flush()

    # 사용자 조회
    user_result = await db.execute(
        select(User).where(User.google_id == google_id)
    )
    user = user_result.scalar_one_or_none()

    # 사용자가 없으면 생성
    if not user:
        user = User(
            company_id=company.id,
            email=email,
            google_id=google_id,
            name=name or "Unknown",
            profile_image=picture,
            role="member",
        )
        db.add(user)
        await db.flush()
    else:
        # 기존 사용자 정보 업데이트
        user.name = name or user.name
        user.profile_image = picture or user.profile_image
        user.updated_at = datetime.utcnow()

    # JWT 토큰 생성
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )

    refresh_token_str, refresh_token_expires = create_refresh_token(
        data={"user_id": user.id}
    )

    # Refresh Token을 데이터베이스에 저장
    user.refresh_token = refresh_token_str
    user.refresh_token_expires_at = refresh_token_expires

    await db.commit()
    await db.refresh(user)

    # 응답 생성
    return LoginResponse(
        user=UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            profile_image=user.profile_image,
            role=user.role,
            company_id=user.company_id,
            department_id=user.department_id,
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh Token을 사용하여 새로운 Access Token을 발급합니다.

    Args:
        request: Refresh Token
        db: 데이터베이스 세션

    Returns:
        TokenResponse: 새로운 토큰 정보
    """
    # Refresh Token 검증
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 데이터베이스에서 사용자 조회
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # 저장된 Refresh Token과 비교
    if user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Refresh Token 만료 확인
    if user.refresh_token_expires_at and user.refresh_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # 새로운 Access Token 생성
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
    )

    # 새로운 Refresh Token 생성 (Refresh Token Rotation)
    refresh_token_str, refresh_token_expires = create_refresh_token(
        data={"user_id": user.id}
    )

    # 새로운 Refresh Token을 데이터베이스에 저장
    user.refresh_token = refresh_token_str
    user.refresh_token_expires_at = refresh_token_expires
    user.updated_at = datetime.utcnow()

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    로그아웃합니다.

    사용자의 Refresh Token을 데이터베이스에서 삭제합니다.

    Args:
        user: 현재 인증된 사용자
        db: 데이터베이스 세션
    """
    # Refresh Token 삭제
    user.refresh_token = None
    user.refresh_token_expires_at = None
    user.updated_at = datetime.utcnow()

    await db.commit()
