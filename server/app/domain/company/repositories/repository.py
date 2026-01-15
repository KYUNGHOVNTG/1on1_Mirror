from typing import Optional

from sqlalchemy import select
from server.app.shared.base.repository import BaseRepository
from server.app.domain.company.models.company import Company

class CompanyRepository(BaseRepository[Company, Company]):
    async def provide(self, input_data: Company) -> Company:
        """
        Company 객체를 DB에 저장합니다.
        """
        self.db.add(input_data)
        # Service layer handles commit
        return input_data

    async def get_by_domain(self, domain: str) -> Optional[Company]:
        stmt = select(Company).where(Company.domain == domain)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, id: int) -> Optional[Company]:
        stmt = select(Company).where(Company.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
