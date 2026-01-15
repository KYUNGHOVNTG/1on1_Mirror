"""
Calculator for analyzing Psychological Safety score using LLM.
"""

from pydantic import BaseModel, Field

from app.calculators.llm_base import LLMBaseCalculator


class SafetyScoreInput(BaseModel):
    """Input for safety score analysis."""
    transcript: str = Field(..., description="Full conversation script to analyze")


class SafetyIndicator(BaseModel):
    """An indicator of psychological safety (positive or negative)."""
    category: str = Field(..., description="Category (e.g., 'Empathy', 'Blame', 'Listening')")
    description: str = Field(..., description="Description of the observation")
    quote: str | None = Field(None, description="Relevant quote from transcript if applicable")
    impact: str = Field(..., description="How this impacts safety (Positive/Negative)")


class SafetyScoreResult(BaseModel):
    """Result of psychological safety analysis."""
    
    safety_score: int = Field(
        ..., 
        ge=0, le=100, 
        description="Psychological Safety Score (0-100)"
    )
    score_rationale: str = Field(
        ..., 
        description="Explanation of why this score was given"
    )
    positive_factors: list[SafetyIndicator] = Field(
        default_factory=list,
        description="Factors that enhanced safety"
    )
    risk_factors: list[SafetyIndicator] = Field(
        default_factory=list,
        description="Factors that diminished safety"
    )
    manager_behavior_analysis: str = Field(
        ..., 
        description="Specific analysis of manager's behavior regarding safety"
    )


class SafetyScoreCalculator(LLMBaseCalculator[SafetyScoreInput, SafetyScoreResult]):
    """
    Analyzes Psychological Safety in the conversation.
    
    Based on Amy Edmondson's definition: "A shared belief that the team is safe for interpersonal risk taking."
    """
    
    SYSTEM_PROMPT = """
    You are an expert in Organizational Psychology, specifically focusing on **Psychological Safety**.
    
    Your task is to analyze a 1-on-1 meeting transcript and assess the level of psychological safety present.
    
    **Definition of Psychological Safety (Amy Edmondson):**
    "A belief that one will not be punished or humiliated for speaking up with ideas, questions, concerns, or mistakes."
    
    **Analysis Framework:**
    
    1. **Psychological Safety Enhancers (+):**
       - **Curiosity:** Asking genuine questions to understand.
       - **Vulnerability:** Admitting mistakes or "I don't know".
       - **Active Listening:** Validating feelings, paraphrasing.
       - **Empathy:** Acknowledging emotions.
       - **Feedback Solicitation:** Asking for feedback.
       
    2. **Psychological Safety Inhibitors (-):**
       - **Blame/Judgment:** Focusing on "Who did it?" rather than "What happened?".
       - **Dismissiveness:** Ignoring or minimizing concerns.
       - **Interruption:** Cutting off the other person.
       - **Defensiveness:** Reacting negatively to feedback.
       - **Fear Instillation:** Threats or aggressive tone (textual evidence).
       
    Assess the interaction dynamics between the Manager and Member.
    Assign a score 0-100 (where 100 is perfectly safe).
    """
    
    async def calculate(self, data: SafetyScoreInput) -> SafetyScoreResult:
        """
        Calculate psychological safety score.
        
        Args:
            data: Input containing the transcript
            
        Returns:
            SafetyScoreResult with analysis
        """
        return await self._get_llm_insight(
            system_prompt=self.SYSTEM_PROMPT,
            user_message=f"Analyze the psychological safety of this interaction:\n\n{data.transcript}",
            output_model=SafetyScoreResult
        )
