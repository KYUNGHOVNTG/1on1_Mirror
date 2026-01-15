from typing import Optional, List
from sqlalchemy import select
from server.app.shared.base.repository import BaseRepository
from server.app.domain.user.models.user import Department

class DepartmentRepository(BaseRepository[Department, Department]):
    async def provide(self, input_data: Department) -> Department:
        self.db.add(input_data)
        return input_data

    async def get_by_company_id(self, company_id: int) -> List[Department]:
        """
        특정 회사의 모든 부서를 조회합니다.
        """
        stmt = select(Department).where(Department.company_id == company_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_root_department(self, company_id: int) -> Optional[Department]:
        """
        특정 회사의 최상위 부서(Root Department)를 조회합니다.
        """
        stmt = select(Department).where(
            Department.company_id == company_id,
            Department.parent_id == None
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
