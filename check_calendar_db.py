
import asyncio
from sqlalchemy import select
from server.app.core.database import AsyncSessionLocal
from server.app.domain.calendar.models.calendar_connection import CalendarConnection

async def check_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CalendarConnection))
        connections = result.scalars().all()
        print(f"Total connections: {len(connections)}")
        for conn in connections:
            print(f"ID: {conn.id}, UserID: {conn.user_id}, GoogleID: {conn.google_calendar_id}, Active: {conn.is_active}")

if __name__ == "__main__":
    asyncio.run(check_db())
