from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def get_all_donors(session: AsyncSession):
    query = select(models.SpamDonor).order_by(models.SpamDonor.updated_at.desc())
    result = await session.execute(query)
    result = [i for i in result.scalars()]
    return result
