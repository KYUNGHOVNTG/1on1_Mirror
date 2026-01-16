"""
이벤트 필터링 계산기

캘린더 이벤트가 1:1 미팅인지 판단하는 로직을 담당합니다.
"""

import re
from typing import Dict, Any, List

from server.app.core.logging import get_logger

logger = get_logger(__name__)


class EventFilterCalculator:
    """
    이벤트 필터링 계산기

    캘린더 이벤트가 1:1 미팅 조건을 만족하는지 계산합니다.
    """

    # 1:1 미팅을 나타내는 키워드 (대소문자 무시)
    ONE_ON_ONE_KEYWORDS = [
        "1on1",
        "1:1",
        "1-1",
        "one on one",
        "one-on-one",
        "원온원",
        "일대일",
        "mirror",
        "미러",
        "1대1",
    ]

    def __init__(self):
        """
        이벤트 필터링 계산기 초기화

        키워드 패턴을 미리 컴파일하여 성능을 향상시킵니다.
        """
        # 키워드 패턴 컴파일 (대소문자 무시)
        self.keyword_patterns = [
            re.compile(re.escape(keyword), re.IGNORECASE)
            for keyword in self.ONE_ON_ONE_KEYWORDS
        ]

    def is_one_on_one_event(
        self,
        summary: str,
        description: str = "",
        attendees_count: int = 0,
    ) -> bool:
        """
        이벤트가 1:1 미팅인지 판단

        Args:
            summary: 이벤트 제목
            description: 이벤트 설명
            attendees_count: 참석자 수

        Returns:
            bool: 1:1 미팅 여부
        """
        # 1. 키워드 기반 필터링
        if self._contains_one_on_one_keyword(summary, description):
            logger.debug(
                f"Event matched by keyword: {summary}",
                extra={"summary": summary},
            )
            return True

        # 2. 참석자 수 기반 필터링 (참석자 2명)
        if attendees_count == 2:
            logger.debug(
                f"Event matched by attendees count: {summary}",
                extra={"summary": summary, "attendees_count": attendees_count},
            )
            return True

        return False

    def _contains_one_on_one_keyword(
        self,
        summary: str,
        description: str = "",
    ) -> bool:
        """
        제목이나 설명에 1:1 키워드가 포함되어 있는지 확인

        Args:
            summary: 이벤트 제목
            description: 이벤트 설명

        Returns:
            bool: 키워드 포함 여부
        """
        text = f"{summary} {description}".lower()

        for pattern in self.keyword_patterns:
            if pattern.search(text):
                return True

        return False

    def filter_events(
        self,
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        이벤트 목록을 필터링

        Args:
            events: 구글 캘린더 이벤트 목록

        Returns:
            List[Dict]: 필터링된 이벤트 목록
        """
        filtered_events = []

        for event in events:
            summary = event.get("summary", "")
            description = event.get("description", "")
            attendees = event.get("attendees", [])
            attendees_count = len(attendees)

            if self.is_one_on_one_event(summary, description, attendees_count):
                filtered_events.append(event)

        logger.info(
            f"Filtered {len(filtered_events)} events out of {len(events)}",
            extra={
                "total_events": len(events),
                "filtered_events": len(filtered_events),
            },
        )

        return filtered_events

    def calculate_filter_stats(
        self,
        events: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """
        필터링 통계 계산

        Args:
            events: 구글 캘린더 이벤트 목록

        Returns:
            Dict: 필터링 통계 (total, keyword_matched, attendees_matched)
        """
        total = len(events)
        keyword_matched = 0
        attendees_matched = 0

        for event in events:
            summary = event.get("summary", "")
            description = event.get("description", "")
            attendees = event.get("attendees", [])
            attendees_count = len(attendees)

            has_keyword = self._contains_one_on_one_keyword(summary, description)
            has_two_attendees = attendees_count == 2

            if has_keyword:
                keyword_matched += 1
            if has_two_attendees:
                attendees_matched += 1

        return {
            "total": total,
            "keyword_matched": keyword_matched,
            "attendees_matched": attendees_matched,
            "filtered": keyword_matched + attendees_matched,
        }
