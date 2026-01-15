"""
Goal alignment calculator for analyzing topic similarity between goals and conversation.
"""

import re
from collections import Counter

from pydantic import BaseModel, Field

from app.calculators.base import BaseCalculator


class GoalAlignmentInput(BaseModel):
    """Input model for goal alignment analysis."""
    
    goal_text: str = Field(
        ...,
        description="The team member's goal text"
    )
    conversation_transcript: str = Field(
        ...,
        description="The full conversation transcript from the meeting"
    )
    language: str = Field(
        default="ko",
        description="Language code for text processing (ko, en, etc.)"
    )


class TopicMatch(BaseModel):
    """A matched topic/keyword between goal and conversation."""
    
    keyword: str = Field(..., description="The matched keyword")
    goal_frequency: int = Field(..., description="Frequency in goal text")
    conversation_frequency: int = Field(..., description="Frequency in conversation")
    relevance_score: float = Field(
        ...,
        description="Relevance score (0-1) based on frequency and position"
    )


class GoalAlignmentResult(BaseModel):
    """Output model for goal alignment analysis results."""
    
    # Overall metrics
    alignment_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall alignment score between 0 and 1"
    )
    
    # Topic matching
    matched_topics: list[TopicMatch] = Field(
        default_factory=list,
        description="List of matched topics/keywords"
    )
    matched_topic_count: int = Field(
        ...,
        description="Number of unique topics found in both goal and conversation"
    )
    
    # Keyword analysis
    goal_keywords: list[str] = Field(
        default_factory=list,
        description="Key terms extracted from goal text"
    )
    conversation_keywords: list[str] = Field(
        default_factory=list,
        description="Key terms extracted from conversation"
    )
    
    # Coverage metrics
    goal_coverage: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Percentage of goal keywords discussed in conversation (0-1)"
    )
    
    # Detailed analysis
    is_aligned: bool = Field(
        ...,
        description="Whether the conversation is aligned with the goal (threshold: 0.3)"
    )
    alignment_category: str = Field(
        ...,
        description="Alignment category: 'high', 'medium', 'low', or 'none'"
    )
    
    # Recommendations
    missing_topics: list[str] = Field(
        default_factory=list,
        description="Important topics from goal not discussed in conversation"
    )


