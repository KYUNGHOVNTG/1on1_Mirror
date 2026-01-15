from typing import Optional, List
from sqlalchemy import select
from server.app.shared.base.repository import BaseRepository
from server.app.domain.oneonone.models.session import OneOnOneSession

class SessionRepository(BaseRepository[OneOnOneSession, OneOnOneSession]):
    async def provide(self, input_data: OneOnOneSession) -> OneOnOneSession:
        self.db.add(input_data)
        return input_data

    async def get_by_company_id(self, company_id: int) -> List[OneOnOneSession]:
        stmt = select(OneOnOneSession).where(OneOnOneSession.company_id == company_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> List[OneOnOneSession]:
        stmt = select(OneOnOneSession).where(OneOnOneSession.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
