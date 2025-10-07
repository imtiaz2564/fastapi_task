import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.database import async_session_maker
from app.db import models

async def cleanup_database():
    async with async_session_maker() as session:
        try:
            # Delete all token sessions and users
            await session.execute(models.TokenSession.__table__.delete())
            await session.execute(models.User.__table__.delete())
            await session.commit()
            print("✅ Database cleaned successfully!")
        except Exception as e:
            print(f"❌ Error cleaning database: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(cleanup_database())