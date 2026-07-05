import asyncio
from sqlalchemy.future import select
from app.database import engine, async_session, Base
from app.models.house import House
from app.models.section import Section

async def seed():
    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session() as db:
        print("Checking for existing seed data...")
        
        # Houses
        houses_result = await db.execute(select(House))
        existing_houses = houses_result.scalars().all()
        
        if not existing_houses:
            print("Seeding Houses...")
            houses = [
                House(name="Poseidon", total_points=12840),
                House(name="Mercury", total_points=11250),
                House(name="Apollo", total_points=9820),
                House(name="Zeus", total_points=9140)
            ]
            db.add_all(houses)
        else:
            print(f"Houses already exist: {[h.name for h in existing_houses]}")
            
        # Sections
        sections_result = await db.execute(select(Section))
        existing_sections = sections_result.scalars().all()
        
        if not existing_sections:
            print("Seeding Sections...")
            sections = [
                Section(name="Grade 12-A", student_count=0),
                Section(name="Grade 12-B", student_count=0),
                Section(name="Grade 12-C", student_count=0)
            ]
            db.add_all(sections)
        else:
            print(f"Sections already exist: {[s.name for s in existing_sections]}")
            
        await db.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
