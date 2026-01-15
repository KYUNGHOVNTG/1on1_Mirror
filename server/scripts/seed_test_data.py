"""
원온원 미러 테스트 데이터 생성 스크립트

/analyze 엔드포인트 테스트를 위한 샘플 데이터를 생성합니다.
- Company: VNTG
- Manager User: 조직장
- Member User: 팀원 (Goal 포함)
- OneOnOneSession: Manager-Member 1on1 세션
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 로드 (스크립트 실행 시 필수)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from sqlalchemy import select
from server.app.core.database import AsyncSessionLocal, DatabaseManager
from server.app.core.config import settings
from server.app.domain.company.models.company import Company
from server.app.domain.user.models.user import Department, User
from server.app.domain.oneonone.models.session import Goal, OneOnOneSession

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def seed_test_data() -> None:
    """
    테스트용 데이터를 DB에 생성합니다.

    이미 존재하는 데이터는 건너뛰고, 새로운 데이터만 추가합니다.

    Returns:
        None

    Raises:
        Exception: 데이터베이스 작업 중 오류 발생 시
    """
    # 디버깅: DB URL 확인 (비밀번호 마스킹)
    db_url = str(settings.DATABASE_URL)
    masked_url = db_url.replace(str(settings.POSTGRES_PASSWORD), "****") if settings.POSTGRES_PASSWORD else db_url
    logger.info(f"🔗 데이터베이스 연결: {masked_url}")

    # 테이블 생성 (존재하지 않는 경우)
    logger.info("📋 테이블 존재 여부 확인 중...")
    await DatabaseManager.create_tables()

    async with AsyncSessionLocal() as db:
        try:
            # ==================== 1. Company 생성 ====================
            logger.info("🏢 Company 데이터 확인 중...")
            company_domain = "vntg.company"
            stmt = select(Company).where(Company.domain == company_domain)
            result = await db.execute(stmt)
            company = result.scalar_one_or_none()

            if not company:
                logger.info(f"✨ Company 생성: VNTG ({company_domain})")
                company = Company(
                    name="VNTG",
                    business_number="123-45-67890",
                    domain=company_domain,
                    is_active=True
                )
                db.add(company)
                await db.flush()  # ID 생성을 위해 flush
                logger.info(f"✅ Company 생성 완료 (ID: {company.id})")
            else:
                logger.info(f"ℹ️  Company 이미 존재 (ID: {company.id})")

            # ==================== 2. Department 생성 ====================
            logger.info("🏗️  Department 데이터 확인 중...")
            stmt = select(Department).where(
                Department.company_id == company.id,
                Department.name == "개발팀"
            )
            result = await db.execute(stmt)
            department = result.scalar_one_or_none()

            if not department:
                logger.info("✨ Department 생성: 개발팀")
                department = Department(
                    company_id=company.id,
                    name="개발팀",
                    parent_id=None
                )
                db.add(department)
                await db.flush()
                logger.info(f"✅ Department 생성 완료 (ID: {department.id})")
            else:
                logger.info(f"ℹ️  Department 이미 존재 (ID: {department.id})")

            # ==================== 3. Manager User 생성 ====================
            logger.info("👔 Manager User 확인 중...")
            manager_email = "manager@vntg.company"
            stmt = select(User).where(User.email == manager_email)
            result = await db.execute(stmt)
            manager = result.scalar_one_or_none()

            if not manager:
                logger.info(f"✨ Manager User 생성: 조직장 ({manager_email})")
                manager = User(
                    company_id=company.id,
                    department_id=department.id,
                    email=manager_email,
                    google_id=f"google_manager_{datetime.now().timestamp()}",
                    name="조직장",
                    role="manager"
                )
                db.add(manager)
                await db.flush()
                logger.info(f"✅ Manager User 생성 완료 (ID: {manager.id})")
            else:
                logger.info(f"ℹ️  Manager User 이미 존재 (ID: {manager.id})")

            # ==================== 4. Member User 생성 ====================
            logger.info("👤 Member User 확인 중...")
            member_email = "member@vntg.company"
            stmt = select(User).where(User.email == member_email)
            result = await db.execute(stmt)
            member = result.scalar_one_or_none()

            if not member:
                logger.info(f"✨ Member User 생성: 팀원 ({member_email})")
                member = User(
                    company_id=company.id,
                    department_id=department.id,
                    email=member_email,
                    google_id=f"google_member_{datetime.now().timestamp()}",
                    name="팀원",
                    role="member"
                )
                db.add(member)
                await db.flush()
                logger.info(f"✅ Member User 생성 완료 (ID: {member.id})")
            else:
                logger.info(f"ℹ️  Member User 이미 존재 (ID: {member.id})")

            # ==================== 5. Goal 생성 ====================
            logger.info("🎯 Goal 데이터 확인 중...")
            stmt = select(Goal).where(Goal.user_id == member.id)
            result = await db.execute(stmt)
            existing_goals = result.scalars().all()

            if not existing_goals:
                logger.info("✨ Goal 생성: Q1 백엔드 성능 개선")
                goal = Goal(
                    user_id=member.id,
                    content="Q1 백엔드 API 응답 시간 30% 개선",
                    criteria="평균 응답 시간 300ms 이하 달성, 모든 엔드포인트 p95 < 500ms",
                    status="in_progress"
                )
                db.add(goal)
                await db.flush()
                logger.info(f"✅ Goal 생성 완료 (ID: {goal.id})")
            else:
                logger.info(f"ℹ️  Goal 이미 존재 (개수: {len(existing_goals)})")

            # ==================== 6. OneOnOneSession 생성 ====================
            logger.info("📅 OneOnOneSession 확인 중...")
            stmt = select(OneOnOneSession).where(
                OneOnOneSession.manager_id == manager.id,
                OneOnOneSession.user_id == member.id,
                OneOnOneSession.status == "scheduled"
            )
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()

            if not session:
                logger.info("✨ OneOnOneSession 생성")
                scheduled_time = datetime.now() + timedelta(days=3)
                session = OneOnOneSession(
                    company_id=company.id,
                    user_id=member.id,
                    manager_id=manager.id,
                    topic="Q1 성과 리뷰 및 커리어 개발 논의",
                    status="scheduled",
                    scheduled_at=scheduled_time,
                    report_data=None
                )
                db.add(session)
                await db.flush()
                logger.info(f"✅ OneOnOneSession 생성 완료 (ID: {session.id})")
                logger.info(f"   📆 예정 시간: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logger.info(f"ℹ️  OneOnOneSession 이미 존재 (ID: {session.id})")

            # ==================== 7. Commit ====================
            await db.commit()
            logger.info("=" * 60)
            logger.info("🎉 테스트 데이터 생성 완료!")
            logger.info("=" * 60)
            logger.info(f"📊 생성된 데이터 요약:")
            logger.info(f"   - Company: {company.name} (ID: {company.id})")
            logger.info(f"   - Manager: {manager.name} ({manager.email})")
            logger.info(f"   - Member: {member.name} ({member.email})")
            logger.info(f"   - OneOnOneSession ID: {session.id}")
            logger.info(f"   - Session Status: {session.status}")
            logger.info("=" * 60)
            logger.info(f"🧪 /analyze 엔드포인트 테스트 가능:")
            logger.info(f"   curl -X POST http://localhost:8000/api/v1/sessions/{session.id}/analyze")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ 데이터 생성 실패: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    logger.info("🚀 테스트 데이터 생성 스크립트 시작")
    logger.info("=" * 60)
    try:
        asyncio.run(seed_test_data())
    except KeyboardInterrupt:
        logger.info("\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"\n💥 스크립트 실행 중 오류 발생: {e}")
        raise
