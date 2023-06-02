from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, database, service, schemas

router = APIRouter(
    prefix='/referrals',
    tags=['Referrals api']
)


@router.get('', response_model=list[schemas.ReferralSchema])
async def referral_method(db_session: AsyncSession = Depends(database.create_async_session)
                          ) -> list[schemas.ReferralSchema]:
    referral_models: list[models.Referral] = await service.get_referrals_with_where(db_session)
    return [schemas.ReferralSchema(**ref.as_dict()) for ref in referral_models]
