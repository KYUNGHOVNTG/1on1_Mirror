"""
Data formatter for generating UI-optimized report data.

This module transforms raw analysis results from various calculators into
JSON structures suitable for frontend visualization libraries (e.g., Recharts).
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.calculators.coaching_style_calculator import CoachingStyleResult
from app.calculators.goal_alignment_calculator import GoalAlignmentResult
from app.calculators.safety_score_calculator import SafetyScoreResult
from app.calculators.speech_analyzer import SpeechAnalysisResult


# ====================
# Output Models (UI Schema)
# ====================

class RadarChartPoint(BaseModel):
    """Data point for Radar Chart."""
    subject: str = Field(..., description="Metric name (e.g., 'Listening')")
    A: float = Field(..., description="Score value (0-100 or normalized)")
    fullMark: int = Field(100, description="Max possible score")


class TimelinePoint(BaseModel):
    """Data point for Timeline Chart."""
    time: str = Field(..., description="Time label (e.g., '00:00')")
    value: float = Field(..., description="Value to plot")
    speaker: str = Field(..., description="Active speaker or category")


class WordCloudItem(BaseModel):
    """Data item for Word Cloud."""
    text: str = Field(..., description="Keyword text")
    value: int = Field(..., description="Frequency or weight size")


class ManagerReportResponse(BaseModel):
    """Formatted report data for Manager Dashboard (Coaching Mirror)."""
    
    # 1. Coaching Skills Radar Chart
    radar_chart: List[RadarChartPoint]
    
    # 2. Conversation Flow/Timeline
    timeline_data: List[TimelinePoint]
    
    # 3. Key Metrics Summary
    coaching_score: float = Field(..., description="Coaching style percentage")
    safety_score: int = Field(..., description="Psychological safety score")
    talk_ratio: float = Field(..., description="Manager's talk ratio (0-1)")
    
    # 4. Detailed Feedback
    feedback: str = Field(..., description="Actionable feedback for manager")


class MemberReportResponse(BaseModel):
    """Formatted report data for Member Dashboard (Growth Mirror)."""
    
    # 1. Growth Word Cloud
    word_cloud: List[WordCloudItem]
    
    # 2. Goal Alignment Status
    alignment_score: float = Field(..., description="Goal alignment score (0-1)")
    alignment_category: str = Field(..., description="High/Medium/Low")
    
    # 3. Action Items / Key Takeaways (Derived from feedback/topics)
    # Note: Dedicated Action Item Extractor might be needed in future
    action_items: List[str] = Field(default_factory=list)
    
    # 4. Meeting Summary
    meeting_duration: float
    total_turns: int


# ====================
# Formatter Logic
# ====================

class ReportFormatter:
    """
    Transforms analysis results into UI-ready data structures.
    """
    
    def format_manager_report(
        self,
        speech_result: SpeechAnalysisResult,
        style_result: CoachingStyleResult,
        safety_result: SafetyScoreResult,
        goal_result: GoalAlignmentResult
    ) -> ManagerReportResponse:
        """
        Create data for Manager's Coaching Mirror.
        """
        
        # 1. Construct Radar Chart Data (5 Core Skills)
        # Mapping logic:
        # - Listening: Based on Member's speaking ratio (ideal ~50-60%) and silence
        # - Questioning: Based on Coaching Style Score
        # - Safety: From SafetyScoreCalculator
        # - Alignment: From GoalAlignmentCalculator
        # - Balance: Based on turn-taking balance
        
        # Calculate Listening Score (Simple Heuristic)
        # Validates if manager listens enough (Member ratio > 40% is good)
        listening_raw = speech_result.member_speaking_ratio * 100
        listening_score = min(100, listening_raw * 1.5)  # Scale up slightly
        
        # Calculate Stability/Balance Score
        # Penalize if one side dominates too much (>70%)
        balance_ratio = max(speech_result.manager_speaking_ratio, speech_result.member_speaking_ratio)
        stability_score = 100 - (max(0, balance_ratio - 0.5) * 200)  # 0.5->100, 1.0->0
        stability_score = max(0, min(100, stability_score))
        
        radar_data = [
            RadarChartPoint(subject="경청(Listening)", A=int(listening_score)),
            RadarChartPoint(subject="질문(Questioning)", A=int(style_result.coaching_score)),
            RadarChartPoint(subject="심리적 안전감", A=int(safety_result.safety_score)),
            RadarChartPoint(subject="목표 정렬", A=int(goal_result.alignment_score * 100)),
            RadarChartPoint(subject="대화 균형", A=int(stability_score)),
        ]
        
        # 2. Construct Timeline Data (Placeholder using Segments if available, or simplified)
        # Since we don't have raw segments passed here (only aggregate results),
        # we'll generate a simplified view or require segments in the input.
        # For now, we return an empty list or simplified dummy if Raw Segments aren't available.
        # Ideally, SpeechAnalysisResult should carry simplified timeline info.
        timeline_data = [] 
        
        return ManagerReportResponse(
            radar_chart=radar_data,
            timeline_data=timeline_data,
            coaching_score=style_result.coaching_score,
            safety_score=safety_result.safety_score,
            talk_ratio=speech_result.manager_speaking_ratio,
            feedback=style_result.improvement_feedback
        )

    def format_member_report(
        self,
        goal_result: GoalAlignmentResult,
        speech_result: SpeechAnalysisResult,
        style_result: CoachingStyleResult
    ) -> MemberReportResponse:
        """
        Create data for Member's Growth Mirror.
        """
        
        # 1. Word Cloud
        # Combine goal keywords and matched topics
        word_cloud = []
        
        # Add conversation keywords
        for kw in goal_result.conversation_keywords[:15]:
            word_cloud.append(WordCloudItem(text=kw, value=30)) # Base weight
            
        # Highlight matched topics
        for topic in goal_result.matched_topics:
            # Check if already added
            existing = next((w for w in word_cloud if w.text == topic.keyword), None)
            if existing:
                existing.value += 50  # Boost weight
            else:
                word_cloud.append(WordCloudItem(text=topic.keyword, value=60))
                
        # Sort by value desc
        word_cloud.sort(key=lambda x: x.value, reverse=True)
        
        # 2. Action Items (Derived placeholder)
        # In a real scenario, we would have an ActionItemCalculator.
        # For now, we use missing topics as suggested focus areas.
        action_items = []
        if goal_result.missing_topics:
            for topic in goal_result.missing_topics:
                action_items.append(f"'{topic}'에 대해 더 논의해보기")
        
        if style_result.improvement_feedback:
             action_items.append("매니저와의 피드백 세션 준비하기")

        return MemberReportResponse(
            word_cloud=word_cloud[:20],  # Top 20 only
            alignment_score=goal_result.alignment_score,
            alignment_category=goal_result.alignment_category.upper(),
            action_items=action_items,
            meeting_duration=speech_result.meeting_duration,
            total_turns=speech_result.total_turns
        )
