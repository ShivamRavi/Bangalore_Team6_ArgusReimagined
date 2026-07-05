import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.house import House
from app.models.section import Section
from app.models.user import User
from app.models.transaction import Transaction, CurrencyType

@pytest.mark.asyncio
async def test_create_house_success(db: AsyncSession):
    """Test creating a House model successfully."""
    house = House(name="Gryffindor", total_points=100)
    db.add(house)
    await db.commit()
    
    result = await db.execute(select(House).where(House.name == "Gryffindor"))
    fetched_house = result.scalars().first()
    assert fetched_house is not None
    assert fetched_house.name == "Gryffindor"
    assert fetched_house.total_points == 100

@pytest.mark.asyncio
async def test_house_unique_name(db: AsyncSession):
    """Test that House name has unique constraint."""
    house1 = House(name="DupHouse")
    db.add(house1)
    await db.commit()
    
    house2 = House(name="DupHouse")
    db.add(house2)
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()

@pytest.mark.asyncio
async def test_create_section_success(db: AsyncSession):
    """Test creating a Section model successfully."""
    section = Section(name="Grade 11-A", student_count=10)
    db.add(section)
    await db.commit()
    
    result = await db.execute(select(Section).where(Section.name == "Grade 11-A"))
    fetched_section = result.scalars().first()
    assert fetched_section is not None
    assert fetched_section.student_count == 10

@pytest.mark.asyncio
async def test_create_user_with_defaults(db: AsyncSession):
    """Test user creation and verification of default values."""
    user = User(
        username="default_val_user",
        hashed_password="somehashedpwd",
        role="STUDENT"
    )
    db.add(user)
    await db.commit()
    
    result = await db.execute(select(User).where(User.username == "default_val_user"))
    fetched_user = result.scalars().first()
    assert fetched_user is not None
    assert isinstance(fetched_user.id, uuid.UUID)
    assert fetched_user.euros_balance == 0
    assert fetched_user.lifetime_euros == 0
    assert fetched_user.current_planet == "Mercury"
    assert fetched_user.current_streak == 0
    assert fetched_user.house_id is None
    assert fetched_user.section_id is None

@pytest.mark.asyncio
async def test_user_unique_username(db: AsyncSession):
    """Test that username has unique constraint."""
    user1 = User(username="dup_user", hashed_password="hash1", role="STUDENT")
    db.add(user1)
    await db.commit()

    user2 = User(username="dup_user", hashed_password="hash2", role="STUDENT")
    db.add(user2)
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()


@pytest.mark.asyncio
async def test_create_user_with_relations(db: AsyncSession):
    """Test user linked to House and Section."""
    # Seed a house and section
    house = House(name="TestHouse", total_points=0)
    section = Section(name="TestSection", student_count=1)
    db.add_all([house, section])
    await db.commit()
    
    user = User(
        username="linked_user",
        hashed_password="somehashedpwd",
        role="STUDENT",
        house_id=house.id,
        section_id=section.id
    )
    db.add(user)
    await db.commit()
    
    result = await db.execute(
        select(User).where(User.username == "linked_user")
    )
    fetched_user = result.scalars().first()
    assert fetched_user is not None
    assert fetched_user.house_id == house.id
    assert fetched_user.section_id == section.id

@pytest.mark.asyncio
async def test_create_transaction(db: AsyncSession):
    """Test creating a transaction linked to a user."""
    user = User(
        username="transaction_user",
        hashed_password="somehashedpwd",
        role="STUDENT"
    )
    db.add(user)
    await db.commit()
    
    tx = Transaction(
        user_id=user.id,
        currency_type=CurrencyType.EUROS,
        amount=10,
        reason="Completed Worksheet"
    )
    db.add(tx)
    await db.commit()
    
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user.id)
    )
    fetched_tx = result.scalars().first()
    assert fetched_tx is not None
    assert fetched_tx.amount == 10
    assert fetched_tx.currency_type == CurrencyType.EUROS
    assert fetched_tx.reason == "Completed Worksheet"
