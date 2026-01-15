"""
Test suite for calculator modules.
"""

import asyncio

from server.app.calculators.speech_analyzer import (
    SpeechAnalyzer,
    SpeechSegment,
    WhisperTranscription,
)
from server.app.calculators.goal_alignment_calculator import (
    GoalAlignmentCalculator,
    GoalAlignmentInput,
)


async def test_speech_analyzer():
    """Test the speech analyzer with sample data."""
    print("=" * 60)
    print("Testing Speech Analyzer")
    print("=" * 60)
    
    # Create sample Whisper transcription data
    transcription = WhisperTranscription(
        segments=[
            SpeechSegment(
                speaker="manager",
                text="안녕하세요. 오늘 1on1 미팅을 시작하겠습니다.",
                start_time=0.0,
                end_time=3.5
            ),
            SpeechSegment(
                speaker="member",
                text="네, 안녕하세요.",
                start_time=4.0,
                end_time=5.2
            ),
            SpeechSegment(
                speaker="manager",
                text="이번 주 업무는 어떻게 진행되고 있나요?",
                start_time=6.0,
                end_time=9.0
            ),
            SpeechSegment(
                speaker="member",
                text="프로젝트가 순조롭게 진행되고 있습니다. 특히 새로운 기능 개발이 잘 되고 있어요.",
                start_time=9.5,
                end_time=14.0
            ),
            SpeechSegment(
                speaker="manager",
                text="좋네요. 어려운 점은 없나요?",
                start_time=15.0,
                end_time=17.5
            ),
            SpeechSegment(
                speaker="member",
                text="약간의 기술적 문제가 있었지만 해결했습니다. 팀원들과 협업도 잘 되고 있습니다.",
                start_time=18.0,
                end_time=23.5
            ),
        ],
        manager_identifier="manager",
        member_identifier="member",
        total_duration=30.0
    )
    
    # Run analysis
    analyzer = SpeechAnalyzer()
    result = await analyzer.calculate(transcription)
    
    # Print results
    print(f"\n📊 Speaking Time Analysis:")
    print(f"  - Manager speaking time: {result.manager_speaking_time:.2f}s")
    print(f"  - Member speaking time: {result.member_speaking_time:.2f}s")
    print(f"  - Total speaking time: {result.total_speaking_time:.2f}s")
    
    print(f"\n🔇 Silence Analysis:")
    print(f"  - Total silence time: {result.total_silence_time:.2f}s")
    print(f"  - Silence percentage: {result.silence_percentage:.1f}%")
    
    print(f"\n⚖️ Speaking Ratio:")
    print(f"  - Manager ratio: {result.manager_speaking_ratio:.1%}")
    print(f"  - Member ratio: {result.member_speaking_ratio:.1%}")
    
    print(f"\n🔄 Turn-taking:")
    print(f"  - Manager turns: {result.manager_turn_count}")
    print(f"  - Member turns: {result.member_turn_count}")
    print(f"  - Total turns: {result.total_turns}")
    
    print(f"\n⏱️ Average Segment Duration:")
    print(f"  - Manager avg: {result.manager_avg_segment_duration:.2f}s")
    print(f"  - Member avg: {result.member_avg_segment_duration:.2f}s")
    
    print(f"\n✅ Speech analysis completed successfully!\n")


async def test_goal_alignment_calculator():
    """Test the goal alignment calculator with sample data."""
    print("=" * 60)
    print("Testing Goal Alignment Calculator")
    print("=" * 60)
    
    # Create sample goal and conversation data
    goal_input = GoalAlignmentInput(
        goal_text="""
        Q2 목표: 새로운 AI 기능 개발 및 사용자 경험 개선
        - 머신러닝 모델 정확도 향상
        - 사용자 인터페이스 리팩토링
        - 성능 최적화 및 테스트 자동화
        - 팀 협업 강화 및 코드 리뷰 프로세스 개선
        """,
        conversation_transcript="""
        Manager: 안녕하세요. 오늘 1on1 미팅을 시작하겠습니다.
        Member: 네, 안녕하세요.
        Manager: 이번 주 업무는 어떻게 진행되고 있나요?
        Member: 프로젝트가 순조롭게 진행되고 있습니다. 특히 새로운 AI 기능 개발이 잘 되고 있어요.
                머신러닝 모델의 정확도도 많이 향상되었습니다.
        Manager: 좋네요. 어려운 점은 없나요?
        Member: 약간의 기술적 문제가 있었지만 해결했습니다. 팀원들과 협업도 잘 되고 있고,
                코드 리뷰를 통해 코드 품질도 개선되고 있습니다.
        Manager: 사용자 인터페이스 작업은 어떻게 되고 있나요?
        Member: 아직 시작하지 못했습니다. 다음 주부터 시작할 예정입니다.
        Manager: 알겠습니다. 성능 테스트는 진행하셨나요?
        Member: 네, 기본적인 성능 최적화는 완료했습니다.
        """,
        language="ko"
    )
    
    # Run analysis
    calculator = GoalAlignmentCalculator()
    result = await calculator.calculate(goal_input)
    
    # Print results
    print(f"\n🎯 Overall Alignment:")
    print(f"  - Alignment Score: {result.alignment_score:.2%}")
    print(f"  - Category: {result.alignment_category.upper()}")
    print(f"  - Is Aligned: {'✅ Yes' if result.is_aligned else '❌ No'}")
    
    print(f"\n📈 Coverage Metrics:")
    print(f"  - Goal Coverage: {result.goal_coverage:.1%}")
    print(f"  - Matched Topics: {result.matched_topic_count}")
    
    print(f"\n🔑 Top Matched Topics:")
    for i, topic in enumerate(result.matched_topics[:5], 1):
        print(f"  {i}. '{topic.keyword}' - Relevance: {topic.relevance_score:.2f}")
        print(f"     (Goal: {topic.goal_frequency}x, Conv: {topic.conversation_frequency}x)")
    
    print(f"\n📝 Goal Keywords ({len(result.goal_keywords)}):")
    print(f"  {', '.join(result.goal_keywords[:10])}")
    
    print(f"\n💬 Conversation Keywords ({len(result.conversation_keywords)}):")
    print(f"  {', '.join(result.conversation_keywords[:10])}")
    
    if result.missing_topics:
        print(f"\n⚠️ Missing Topics from Goal:")
        for topic in result.missing_topics:
            print(f"  - {topic}")
    
    print(f"\n✅ Goal alignment analysis completed successfully!\n")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 Running Calculator Tests")
    print("=" * 60 + "\n")
    
    try:
        await test_speech_analyzer()
        await test_goal_alignment_calculator()
        
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
