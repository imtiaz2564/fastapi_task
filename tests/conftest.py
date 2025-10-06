import pytest
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path to access the app package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Import from app package
from app.main import app
from app.database import Base, async_session_maker
from app.auth import get_db

# Use MySQL for testing (same as your development database but with test database)
TEST_DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/test_fastapi_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture(scope="session")
async def test_db(test_engine):
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop all tables (cleanup)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_engine, test_db):
    async with test_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = AsyncSession(bind=connection)

            # Override the dependency
            async def override_get_db():
                try:
                    yield session
                finally:
                    pass

            app.dependency_overrides[get_db] = override_get_db

            yield session

            # Rollback the transaction after test
            await transaction.rollback()
            app.dependency_overrides.clear()


@pytest.fixture
def client(db_session):
    with TestClient(app) as test_client:
        yield test_client