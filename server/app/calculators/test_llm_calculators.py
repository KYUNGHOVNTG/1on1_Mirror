"""
Test suite for LLM-based calculator modules.

Note: These tests require a valid ANTHROPIC_API_KEY in .env
"""

import asyncio
import os
from typing import Any

from app.calculators.coaching_style_calculator import (
    CoachingStyleCalculator,
    CoachingStyleInput,
)
from app.calculators.safety_score_calculator import (
    SafetyScoreCalculator,
    SafetyScoreInput,
)
from app.core.config import settings


# Sample transcript for testing
SAMPLE_TRANSCRIPT = """
Manager: 자, 이번 프로젝트 지연된 이유가 뭐죠? 누구 책임입니까?
Member: 죄송합니다. 기술적인 이슈가 좀 생겨서...
Manager: 기술 이슈는 핑계고, 미리미리 체크 안 했나요? 내가 저번에 분명히 말했잖아요.
Member: 네... 제가 놓친 부분이 있습니다.
Manager: 다음부터는 이런 일 없도록 하세요. 매일 오전 9시까지 보고하고요.
Member: 알겠습니다. 혹시 인력 지원을 좀 받을 수 있을까요?
Manager: 인력 타령하지 말고 있는 자원으로 해결할 방법을 찾아보세요. 그게 능력이에요.
"""

async def test_coaching_style():
    """Test CoachingStyleCalculator."""
    print("=" * 60)
    print("Testing Coaching Style Calculator")
    print("=" * 60)
    
    if not settings.ANTHROPIC_API_KEY or "your_" in settings.ANTHROPIC_API_KEY:
        print("⚠️ SKIPPING: ANTHROPIC_API_KEY not set properly.")
        return

    calculator = CoachingStyleCalculator()
    input_data = CoachingStyleInput(transcript=SAMPLE_TRANSCRIPT)
    
    try:
        result = await calculator.calculate(input_data)
        
        print(f"\n📊 Scores:")
        print(f"  - Directive: {result.directive_score:.1f}%")
        print(f"  - Coaching: {result.coaching_score:.1f}%")
        print(f"  - Balance: {result.balance_assessment}")
        
        print(f"\n📝 Feedback:")
        print(f"  {result.improvement_feedback}")
        
        print(f"\n🔎 Key Examples:")
        for ex in result.key_examples:
            print(f"  - [{ex.style.upper()}] \"{ex.text}\" ({ex.reason})")
            
        print("\n✅ Coaching style analysis successful!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_safety_score():
    """Test SafetyScoreCalculator."""
    print("\n" + "=" * 60)
    print("Testing Safety Score Calculator")
    print("=" * 60)
    
    if not settings.ANTHROPIC_API_KEY or "your_" in settings.ANTHROPIC_API_KEY:
        print("⚠️ SKIPPING: ANTHROPIC_API_KEY not set properly.")
        return

    calculator = SafetyScoreCalculator()
    input_data = SafetyScoreInput(transcript=SAMPLE_TRANSCRIPT)
    
    try:
        result = await calculator.calculate(input_data)
        
        print(f"\n🛡️ Safety Score: {result.safety_score}/100")
        print(f"\n💡 Rationale: {result.score_rationale}")
        
        if result.risk_factors:
            print(f"\n⚠️ Risk Factors:")
            for risk in result.risk_factors:
                print(f"  - [{risk.category}] {risk.description}")
                if risk.quote:
                    print(f"    Quote: \"{risk.quote}\"")
        
        if result.positive_factors:
            print(f"\n✅ Positive Factors:")
            for pos in result.positive_factors:
                print(f"  - [{pos.category}] {pos.description}")
        
        print(f"\n📋 Manager Analysis: {result.manager_behavior_analysis}")
        
        print("\n✅ Safety score analysis successful!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run all tests."""
    print("\n⚠️ NOTE: Ensure ANTHROPIC_API_KEY is set in .env for these tests to work.\n")
    await test_coaching_style()
    await test_safety_score()


if __name__ == "__main__":
    asyncio.run(main())
