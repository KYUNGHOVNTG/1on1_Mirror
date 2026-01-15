"""
Base class for LLM-based calculators using Claude 3.5 Sonnet.
"""

import json
from typing import Type, TypeVar

from anthropic import AsyncAnthropic, APIError
from pydantic import BaseModel

from app.calculators.base import BaseCalculator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput", bound=BaseModel)


class LLMBaseCalculator(BaseCalculator[TInput, TOutput]):
    """
    Abstract base class for calculators that leverage LLM for analysis.
    
    This class handles the initialization of the Anthropic client and provides
    helper methods for generating structured insights using Claude 3.5 Sonnet.
    """
    
    def __init__(self):
        """Initialize Anthropic client with API key from settings."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY is not set. LLM features will not work.")
        
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20240620"  # Latest Sonnet as of coding
        
    async def _get_llm_insight(
        self,
        system_prompt: str,
        user_message: str,
        output_model: Type[TOutput]
    ) -> TOutput:
        """
        Generate structured insight from LLM.
        
        Uses Claude's Tool Use feature (or JSON embedding) to ensure the output
        matches the Pydantic model structure.
        
        Args:
            system_prompt: Investigated system prompt with definitions
            user_message: The content to analyze
            output_model: Pydantic model class for validation
            
        Returns:
            Validated instance of output_model
            
        Raises:
            Exception: If API call fails or parsing fails
        """
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API Key is missing")

        # Construct the tool definition from Pydantic model
        schema = output_model.model_json_schema()
        tool_name = "record_analysis_result"
        
        tool_definition = {
            "name": tool_name,
            "description": "Record the analysis result in the specified structure.",
            "input_schema": schema
        }
        
        try:
            logger.info("Calling Claude 3.5 Sonnet API for analysis")
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                tools=[tool_definition],
                tool_choice={"type": "tool", "name": tool_name}
            )
            
            # Extract tool use content
            for content in response.content:
                if content.type == "tool_use" and content.name == tool_name:
                    return output_model.model_validate(content.input)
            
            raise ValueError("LLM did not return a valid tool use response")
            
        except APIError as e:
            logger.error(f"Anthropic API Error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to process LLM response: {str(e)}")
            raise
