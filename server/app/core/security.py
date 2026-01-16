"""
JWT 토큰 생성 및 검증 유틸리티
OAuth 인증 및 토큰 관리를 위한 보안 기능
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from jwt.exceptions import InvalidTokenError

from server.app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token을 생성합니다.

    Args:
        data: 토큰에 포함할 데이터 (user_id, email 등)
        expires_delta: 만료 시간 (기본값: 설정의 ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        str: JWT 토큰 문자열
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> tuple[str, datetime]:
    """
    JWT Refresh Token을 생성합니다.

    Args:
        data: 토큰에 포함할 데이터 (user_id만 포함하는 것이 안전)

    Returns:
        tuple[str, datetime]: (토큰 문자열, 만료 시간)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, expire


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    JWT 토큰을 검증하고 페이로드를 반환합니다.

    Args:
        token: 검증할 JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")

    Returns:
        Optional[Dict[str, Any]]: 검증 성공 시 토큰 페이로드, 실패 시 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # 토큰 타입 검증
        if payload.get("type") != token_type:
            return None

        # 만료 시간 검증 (jwt.decode가 자동으로 수행하지만 명시적으로 확인)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            return None

        return payload

    except InvalidTokenError:
        return None
    except Exception:
        return None


def decode_google_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Google OAuth ID Token을 디코딩합니다.

    주의: 프로덕션에서는 Google의 공개 키로 검증해야 합니다.
    현재는 클라이언트에서 이미 검증된 토큰을 받는다고 가정합니다.

    Args:
        token: Google ID Token

    Returns:
        Optional[Dict[str, Any]]: 디코딩된 토큰 정보
    """
    try:
        # 검증 없이 디코딩 (클라이언트에서 이미 검증됨)
        # 프로덕션에서는 google.auth.transport.requests를 사용하여 검증 필요
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception:
        return None


def get_token_expiry_time(token: str) -> Optional[datetime]:
    """
    토큰의 만료 시간을 반환합니다.

    Args:
        token: JWT 토큰

    Returns:
        Optional[datetime]: 만료 시간
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except Exception:
        return None
