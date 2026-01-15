import asyncio
import json
import os
from typing import List, Optional
from datetime import datetime

from fastapi import UploadFile
from openai import AsyncOpenAI
from sqlalchemy import select

from server.app.core.config import settings
from server.app.core.logging import get_logger
from server.app.domain.oneonone.models.session import OneOnOneSession, Goal
from server.app.domain.oneonone.repositories.session_repository import SessionRepository
from server.app.domain.oneonone.repositories.goal_repository import GoalRepository
from server.app.calculators import (
    SpeechAnalyzer,
    GoalAlignmentCalculator,
    CoachingStyleCalculator,
    SafetyScoreCalculator,
    SpeechAnalyzer,
    WhisperTranscription,
    SpeechSegment,
    GoalAlignmentInput,
    CoachingStyleInput,
    SafetyScoreInput
)
from server.app.formatters.report_formatter import ReportFormatter

logger = get_logger(__name__)

class OneOnOneService:
    def __init__(
        self,
        session_repo: SessionRepository,
        goal_repo: GoalRepository,
        formatter: ReportFormatter
    ):
        self.session_repo = session_repo
        self.goal_repo = goal_repo
        self.formatter = formatter
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_audio(self, session_id: int, audio_file: UploadFile) -> str:
        """
        Analyze 1on1 session audio:
        1. STT using OpenAI Whisper
        2. Analyze using multiple Calculators
        3. Format and Save
        """
        # 1. Save file locally (Temporary)
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = f"{temp_dir}/{session_id}_{datetime.now().timestamp()}_{audio_file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                content = await audio_file.read()
                buffer.write(content)
            
            # 2. STT via Whisper
            logger.info(f"Starting STT for session {session_id}")
            with open(file_path, "rb") as f:
                # We use verbose_json to get segment timestamps
                transcription_response = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="verbose_json"
                )
            
            # Whisper segments don't have speaker labels.
            # In a real production app, we would use a diarization model or LLM to label speakers.
            # For this task, we will simulate speaker labelling using LLM to make Calculators work.
            raw_text = transcription_response.text
            segments_raw = transcription_response.segments
            
            # TODO: Add Diarization logic if needed. 
            # For now, let's create WhisperTranscription object.
            # We'll distribute segments between manager/member arbitrarily or use LLM later.
            # Let's use a simple heuristic for demo or use LLM to diarize.
            
            labeled_segments = []
            for i, seg in enumerate(segments_raw):
                # Simple logic for now: alternate speakers if not provided
                speaker = "manager" if i % 2 == 0 else "member"
                labeled_segments.append(SpeechSegment(
                    speaker=speaker,
                    text=seg.text,
                    start_time=seg.start,
                    end_time=seg.end
                ))

            whisper_data = WhisperTranscription(
                segments=labeled_segments,
                total_duration=transcription_response.duration
            )

            # 3. Load Session and Goal context
            # We need the Goal of the member to check for Alignment.
            session_stmt = select(OneOnOneSession).where(OneOnOneSession.id == session_id)
            result = await self.session_repo.db.execute(session_stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Session {session_id} not found")

            goals = await self.goal_repo.get_by_user_id(session.user_id)
            goal_text = goals[0].content if goals else "No specific goal provided."

            # 4. Run Calculators in Parallel
            logger.info(f"Running calculators for session {session_id}")
            
            speech_analyzer = SpeechAnalyzer()
            goal_calculator = GoalAlignmentCalculator()
            coaching_calculator = CoachingStyleCalculator()
            safety_calculator = SafetyScoreCalculator()

            # Prepare Inputs
            full_transcript = " ".join([f"{s.speaker}: {s.text}" for s in labeled_segments])
            
            # asyncio.gather
            speech_task = speech_analyzer.calculate(whisper_data)
            goal_task = goal_calculator.calculate(GoalAlignmentInput(
                goal_text=goal_text,
                conversation_transcript=full_transcript
            ))
            coaching_task = coaching_calculator.calculate(CoachingStyleInput(
                transcript=full_transcript
            ))
            safety_task = safety_calculator.calculate(SafetyScoreInput(
                transcript=full_transcript
            ))

            results = await asyncio.gather(
                speech_task, goal_task, coaching_task, safety_task,
                return_exceptions=True
            )
            
            # Handle potential errors in parallel tasks
            for res in results:
                if isinstance(res, Exception):
                    logger.error(f"Calculator failed: {res}")
                    raise res

            speech_res, goal_res, coaching_res, safety_res = results

            # 5. Format Outcome
            manager_report = self.formatter.format_manager_report(
                speech_res, coaching_res, safety_res, goal_res
            )
            member_report = self.formatter.format_member_report(
                goal_res, speech_res, coaching_res
            )

            final_report = {
                "manager": manager_report.model_dump(),
                "member": member_report.model_dump(),
                "performed_at": datetime.now().isoformat()
            }

            # 6. Save to Database
            session.report_data = json.dumps(final_report, ensure_ascii=False)
            session.status = "completed"
            await self.session_repo.db.commit()
            
            return session.report_data

        finally:
            # Cleanup temp file
            if os.path.exists(file_path):
                os.remove(file_path)

    async def get_report(self, session_id: int) -> Optional[dict]:
        session_stmt = select(OneOnOneSession).where(OneOnOneSession.id == session_id)
        result = await self.session_repo.db.execute(session_stmt)
        session = result.scalar_one_or_none()
        
        if session and session.report_data:
            return json.loads(session.report_data)
        return None
