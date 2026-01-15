"""
Calculator for analyzing coaching vs directive communication styles using LLM.
"""

from pydantic import BaseModel, Field

from server.app.calculators.llm_base import LLMBaseCalculator


class CoachingStyleInput(BaseModel):
    """Input for coaching style analysis."""
    transcript: str = Field(..., description="Full conversation script to analyze")


class StyleExample(BaseModel):
    """Example sentence for a specific style."""
    text: str = Field(..., description="The quoted sentence from the transcript")
    style: str = Field(..., description="'coaching' or 'directive'")
    reason: str = Field(..., description="Why this was classified as such")


class CoachingStyleResult(BaseModel):
    """Result of coaching style analysis."""
    
    directive_score: float = Field(
        ..., 
        ge=0, le=100, 
        description="Percentage of directive communication (0-100)"
    )
    coaching_score: float = Field(
        ..., 
        ge=0, le=100, 
        description="Percentage of coaching communication (0-100)"
    )
    balance_assessment: str = Field(
        ..., 
        description="Short assessment of the balance (e.g. 'Coaching Dominant', 'Balanced', 'Directive Dominant')"
    )
    key_examples: list[StyleExample] = Field(
        default_factory=list,
        description="Key examples of each style from the conversation"
    )
    improvement_feedback: str = Field(
        ..., 
        description="Actionable feedback to improve coaching style"
    )


class CoachingStyleCalculator(LLMBaseCalculator[CoachingStyleInput, CoachingStyleResult]):
    """
    Analyzes the manager's communication style (Coaching vs Directive).
    
    Uses LLM to classify sentences and compute the balance.
    """
    
    SYSTEM_PROMPT = """
    You are an expert Executive Coach Analyzer.
    Your task is to analyze a 1-on-1 meeting transcript between a Manager and a Team Member.
    
    Focus ONLY on the Manager's speech.
    
    Classify the Manager's communication into two styles:
    1. **Directive Style**: Giving solutions, instructions, teaching, advice-giving, stating facts, controlling the agenda.
       (e.g., "You should do X", "I want you to...", "Here is the answer.")
    2. **Coaching Style**: Asking open-ended questions, active listening, reflecting back, facilitating self-discovery, empowering.
       (e.g., "What do you think?", "How would you approach this?", "What did you learn?")
    
    Analyze the 'Manager's' lines specifically.
    
    Output Requirements:
    - Estimate the percentage ratio of Directive vs Coaching (should sum to approx 100%).
    - Provide concrete examples from the text.
    - Provide constructive feedback.
    """
    
    async def calculate(self, data: CoachingStyleInput) -> CoachingStyleResult:
        """
        Analyze coaching style from transcript.
        
        Args:
            data: Input containing the transcript
            
        Returns:
            CoachingStyleResult with scores and feedback
        """
        return await self._get_llm_insight(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=f"Analyze the following transcript:\n\n{data.transcript}",
            output_model=CoachingStyleResult
        )
