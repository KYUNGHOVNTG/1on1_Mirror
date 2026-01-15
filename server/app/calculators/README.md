# Calculator Module Documentation

## 개요

`app/calculators/` 모듈은 1on1 Mirror 시스템의 핵심 분석 엔진을 제공합니다. 이 모듈은 순수한 데이터 변환 로직을 담당하며, 데이터베이스 접근 없이 입력 데이터를 분석하여 인사이트를 생성합니다.

## 아키텍처 원칙

### 1. **순수 함수형 설계**
- Calculator는 DB나 외부 API에 접근하지 않습니다
- 입력 데이터 → 계산 로직 → 결과 반환의 단순한 흐름
- Side Effect가 없어 테스트와 재사용이 용이합니다

### 2. **타입 안전성**
- Python 3.12의 `Generic`과 `TypeVar` 활용
- 모든 입력/출력은 Pydantic 모델로 정의
- 명시적인 타입 힌트로 IDE 지원 최적화

### 3. **비동기 패턴**
- 모든 `calculate()` 메서드는 비동기로 구현
- 향후 병렬 처리 및 확장성 확보

## 파일 구조

```
app/calculators/
├── __init__.py                        # 모듈 내보내기
├── base.py                            # BaseCalculator 추상 클래스
├── speech_analyzer.py                 # 발화 패턴 분석 Calculator
├── goal_alignment_calculator.py       # 목표 정렬도 분석 Calculator
└── test_calculators.py                # 통합 테스트 스크립트
```

## 주요 컴포넌트

### 1. BaseCalculator (base.py)

모든 Calculator의 추상 기반 클래스입니다.

```python
from app.calculators.base import BaseCalculator
from pydantic import BaseModel

class MyResultModel(BaseModel):
    score: float
    details: str

class MyCalculator(BaseCalculator[dict, MyResultModel]):
    async def calculate(self, data: dict) -> MyResultModel:
        # 계산 로직 구현
        return MyResultModel(score=0.95, details="분석 완료")
```

**주요 기능:**
- 제네릭 타입 파라미터 `TInput`, `TOutput`
- 추상 메서드 `calculate()` 정의
- 선택적 `validate_input()` 훅 제공

### 2. SpeechAnalyzer (speech_analyzer.py)

Whisper 전사 데이터를 분석하여 대화 패턴 인사이트를 생성합니다.

**입력 모델:**
```python
WhisperTranscription(
    segments=[
        SpeechSegment(
            speaker="manager",
            text="안녕하세요",
            start_time=0.0,
            end_time=2.5
        ),
        ...
    ],
    manager_identifier="manager",
    member_identifier="member",
    total_duration=120.0  # optional
)
```

**출력 모델:**
```python
SpeechAnalysisResult(
    manager_speaking_time=45.2,      # 조직장 발화 시간 (초)
    member_speaking_time=52.8,       # 팀원 발화 시간 (초)
    total_speaking_time=98.0,        # 총 발화 시간
    total_silence_time=22.0,         # 침묵 시간
    silence_percentage=18.3,         # 침묵 비율 (%)
    manager_speaking_ratio=0.46,     # 조직장 발화 점유율 (0-1)
    member_speaking_ratio=0.54,      # 팀원 발화 점유율 (0-1)
    manager_turn_count=15,           # 조직장 발언 횟수
    member_turn_count=18,            # 팀원 발언 횟수
    total_turns=33,                  # 총 발언 횟수
    manager_avg_segment_duration=3.0,
    member_avg_segment_duration=2.9,
    meeting_duration=120.0
)
```

**분석 메트릭:**
- ⏱️ **발화 시간**: 조직장 vs 팀원 발화 시간 및 비율
- 🔇 **침묵 분석**: 세그먼트 간 침묵 시간 계산
- 🔄 **턴테이킹**: 발언 횟수 및 평균 발언 길이
- ⚖️ **대화 균형**: 발화 점유율 분석

### 3. GoalAlignmentCalculator (goal_alignment_calculator.py)

팀원의 목표와 대화 내용 간의 주제 정렬도를 분석합니다.

**입력 모델:**
```python
GoalAlignmentInput(
    goal_text="Q2 목표: AI 기능 개발 및 성능 최적화...",
    conversation_transcript="Manager: 이번 주 업무는...",
    language="ko"
)
```

**출력 모델:**
```python
GoalAlignmentResult(
    alignment_score=0.67,            # 전체 정렬 점수 (0-1)
    matched_topics=[                 # 매칭된 주제들
        TopicMatch(
            keyword="성능",
            goal_frequency=2,
            conversation_frequency=3,
            relevance_score=0.85
        ),
        ...
    ],
    matched_topic_count=8,           # 매칭된 주제 개수
    goal_keywords=["ai", "성능", ...],
    conversation_keywords=["개발", "성능", ...],
    goal_coverage=0.72,              # 목표 키워드 커버리지
    is_aligned=True,                 # 정렬 여부 (threshold: 0.3)
    alignment_category="high",       # "high", "medium", "low", "none"
    missing_topics=["최적화", "리팩토링"]
)
```

