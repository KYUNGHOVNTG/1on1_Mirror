from typing import Optional, List
from sqlalchemy import select
from server.app.shared.base.repository import BaseRepository
from server.app.domain.oneonone.models.session import Goal

class GoalRepository(BaseRepository[Goal, Goal]):
    async def provide(self, input_data: Goal) -> Goal:
        self.db.add(input_data)
        return input_data

    async def get_by_user_id(self, user_id: int) -> List[Goal]:
        stmt = select(Goal).where(Goal.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
