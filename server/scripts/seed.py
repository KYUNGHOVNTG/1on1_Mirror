import asyncio
import logging
import os
from dotenv import load_dotenv

# .env 로드 (스크립트 실행 시 필수)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from sqlalchemy import select
from server.app.core.database import AsyncSessionLocal, DatabaseManager
from server.app.core.config import settings
from server.app.domain.company.models.company import Company
from server.app.domain.user.models.user import Department, User

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    # 디버깅: DB URL 확인 (비번 마스킹)
    db_url = str(settings.DATABASE_URL)
    masked_url = db_url.replace(str(settings.POSTGRES_PASSWORD), "****") if settings.POSTGRES_PASSWORD else db_url
    logger.info(f"Connecting to DB: {masked_url}")

    # 테이블 생성 (혹시 모르니)
    logger.info("Ensuring tables exist...")
    await DatabaseManager.create_tables()

    async with AsyncSessionLocal() as db:
        try:
            # 1. Check existing Company
            stmt = select(Company).where(Company.domain == "vntgcorp.com")
            result = await db.execute(stmt)
            company = result.scalar_one_or_none()

            if not company:
                logger.info("Creating VNTG Company...")
                company = Company(
                    name="VNTG",
                    business_number="123-45-67890", # Dummy
                    domain="vntgcorp.com",
                    is_active=True
                )
                db.add(company)
                await db.flush() # ID 생성을 위해 flush
            else:
                logger.info("VNTG Company already exists.")

            # 2. Check existing Root Department
            stmt = select(Department).where(
                Department.company_id == company.id, 
                Department.parent_id == None
            )
            result = await db.execute(stmt)
            root_dept = result.scalar_one_or_none()

            if not root_dept:
                logger.info("Creating Root Department...")
                root_dept = Department(
                    company_id=company.id,
                    name="VNTG HQ",
                    parent_id=None
                )
                db.add(root_dept)
                await db.flush()
            else:
                logger.info("Root Department already exists.")

            # 3. Check existing Admin User
            admin_email = "admin@vntgcorp.com"
            stmt = select(User).where(User.email == admin_email)
            result = await db.execute(stmt)
            admin_user = result.scalar_one_or_none()

            if not admin_user:
                logger.info("Creating Admin User...")
                admin_user = User(
                    company_id=company.id,
                    department_id=root_dept.id,
                    email=admin_email,
                    google_id="admin_google_id_dummy",
                    name="Admin User",
                    role="admin"
                )
                db.add(admin_user)
            else:
                logger.info("Admin User already exists.")

            await db.commit()
            logger.info("Seeding completed successfully.")

        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            # 디버깅용 출력 (마지막에 보여지도록)
            db_url = str(settings.DATABASE_URL)
            masked = db_url.replace(settings.POSTGRES_PASSWORD, "****") if settings.POSTGRES_PASSWORD else db_url
            print(f"\n[DEBUG] FAILED WITH DB_URL: {masked}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_data())
