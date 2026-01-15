"""
Base calculator abstract class for all analysis calculators.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


# Type variables for input and output types
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput", bound=BaseModel)


class BaseCalculator(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for all calculators in the 1on1 Mirror system.
    
    Each calculator implements the calculate method to transform input data
    into structured insights using Pydantic models for type safety.
    
    Type Parameters:
        TInput: The type of input data the calculator processes
        TOutput: The Pydantic model type for the calculation result
    
    Example:
        ```python
        class MyCalculator(BaseCalculator[dict, MyResultModel]):
            async def calculate(self, data: dict) -> MyResultModel:
                # Process data and return MyResultModel instance
                return MyResultModel(...)
        ```
    """
    
    @abstractmethod
    async def calculate(self, data: TInput) -> TOutput:
        """
        Perform the calculation on the provided input data.
        
        Args:
            data: The input data to analyze
            
        Returns:
            A Pydantic model containing the calculation results
            
        Raises:
            ValueError: If the input data is invalid or missing required fields
        """
        pass
    
    def validate_input(self, data: TInput) -> None:
        """
        Optional validation hook for input data.
        Override this method to add custom validation logic.
        
        Args:
            data: The input data to validate
            
        Raises:
            ValueError: If validation fails
        """
        pass
