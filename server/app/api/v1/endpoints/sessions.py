from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.oneonone.service import OneOnOneService
from app.domain.oneonone.repositories.session_repository import SessionRepository
from app.domain.oneonone.repositories.goal_repository import GoalRepository
from app.formatters.report_formatter import ReportFormatter
from app.domain.oneonone.schemas.session import AnalysisResponse, ReportResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_one_on_one_service(db: AsyncSession = Depends(get_db)) -> OneOnOneService:
    session_repo = SessionRepository(db)
    goal_repo = GoalRepository(db)
    formatter = ReportFormatter()
    return OneOnOneService(session_repo, goal_repo, formatter)

@router.post("/{session_id}/analyze", response_model=AnalysisResponse)
async def analyze_session(
    session_id: int,
    file: UploadFile = File(...),
    service: OneOnOneService = Depends(get_one_on_one_service)
) -> Any:
    """
    1on1 세션 음성 파일을 업로드하고 분석을 시작합니다.
    """
    try:
        report_json = await service.analyze_audio(session_id, file)
        return {
            "message": "Analysis completed successfully",
            "session_id": session_id,
            "status": "completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {str(e)}")

@router.get("/{session_id}/report", response_model=ReportResponse)
async def get_session_report(
    session_id: int,
    service: OneOnOneService = Depends(get_one_on_one_service)
) -> Any:
    """
    저장된 1on1 분석 리포트를 조회합니다.
    """
    report = await service.get_report(session_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this session. Please analyze first."
        )
    
    return {
        "session_id": session_id,
        "report": report
    }
