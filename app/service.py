import datetime

from sqlalchemy import select, text, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def add_api_data(session: AsyncSession, data_objects: list[models.ApiDataRow]):
    session.add_all(data_objects)
    await session.commit()


async def get_regs_stat_for_current_month(session: AsyncSession):
    date = datetime.datetime.today()
    res = await session.scalars(
        select(models.ApiDataRow).filter(
            func.date_trunc('month', models.ApiDataRow.date) == func.date_trunc('month', date),
            # func.date_trunc('day', models.ApiDataRow.date) == func.date_trunc('day', date),
            # func.date_trunc('year', models.ApiDataRow.date) == func.date_trunc('year', date),
        )
    )
    return res.all()


async def get_regs_stat_for_specific_date(session: AsyncSession, date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    res = await session.scalars(
        select(models.ApiDataRow).where(
            func.date_trunc('month', models.ApiDataRow.date) == func.date_trunc('month', date),
            func.date_trunc('day', models.ApiDataRow.date) == func.date_trunc('day', date),
            func.date_trunc('year', models.ApiDataRow.date) == func.date_trunc('year', date)
        )
    )
    return res.all()


async def get_regs_stat_for_today(session: AsyncSession):
    res = await session.scalars(select(models.ApiDataRow).where(models.ApiDataRow.date == func.current_date()))
    return res.all()


async def get_api_data(session: AsyncSession) -> list[models.ApiDataRow]:
    res = await session.scalars(select(models.ApiDataRow))
    return res.all()


async def get_all_links(session: AsyncSession) -> list[models.Bitly]:
    links = await session.scalars(select(models.Bitly))
    return links.all()


async def delete_api_data(session: AsyncSession):
    await session.execute(delete(models.ApiDataRow))
    await session.commit()


async def get_one_not_spammed_target_with_update(session: AsyncSession, source: models.Source, limit: int = 1):
    statement = select(models.TargetEmail) \
        .where(models.TargetEmail.source_id == source.id) \
        .order_by(models.TargetEmail.sent_counter).limit(limit).with_for_update()
    targets: models.TargetEmail = await session.scalars(statement)
    targets = targets.all()
    for target in targets:
        target.sent_counter += 1
        session.add(target)
    await session.commit()
    return targets


async def get_available_sources(session: AsyncSession):
    stmt = select(models.Source).where(models.Source.is_available)
    res = await session.scalars(stmt)
    return res.all()


async def get_available_sources_join_texts(session: AsyncSession):
    stmt = 'select source_name, lang from sources join texts t on sources.text_id = t.id where sources.is_available'
    statement = text(stmt)
    results = await session.execute(statement)
    results = results.all()
    return {res[0]: {'lang': res[1]} for res in results}


async def get_source_by_name(session: AsyncSession, source_name: str) -> models.Source:
    stmt = select(models.Source).where(models.Source.source_name == source_name)
    return await session.scalar(stmt)


async def get_source_info_by_name(session: AsyncSession, source):
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


async def get_all_sources_info(session: AsyncSession):
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


async def get_referral_with_name(session: AsyncSession, referral_name: str):
    result = await session.scalar(select(models.Referral).where(models.Referral.name == referral_name))
    return result


async def get_referrals_with_where(db_session: AsyncSession, where=models.Referral.available) -> list[models.Referral]:
    results = await db_session.scalars(select(models.Referral).where(where))
    return results.all()
