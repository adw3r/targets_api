from sqlalchemy import select, text, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def get_donors_with_false_status(session: AsyncSession) -> tuple[models.SpamDonor]:
    result = tuple(
        await session.scalars(
            select(models.SpamDonor).where(models.SpamDonor.status == False)
        )
    )
    return result


async def get_donor_by_name(session: AsyncSession, donor_name: str) -> models.SpamDonor:
    return await session.scalar(select(models.SpamDonor).where(models.SpamDonor.donor_name == donor_name))


async def get_all_links(session: AsyncSession) -> list[models.Bitly]:
    return [link for link in await session.scalars(select(models.Bitly))]


async def delete_api_data(session: AsyncSession) -> None:
    await session.execute(delete(models.ApiDataRow))
    await session.commit()


async def get_targets_with_update_sent_counter(session: AsyncSession, source: models.Source, limit: int = 1) -> list[
    models.TargetEmail]:
    statement = select(models.TargetEmail).where(models.TargetEmail.source_id == source.id).order_by(
        models.TargetEmail.sent_counter).limit(limit).with_for_update()
    targets: list[models.TargetEmail] = [t for t in await session.scalars(statement)]
    for target in targets:
        target.sent_counter += 1
        session.add(target)
    await session.commit()
    return targets


async def get_available_sources(session: AsyncSession) -> list[models.Source]:
    stmt = select(models.Source).where(models.Source.is_available)
    return [source for source in await session.scalars(stmt)]


async def get_available_sources_join_texts(session: AsyncSession) -> dict:
    stmt = 'select source_name, lang from sources join texts t on sources.text_id = t.id where sources.is_available'
    statement = text(stmt)
    results = await session.execute(statement)
    results = results.all()
    return {res[0]: {'lang': res[1]} for res in results}


async def get_source_by_name(session: AsyncSession, source_name: str) -> models.Source:
    stmt = select(models.Source).where(models.Source.source_name == source_name)
    return await session.scalar(stmt)


async def get_source_info_by_name(session: AsyncSession, source) -> dict:
    sqmt = '''
    select sources.source_name, count(target_emails.email) as amount, texts.lang
    from sources
             join target_emails on sources.id = target_emails.source_id
             join texts on sources.text_id = texts.id
    where sources.source_name = :source_name
    group by sources.source_name, texts.lang
    '''
    statement = text(sqmt)
    res = await session.execute(statement, {'source_name': source.source_name})
    res = res.first()
    return {'amount_left': res[1], 'text_lang': res[2], 'db_name': res[0]}


async def get_all_sources_info(session: AsyncSession) -> dict:
    stmt = '''
        select source_name, total_sent_counter, texts.lang
        from sources
             join target_emails on sources.id = target_emails.source_id
             join texts on sources.text_id = texts.id
        group by sources.source_name, texts.lang, total_sent_counter
    '''
    all_sources = await session.execute(text(stmt))
    sources_all = all_sources.all()
    result = {row[0]: {'lang': row[2], 'total_sent_counter': row[1]} for row in sources_all}
    return result


async def get_referral_with_name(session: AsyncSession, referral_name: str) -> list[models.Referral]:
    result = await session.scalar(select(models.Referral).where(models.Referral.name == referral_name))
    return result


async def get_referrals_with_where(db_session: AsyncSession, where=models.Referral.available) -> list[models.Referral]:
    return [referral for referral in await db_session.scalars(select(models.Referral).where(where))]
