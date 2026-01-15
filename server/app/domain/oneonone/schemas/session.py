from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class SessionBase(BaseModel):
    topic: str
    scheduled_at: datetime
    status: str = "scheduled"

class SessionCreate(SessionBase):
    user_id: int
    manager_id: int
    company_id: int

class SessionResponse(SessionBase):
    id: int
    user_id: int
    manager_id: int
    company_id: int
    created_at: datetime
    report_data: Optional[str] = None

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    message: str
    session_id: int
    status: str

class ReportResponse(BaseModel):
    session_id: int
    report: Any # This will hold the JSON from ManagerReportResponse or MemberReportResponse
