"""Seed data for Houses and Sections required before user registration."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.house import House
from app.models.section import Section

HOUSES_SEED = [
    {"name": "Poseidon", "total_points": 12840},
    {"name": "Mercury", "total_points": 11250},
    {"name": "Apollo", "total_points": 9820},
    {"name": "Zeus", "total_points": 9140},
]

SECTIONS_SEED = [
    {"name": "Grade 12-A", "student_count": 0},
    {"name": "Grade 12-B", "student_count": 0},
    {"name": "Grade 12-C", "student_count": 0},
]


async def seed_houses_and_sections(db: AsyncSession) -> bool:
    """Insert default Houses and Sections if none exist. Returns True if seeded."""
    result = await db.execute(select(House.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return False

    db.add_all([House(**row) for row in HOUSES_SEED])
    db.add_all([Section(**row) for row in SECTIONS_SEED])
    await db.commit()
    return True
