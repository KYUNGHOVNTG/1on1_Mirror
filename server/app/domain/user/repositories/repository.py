from typing import Optional, List

from sqlalchemy import select
from server.app.shared.base.repository import BaseRepository
from server.app.domain.user.models.user import User

class UserRepository(BaseRepository[User, User]):
    async def provide(self, input_data: User) -> User:
        self.db.add(input_data)
        return input_data

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_company_id(self, company_id: int) -> List[User]:
        stmt = select(User).where(User.company_id == company_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
