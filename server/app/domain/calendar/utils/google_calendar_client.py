"""
구글 캘린더 API 클라이언트

구글 캘린더 API와의 상호작용을 담당하는 유틸리티 클래스입니다.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from server.app.core.config import settings
from server.app.core.logging import get_logger

logger = get_logger(__name__)


class GoogleCalendarClient:
    """
    구글 캘린더 API 클라이언트

    구글 캘린더 API를 사용하여 이벤트를 조회하고 관리합니다.
    """

    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events.readonly",
    ]

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        token_expires_at: datetime,
    ):
        """
        Args:
            access_token: 구글 OAuth 액세스 토큰
            refresh_token: 구글 OAuth 리프레시 토큰
            token_expires_at: 토큰 만료 시간
        """
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES,
        )
        self.service = build("calendar", "v3", credentials=self.credentials)

    def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        캘린더 이벤트 목록 조회

        Args:
            calendar_id: 캘린더 ID (기본: primary)
            time_min: 조회 시작 시간 (기본: 현재 시각)
            time_max: 조회 종료 시간 (기본: 3개월 후)
            max_results: 최대 조회 개수

        Returns:
            List[Dict]: 이벤트 목록

        Raises:
            HttpError: API 호출 실패
        """
        try:
            # 기본값 설정
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = datetime.utcnow() + timedelta(days=90)

            # RFC3339 형식으로 변환
            time_min_str = time_min.isoformat() + "Z"
            time_max_str = time_max.isoformat() + "Z"

            logger.info(
                f"Fetching events from Google Calendar: {calendar_id}",
                extra={
                    "calendar_id": calendar_id,
                    "time_min": time_min_str,
                    "time_max": time_max_str,
                    "max_results": max_results,
                },
            )

            # 이벤트 조회
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min_str,
                    timeMax=time_max_str,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            logger.info(f"Fetched {len(events)} events from Google Calendar")

            return events

        except HttpError as error:
            logger.error(
                f"Failed to fetch events from Google Calendar: {error}",
                extra={"error": str(error)},
            )
            raise

    def get_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> Optional[Dict[str, Any]]:
        """
        캘린더 이벤트 단건 조회

        Args:
            event_id: 이벤트 ID
            calendar_id: 캘린더 ID (기본: primary)

        Returns:
            Optional[Dict]: 이벤트 정보

        Raises:
            HttpError: API 호출 실패
        """
        try:
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )
            return event

        except HttpError as error:
            if error.resp.status == 404:
                logger.warning(f"Event not found: {event_id}")
                return None
            logger.error(
                f"Failed to fetch event from Google Calendar: {error}",
                extra={"event_id": event_id, "error": str(error)},
            )
            raise

    def watch_events(
        self,
        calendar_id: str,
        webhook_url: str,
        channel_id: str,
    ) -> Dict[str, Any]:
        """
        캘린더 이벤트 변경 감시 (Webhook 등록)

        Args:
            calendar_id: 캘린더 ID
            webhook_url: Webhook 수신 URL
            channel_id: 채널 ID (UUID)

        Returns:
            Dict: Webhook 등록 정보 (channel_id, resource_id, expiration)

        Raises:
            HttpError: API 호출 실패
        """
        try:
            body = {
                "id": channel_id,
                "type": "web_hook",
                "address": webhook_url,
            }

            channel = (
                self.service.events()
                .watch(calendarId=calendar_id, body=body)
                .execute()
            )

            logger.info(
                f"Registered webhook for calendar: {calendar_id}",
                extra={
                    "channel_id": channel_id,
                    "resource_id": channel.get("resourceId"),
                    "expiration": channel.get("expiration"),
                },
            )

            return channel

        except HttpError as error:
            logger.error(
                f"Failed to register webhook: {error}",
                extra={"calendar_id": calendar_id, "error": str(error)},
            )
            raise

    def stop_watch(
        self,
        channel_id: str,
        resource_id: str,
    ) -> None:
        """
        캘린더 이벤트 변경 감시 중지 (Webhook 해제)

        Args:
            channel_id: 채널 ID
            resource_id: 리소스 ID

        Raises:
            HttpError: API 호출 실패
        """
        try:
            body = {
                "id": channel_id,
                "resourceId": resource_id,
            }

            self.service.channels().stop(body=body).execute()

            logger.info(
                f"Stopped webhook",
                extra={"channel_id": channel_id, "resource_id": resource_id},
            )

        except HttpError as error:
            logger.error(
                f"Failed to stop webhook: {error}",
                extra={
                    "channel_id": channel_id,
                    "resource_id": resource_id,
                    "error": str(error),
                },
            )
            raise

    @staticmethod
    def parse_event_datetime(event_time: Dict[str, Any]) -> datetime:
        """
        구글 캘린더 이벤트 시간 파싱

        Args:
            event_time: 이벤트 시간 정보 (dateTime 또는 date)

        Returns:
            datetime: 파싱된 시간
        """
        # dateTime이 있으면 사용 (시간 포함)
        if "dateTime" in event_time:
            return datetime.fromisoformat(
                event_time["dateTime"].replace("Z", "+00:00")
            )
        # date만 있으면 자정으로 설정 (종일 이벤트)
        elif "date" in event_time:
            return datetime.fromisoformat(event_time["date"] + "T00:00:00+00:00")
        else:
            raise ValueError("Invalid event time format")

    @staticmethod
    def extract_attendees(event: Dict[str, Any]) -> tuple[int, List[str]]:
        """
        이벤트에서 참석자 정보 추출

        Args:
            event: 구글 캘린더 이벤트

        Returns:
            tuple: (참석자 수, 참석자 이메일 목록)
        """
        attendees = event.get("attendees", [])
        attendees_count = len(attendees)
        attendees_emails = [attendee.get("email") for attendee in attendees if attendee.get("email")]
        return attendees_count, attendees_emails
