"""
Speech analyzer calculator for analyzing conversation dynamics from Whisper transcriptions.
"""

from pydantic import BaseModel, Field

from server.app.calculators.base import BaseCalculator


class SpeechSegment(BaseModel):
    """A single speech segment from Whisper transcription."""
    
    speaker: str = Field(..., description="Speaker identifier (e.g., 'manager' or 'member')")
    text: str = Field(..., description="Transcribed text content")
    start_time: float = Field(..., description="Segment start time in seconds")
    end_time: float = Field(..., description="Segment end time in seconds")
    
    @property
    def duration(self) -> float:
        """Calculate the duration of this segment in seconds."""
        return self.end_time - self.start_time


class WhisperTranscription(BaseModel):
    """Input model for Whisper transcription data."""
    
    segments: list[SpeechSegment] = Field(..., description="List of speech segments")
    manager_identifier: str = Field(
        default="manager",
        description="Identifier used to mark manager segments"
    )
    member_identifier: str = Field(
        default="member", 
        description="Identifier used to mark member segments"
    )
    total_duration: float | None = Field(
        default=None,
        description="Total meeting duration in seconds (optional)"
    )


class SpeechAnalysisResult(BaseModel):
    """Output model for speech analysis results."""
    
    # Speaking time metrics (in seconds)
    manager_speaking_time: float = Field(
        ...,
        description="Total time the manager spoke in seconds"
    )
    member_speaking_time: float = Field(
        ...,
        description="Total time the member spoke in seconds"
    )
    total_speaking_time: float = Field(
        ...,
        description="Total active speaking time in seconds"
    )
    
    # Silence/pause metrics
    total_silence_time: float = Field(
        ...,
        description="Total silence time between segments in seconds"
    )
    silence_percentage: float = Field(
        ...,
        description="Percentage of total time that was silence"
    )
    
    # Speaking ratio metrics
    manager_speaking_ratio: float = Field(
        ...,
        description="Manager's share of total speaking time (0-1)"
    )
    member_speaking_ratio: float = Field(
        ...,
        description="Member's share of total speaking time (0-1)"
    )
    
    # Turn-taking metrics
    manager_turn_count: int = Field(
        ...,
        description="Number of times the manager spoke"
    )
    member_turn_count: int = Field(
        ...,
        description="Number of times the member spoke"
    )
    total_turns: int = Field(
        ...,
        description="Total number of speaking turns"
    )
    
    # Average segment duration
    manager_avg_segment_duration: float = Field(
        ...,
        description="Average duration of manager's speech segments in seconds"
    )
    member_avg_segment_duration: float = Field(
        ...,
        description="Average duration of member's speech segments in seconds"
    )
    
    # Meeting metadata
    meeting_duration: float = Field(
        ...,
        description="Total meeting duration in seconds"
    )


class SpeechAnalyzer(BaseCalculator[WhisperTranscription, SpeechAnalysisResult]):
    """
    Analyzes speech patterns from Whisper transcription data.
    
    This calculator processes timestamped speech segments to compute:
    - Speaking time distribution between manager and member
    - Silence/pause durations
    - Turn-taking patterns
    - Conversation balance metrics
    """
    
    async def calculate(self, data: WhisperTranscription) -> SpeechAnalysisResult:
        """
        Analyze speech patterns from Whisper transcription.
        
        Args:
            data: Whisper transcription with timestamped segments
            
        Returns:
            Detailed speech analysis results
            
        Raises:
            ValueError: If segments are invalid or empty
        """
        self.validate_input(data)
        
        if not data.segments:
            raise ValueError("Cannot analyze empty transcription")
        
        # Sort segments by start time to ensure chronological order
        sorted_segments = sorted(data.segments, key=lambda s: s.start_time)
        
        # Calculate speaking times and turn counts
        manager_time = 0.0
        member_time = 0.0
        manager_turns = 0
        member_turns = 0
        
        for segment in sorted_segments:
            duration = segment.duration
            
            if segment.speaker == data.manager_identifier:
                manager_time += duration
                manager_turns += 1
            elif segment.speaker == data.member_identifier:
                member_time += duration
                member_turns += 1
        
        total_speaking_time = manager_time + member_time
        
        # Calculate silence time
        total_silence_time = self._calculate_silence_time(sorted_segments)
        
        # Determine meeting duration
        if data.total_duration:
            meeting_duration = data.total_duration
        else:
            # Use the last segment's end time as meeting duration
            meeting_duration = sorted_segments[-1].end_time if sorted_segments else 0.0
        
        # Calculate percentages and ratios
        silence_percentage = (
            (total_silence_time / meeting_duration * 100) if meeting_duration > 0 else 0.0
        )
        
        manager_ratio = (
            manager_time / total_speaking_time if total_speaking_time > 0 else 0.0
        )
        member_ratio = (
            member_time / total_speaking_time if total_speaking_time > 0 else 0.0
        )
        
        # Calculate average segment durations
        manager_avg_duration = (
            manager_time / manager_turns if manager_turns > 0 else 0.0
        )
        member_avg_duration = (
            member_time / member_turns if member_turns > 0 else 0.0
        )
        
        return SpeechAnalysisResult(
            manager_speaking_time=manager_time,
            member_speaking_time=member_time,
            total_speaking_time=total_speaking_time,
            total_silence_time=total_silence_time,
            silence_percentage=silence_percentage,
            manager_speaking_ratio=manager_ratio,
            member_speaking_ratio=member_ratio,
            manager_turn_count=manager_turns,
            member_turn_count=member_turns,
            total_turns=manager_turns + member_turns,
            manager_avg_segment_duration=manager_avg_duration,
            member_avg_segment_duration=member_avg_duration,
            meeting_duration=meeting_duration,
        )
    
    def _calculate_silence_time(self, sorted_segments: list[SpeechSegment]) -> float:
        """
        Calculate total silence time between speech segments.
        
        Args:
            sorted_segments: List of segments sorted by start_time
            
        Returns:
            Total silence time in seconds
        """
        if len(sorted_segments) < 2:
            return 0.0
        
        total_silence = 0.0
        
        for i in range(len(sorted_segments) - 1):
            current_end = sorted_segments[i].end_time
            next_start = sorted_segments[i + 1].start_time
            
            # Only count positive gaps as silence (ignore overlaps)
            gap = next_start - current_end
            if gap > 0:
                total_silence += gap
        
        return total_silence
    
    def validate_input(self, data: WhisperTranscription) -> None:
        """
        Validate the input transcription data.
        
        Args:
            data: Whisper transcription to validate
            
        Raises:
            ValueError: If data is invalid
        """
        if not data.segments:
            raise ValueError("Segments list cannot be empty")
        
        for i, segment in enumerate(data.segments):
            if segment.start_time < 0:
                raise ValueError(f"Segment {i} has negative start_time: {segment.start_time}")
            
            if segment.end_time < segment.start_time:
                raise ValueError(
                    f"Segment {i} has end_time ({segment.end_time}) before start_time ({segment.start_time})"
                )
            
            if segment.speaker not in [data.manager_identifier, data.member_identifier]:
                raise ValueError(
                    f"Segment {i} has invalid speaker '{segment.speaker}'. "
                    f"Expected '{data.manager_identifier}' or '{data.member_identifier}'"
                )