class GoalAlignmentCalculator(BaseCalculator[GoalAlignmentInput, GoalAlignmentResult]):
    """
    Analyzes alignment between team member goals and conversation content.
    
    This calculator uses keyword extraction and frequency analysis to determine
    how well the conversation addresses the team member's stated goals.
    
    The algorithm:
    1. Extract keywords from both goal and conversation
    2. Find common keywords (topics)
    3. Calculate frequency-based relevance scores
    4. Compute overall alignment score
    5. Identify missing topics
    """
    
    # Minimum keyword length to consider
    MIN_KEYWORD_LENGTH = 2
    
    # Maximum number of keywords to extract
    MAX_KEYWORDS = 30
    
    # Common stop words (basic Korean and English)
    STOP_WORDS_KO = {
        "이", "그", "저", "것", "수", "등", "들", "및", "에", "을", "를", "이를",
        "위해", "통해", "대한", "있는", "하는", "되는", "같은", "있다", "한다",
        "많은", "다른", "새로운", "그리고", "하지만", "그러나", "또한", "및"
    }
    
    STOP_WORDS_EN = {
        "the", "is", "at", "which", "on", "a", "an", "as", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "should", "could", "may", "might", "must", "can",
        "and", "or", "but", "if", "then", "else", "when", "where", "how", "why"
    }
    
    def __init__(self):
        """Initialize the calculator with language-specific settings."""
        self.stop_words = self.STOP_WORDS_KO | self.STOP_WORDS_EN
    
    async def calculate(self, data: GoalAlignmentInput) -> GoalAlignmentResult:
        """
        Analyze goal alignment between goal text and conversation.
        
        Args:
            data: Goal alignment input with goal and conversation texts
            
        Returns:
            Detailed goal alignment analysis results
            
        Raises:
            ValueError: If input texts are empty or invalid
        """
        self.validate_input(data)
        
        # Extract keywords from both texts
        goal_keywords = self._extract_keywords(data.goal_text)
        conversation_keywords = self._extract_keywords(data.conversation_transcript)
        
        # Find matched topics
        matched_topics = self._find_matched_topics(
            goal_keywords,
            conversation_keywords,
            data.goal_text,
            data.conversation_transcript
        )
        
        # Calculate alignment metrics
        alignment_score = self._calculate_alignment_score(matched_topics, goal_keywords)
        goal_coverage = self._calculate_goal_coverage(goal_keywords, conversation_keywords)
        
        # Determine alignment category
        alignment_category = self._categorize_alignment(alignment_score)
        is_aligned = alignment_score >= 0.3
        
        # Find missing topics
        missing_topics = self._find_missing_topics(goal_keywords, conversation_keywords)
        
        return GoalAlignmentResult(
            alignment_score=alignment_score,
            matched_topics=matched_topics,
            matched_topic_count=len(matched_topics),
            goal_keywords=goal_keywords,
            conversation_keywords=conversation_keywords,
            goal_coverage=goal_coverage,
            is_aligned=is_aligned,
            alignment_category=alignment_category,
            missing_topics=missing_topics,
        )
    
    def _extract_keywords(self, text: str) -> list[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Input text to extract keywords from
            
        Returns:
            List of extracted keywords, ordered by importance
        """
        # Normalize text: lowercase and remove special characters
        normalized = text.lower()
        
        # Extract words (handling both Korean and English)
        # Korean: 한글 문자, English: alphabetic characters
        words = re.findall(r'[가-힣]+|[a-z]+', normalized)
        
        # Filter out stop words and short words
        filtered_words = [
            word for word in words
            if len(word) >= self.MIN_KEYWORD_LENGTH and word not in self.stop_words
        ]
        
        # Count word frequencies
        word_freq = Counter(filtered_words)
        
        # Get top keywords by frequency
        top_keywords = [
            word for word, _ in word_freq.most_common(self.MAX_KEYWORDS)
        ]
        
        return top_keywords
    
    def _find_matched_topics(
        self,
        goal_keywords: list[str],
        conversation_keywords: list[str],
        goal_text: str,
        conversation_text: str
    ) -> list[TopicMatch]:
        """
        Find topics that appear in both goal and conversation.
        
        Args:
            goal_keywords: Keywords from goal text
            conversation_keywords: Keywords from conversation text
            goal_text: Original goal text
            conversation_text: Original conversation text
            
        Returns:
            List of matched topics with relevance scores
        """
        matched_topics = []
        
        # Find common keywords
        common_keywords = set(goal_keywords) & set(conversation_keywords)
        
        # Calculate frequencies in original texts
        goal_text_lower = goal_text.lower()
        conversation_text_lower = conversation_text.lower()
        
        for keyword in common_keywords:
            goal_freq = goal_text_lower.count(keyword)
            conv_freq = conversation_text_lower.count(keyword)
            
            # Calculate relevance score based on:
            # 1. Frequency in both texts
            # 2. Position in keyword lists (earlier = more important)
            goal_position_score = (
                1.0 - (goal_keywords.index(keyword) / len(goal_keywords))
                if keyword in goal_keywords else 0.0
            )
            conv_position_score = (
                1.0 - (conversation_keywords.index(keyword) / len(conversation_keywords))
                if keyword in conversation_keywords else 0.0
            )
            
            # Combined relevance score (0-1)
            relevance_score = (
                (goal_position_score + conv_position_score) / 2.0 *
                min(1.0, (goal_freq + conv_freq) / 10.0)  # Frequency boost, capped at 1.0
            )
            
            matched_topics.append(
                TopicMatch(
                    keyword=keyword,
                    goal_frequency=goal_freq,
                    conversation_frequency=conv_freq,
                    relevance_score=relevance_score
                )
            )
        
        # Sort by relevance score (descending)
        matched_topics.sort(key=lambda t: t.relevance_score, reverse=True)
        
        return matched_topics
    
    def _calculate_alignment_score(
        self,
        matched_topics: list[TopicMatch],
        goal_keywords: list[str]
    ) -> float:
        """
        Calculate overall alignment score.
        
        Args:
            matched_topics: List of matched topics with relevance scores
            goal_keywords: Keywords from goal text
            
        Returns:
            Alignment score between 0 and 1
        """
        if not goal_keywords:
            return 0.0
        
        if not matched_topics:
            return 0.0
        
        # Weighted sum of relevance scores
        total_relevance = sum(topic.relevance_score for topic in matched_topics)
        
        # Normalize by number of goal keywords (with diminishing returns)
        # This ensures that having some high-quality matches is better than
        # having many low-quality matches
        coverage_factor = len(matched_topics) / len(goal_keywords)
        quality_factor = total_relevance / len(matched_topics) if matched_topics else 0.0
        
        # Combined score (weighted average favoring quality)
        alignment_score = (0.6 * quality_factor + 0.4 * coverage_factor)
        
        # Clamp to [0, 1]
        return min(1.0, max(0.0, alignment_score))
    
    def _calculate_goal_coverage(
        self,
        goal_keywords: list[str],
        conversation_keywords: list[str]
    ) -> float:
        """
        Calculate what percentage of goal keywords were discussed.
        
        Args:
            goal_keywords: Keywords from goal text
            conversation_keywords: Keywords from conversation text
            
        Returns:
            Coverage ratio between 0 and 1
        """
        if not goal_keywords:
            return 0.0
        
        matched_count = len(set(goal_keywords) & set(conversation_keywords))
        return matched_count / len(goal_keywords)
    
    def _categorize_alignment(self, alignment_score: float) -> str:
        """
        Categorize alignment score into human-readable category.
        
        Args:
            alignment_score: Alignment score (0-1)
            
        Returns:
            Category string: 'high', 'medium', 'low', or 'none'
        """
        if alignment_score >= 0.7:
            return "high"
        elif alignment_score >= 0.4:
            return "medium"
        elif alignment_score >= 0.15:
            return "low"
        else:
            return "none"
    
    def _find_missing_topics(
        self,
        goal_keywords: list[str],
        conversation_keywords: list[str]
    ) -> list[str]:
        """
        Find important topics from goal that weren't discussed.
        
        Args:
            goal_keywords: Keywords from goal text
            conversation_keywords: Keywords from conversation text
            
        Returns:
            List of missing keywords (top 5 by importance)
        """
        missing = [
            keyword for keyword in goal_keywords
            if keyword not in conversation_keywords
        ]
        
        # Return top 5 most important (earliest in goal_keywords list)
        return missing[:5]
    
    def validate_input(self, data: GoalAlignmentInput) -> None:
        """
        Validate the input data.
        
        Args:
            data: Goal alignment input to validate
            
        Raises:
            ValueError: If data is invalid
        """
        if not data.goal_text or not data.goal_text.strip():
            raise ValueError("Goal text cannot be empty")
        
        if not data.conversation_transcript or not data.conversation_transcript.strip():
            raise ValueError("Conversation transcript cannot be empty")
        
        if len(data.goal_text) < 10:
            raise ValueError("Goal text is too short (minimum 10 characters)")
        
        if len(data.conversation_transcript) < 20:
            raise ValueError("Conversation transcript is too short (minimum 20 characters)")
