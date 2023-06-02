import time
from threading import Thread

import redis

from app import database, models, config
from app.config import logger

CACHE_AMOUNT = 10000

redis_cli = redis.Redis(password=config.REDIS_PASSWORD, port=config.REDIS_PORT, host='10.107.8.10')
logger.info(f'Redis status {redis_cli.ping()}')


def get_targets_list_from_source_to_cache(source: models.Source, limit: int = CACHE_AMOUNT):
    session = database.create_sync_session()
    targets_list = session.query(models.TargetEmail) \
        .where(models.TargetEmail.source_id == source.id) \
        .order_by(models.TargetEmail.sent_counter) \
        .limit(limit).all()
    for target in targets_list:
        target.sent_counter += 1
        session.add(target)
    session.commit()
    session.close()
    result = redis_cli.lpush(source.source_name, *[target.email for target in targets_list])
    return result


def get_all_sources():
    session = database.create_sync_session()
    sources_list = session.query(models.Source).where(models.Source.is_available).all()
    session.close()
    return sources_list


def check_that_cache_is_not_empty():
    active_threads = []
    while True:
        if not any([thread.is_alive() for thread in active_threads]):
            active_threads = []
        logger.info(f'{active_threads=}')
        try:
            sources = get_all_sources()
        except Exception as error:
            logger.error(error)
            continue
        for source in sources:
            current_cache_amount = redis_cli.llen(source.source_name)
            logger.info(f'{current_cache_amount, source}')
            if current_cache_amount < CACHE_AMOUNT and source.source_name not in [t.name for t in active_threads]:
                thread = Thread(target=get_targets_list_from_source_to_cache, args=(source, CACHE_AMOUNT/2), name=source.source_name)
                thread.start()
                active_threads.append(thread)
        time.sleep(1)


if __name__ == '__main__':
    check_that_cache_is_not_empty()
