"""
캘린더 라우터

캘린더 연동 및 이벤트 관리 API 엔드포인트를 제공합니다.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.core.dependencies import get_current_user
from server.app.domain.user.models.user import User
from server.app.domain.calendar.service import CalendarService
from server.app.domain.calendar.schemas.calendar import (
    CalendarConnectionCreate,
    CalendarConnectionResponse,
    CalendarEventResponse,
    CalendarEventListResponse,
    CalendarSyncRequest,
    CalendarSyncResponse,
    EventSelectionRequest,
    EventSelectionResponse,
)
from server.app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.post(
    "/connect",
    response_model=CalendarConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def connect_calendar(
    request: CalendarConnectionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarConnectionResponse:
    """
    구글 캘린더 연동 생성

    Args:
        request: 캘린더 연동 요청
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        CalendarConnectionResponse: 생성된 캘린더 연동 정보
    """
    try:
        service = CalendarService(db)
        return await service.create_connection(
            user_id=user.id,
            authorization_code=request.authorization_code,
            redirect_uri=request.redirect_uri,
        )
    except Exception as e:
        logger.error(f"Failed to connect calendar: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect calendar: {str(e)}",
        )


@router.get(
    "/connection",
    response_model=CalendarConnectionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_calendar_connection(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarConnectionResponse:
    """
    캘린더 연동 상태 조회

    Args:
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        CalendarConnectionResponse: 캘린더 연동 정보

    Raises:
        HTTPException: 연동 정보가 없는 경우 404 에러
    """
    try:
        logger.info(f"Checking calendar connection for user_id={user.id}")
        service = CalendarService(db)
        connection = await service.get_connection(user_id=user.id)
        logger.info(f"Connection found for user_id={user.id}: {connection.id if connection else 'None'}")
        return connection
    except ValueError as e:
        logger.error(f"Calendar connection not found: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get calendar connection: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get calendar connection: {str(e)}",
        )


@router.delete(
    "/connection",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_calendar_connection(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    캘린더 연동 해제

    Args:
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Raises:
        HTTPException: 연동 정보가 없는 경우 404 에러
    """
    try:
        service = CalendarService(db)
        await service.delete_connection(user_id=user.id)
    except ValueError as e:
        logger.error(f"Calendar connection not found: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to delete calendar connection: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete calendar connection: {str(e)}",
        )


@router.post(
    "/sync",
    response_model=CalendarSyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_calendar_events(
    request: CalendarSyncRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarSyncResponse:
    """
    캘린더 이벤트 동기화

    Args:
        request: 동기화 요청
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        CalendarSyncResponse: 동기화 결과
    """
    try:
        service = CalendarService(db)
        return await service.sync_events(
            user_id=user.id,
            time_min=request.time_min,
            time_max=request.time_max,
            max_results=request.max_results,
        )
    except ValueError as e:
        logger.error(f"Calendar sync failed: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to sync calendar: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync calendar: {str(e)}",
        )


@router.get(
    "/events",
    response_model=CalendarEventListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_calendar_events(
    is_filtered: Optional[bool] = None,
    is_selected: Optional[bool] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarEventListResponse:
    """
    캘린더 이벤트 목록 조회

    Args:
        is_filtered: 필터링 여부
        is_selected: 선택 여부
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        CalendarEventListResponse: 이벤트 목록
    """
    try:
        service = CalendarService(db)
        return await service.list_events(
            user_id=user.id,
            is_filtered=is_filtered,
            is_selected=is_selected,
        )
    except ValueError as e:
        logger.error(f"Failed to list events: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to list calendar events: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list calendar events: {str(e)}",
        )


@router.get(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_200_OK,
)
async def get_calendar_event(
    event_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarEventResponse:
    """
    캘린더 이벤트 단건 조회

    Args:
        event_id: 이벤트 ID
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        CalendarEventResponse: 이벤트 상세 정보

    Raises:
        HTTPException: 이벤트를 찾을 수 없는 경우 404 에러
    """
    try:
        service = CalendarService(db)
        return await service.get_event(user_id=user.id, event_id=event_id)
    except ValueError as e:
        logger.error(f"Failed to get event: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to get calendar event: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get calendar event: {str(e)}",
        )


@router.post(
    "/events/select",
    response_model=EventSelectionResponse,
    status_code=status.HTTP_200_OK,
)
async def select_calendar_events(
    request: EventSelectionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventSelectionResponse:
    """
    캘린더 이벤트 선택

    Args:
        request: 이벤트 선택 요청
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        EventSelectionResponse: 선택 결과
    """
    try:
        service = CalendarService(db)
        return await service.select_events(
            user_id=user.id,
            event_ids=request.event_ids,
        )
    except Exception as e:
        logger.error(f"Failed to select events: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to select events: {str(e)}",
        )


@router.post(
    "/events/deselect",
    response_model=EventSelectionResponse,
    status_code=status.HTTP_200_OK,
)
async def deselect_calendar_events(
    request: EventSelectionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventSelectionResponse:
    """
    캘린더 이벤트 선택 해제

    Args:
        request: 이벤트 선택 해제 요청
        user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        EventSelectionResponse: 선택 해제 결과
    """
    try:
        service = CalendarService(db)
        return await service.deselect_events(
            user_id=user.id,
            event_ids=request.event_ids,
        )
    except Exception as e:
        logger.error(f"Failed to deselect events: {e}", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to deselect events: {str(e)}",
        )


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
)
async def calendar_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    구글 캘린더 Webhook 수신

    Args:
        request: FastAPI Request
        db: 데이터베이스 세션

    Returns:
        dict: 성공 응답
    """
    # Webhook 헤더 검증
    channel_id = request.headers.get("X-Goog-Channel-ID")
    resource_id = request.headers.get("X-Goog-Resource-ID")
    resource_state = request.headers.get("X-Goog-Resource-State")

    logger.info(
        f"Received calendar webhook: channel_id={channel_id}, "
        f"resource_id={resource_id}, state={resource_state}"
    )

    # TODO: Webhook 처리 로직 구현
    # - channel_id로 캘린더 연동 조회
    # - 이벤트 재동기화
    # - 알림 전송 등

    return {"status": "ok"}
