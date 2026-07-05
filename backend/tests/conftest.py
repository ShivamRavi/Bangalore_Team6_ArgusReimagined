import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.main import app
from app.models.house import House
from app.models.section import Section

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    """Create tables and seed Houses/Sections once per test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(
        bind=test_engine,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    ) as session:
        session.add_all([
            House(id=1, name="Poseidon", total_points=12840),
            House(id=2, name="Mercury", total_points=11250),
            House(id=3, name="Apollo", total_points=9820),
            House(id=4, name="Zeus", total_points=9140),
        ])
        session.add_all([
            Section(id=1, name="Grade 12-A", student_count=0),
            Section(id=2, name="Grade 12-B", student_count=0),
            Section(id=3, name="Grade 12-C", student_count=0),
        ])
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated DB session; endpoint commits roll back after each test."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
