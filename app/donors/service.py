from sqlalchemy import select, text, delete, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def get_all_donors(session: AsyncSession):
    query = select(models.SpamDonor)
    result = await session.execute(query)
    return [i for i in result.scalars()]
