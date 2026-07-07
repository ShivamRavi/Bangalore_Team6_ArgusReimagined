import asyncio, os, sys

# Ensure the backend package is on the import path
sys.path.append(os.path.abspath('backend'))

from app.seed import seed_houses_and_sections
from app.database import async_session

async def main():
    async with async_session() as db:
        await seed_houses_and_sections(db)

if __name__ == '__main__':
    asyncio.run(main())