**분석 알고리즘:**
1. **키워드 추출**: 양쪽 텍스트에서 중요 키워드 추출 (불용어 제거)
2. **주제 매칭**: 공통 키워드 찾기 및 빈도 계산
3. **관련성 점수**: 위치 + 빈도 기반 relevance score 계산
4. **정렬도 계산**: Quality (60%) + Coverage (40%) 가중평균
5. **누락 주제**: 목표에는 있지만 대화에서 빠진 주제 식별

**카테고리 기준:**
- `high`: ≥ 0.7
- `medium`: 0.4 ~ 0.69
- `low`: 0.15 ~ 0.39
- `none`: < 0.15

## 사용 예제

### 1. 서비스 계층에서 Calculator 사용

```python
from app.calculators import SpeechAnalyzer, GoalAlignmentCalculator

class OneOnOneService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.speech_analyzer = SpeechAnalyzer()
        self.goal_calculator = GoalAlignmentCalculator()
    
    async def analyze_meeting(self, meeting_id: int) -> MeetingInsights:
        # 1. Repository에서 데이터 조회
        whisper_data = await self.repo.get_transcription(meeting_id)
        goal_data = await self.repo.get_goal_and_transcript(meeting_id)
        
        # 2. Calculator로 분석 (순수 계산만 수행)
        speech_result = await self.speech_analyzer.calculate(whisper_data)
        goal_result = await self.goal_calculator.calculate(goal_data)
        
        # 3. Formatter로 응답 변환
        return self.formatter.format_insights(speech_result, goal_result)
```

### 2. 독립적인 테스트/디버깅

```python
# test_calculators.py에서 직접 실행 가능
python app/calculators/test_calculators.py
```

## 테스트 실행

```bash
# PowerShell (Windows)
cd server
$env:PYTHONPATH="e:\1on1_Mirror-1\server"
python app/calculators/test_calculators.py

# Bash (Linux/Mac)
cd server
PYTHONPATH=./server python app/calculators/test_calculators.py
```

**출력 예시:**
```
============================================================
🧪 Running Calculator Tests
============================================================

============================================================
Testing Speech Analyzer
============================================================

📊 Speaking Time Analysis:
  - Manager speaking time: 9.00s
  - Member speaking time: 11.20s
  ...

✅ All tests completed successfully!
```

## .cursorrules 준수 사항

이 모듈은 프로젝트의 `.cursorrules`를 엄격히 준수합니다:

### ✅ 준수 항목:

1. **클래스 기반 설계**
   - 모든 Calculator는 `BaseCalculator` 상속
   - 절차지향 함수 대신 클래스 메서드 사용

2. **타입 안전성**
   - 모든 함수에 타입 힌트 명시
   - Pydantic으로 Request/Response DTO 정의
   - Generic 타입 파라미터 활용

3. **레이어 책임 준수**
   - Calculator는 **순수 계산 로직만** 담당
   - DB 접근 금지 (Repository로 위임)
   - Side Effect 절대 금지

4. **코드 스타일**
   - Import 순서: 표준 라이브러리 → 외부 라이브러리 → 내부 모듈
   - 명명 규칙: `PascalCase` (클래스), `snake_case` (함수/변수)
   - Docstring: Google 스타일 문서화

5. **예외 처리**
   - 명확한 `ValueError` 메시지
   - 입력 검증 로직 (`validate_input()`)

## 향후 확장 계획

### 1. 추가 Calculator 예시

```python
# sentiment_analyzer.py
class SentimentAnalyzer(BaseCalculator[ConversationInput, SentimentResult]):
    """대화 감정 분석"""
    pass

# productivity_calculator.py
class ProductivityCalculator(BaseCalculator[MeetingData, ProductivityScore]):
    """회의 생산성 점수 계산"""
    pass
```

### 2. 고급 분석 기법

- NLP 모델 통합 (transformers, spaCy)
- 감정 분석 (Sentiment Analysis)
- 주제 모델링 (Topic Modeling)
- 의도 분류 (Intent Classification)

### 3. 성능 최적화

- 병렬 처리 (`asyncio.gather()`)
- 캐싱 전략
- 대용량 텍스트 처리

## 문의 및 기여

이 모듈에 대한 문의사항이나 개선 제안은 프로젝트 관리자에게 연락하시기 바랍니다.

---

**Last Updated:** 2026-01-15  
**Version:** 1.0.0  
**Author:** 1on1 Mirror Development Team
