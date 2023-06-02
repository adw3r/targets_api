import time
from threading import Thread

import redis

from app import database, models, config
from app.config import logger

CACHE_AMOUNT = 5000

redis_cli = redis.Redis(password=config.REDIS_PASSWORD, host=config.REDIS_HOST, port=config.REDIS_PORT)


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
    result = redis_cli.lpush(source.source_name, *[target.email for target in targets_list])
    return result


def get_all_sources():
    session = database.create_sync_session()
    sources_list = session.query(models.Source).where(models.Source.is_available).all()
    return sources_list


def check_that_cache_is_not_empty():
    while True:
        sources = get_all_sources()
        for source in sources:
            cache_amount = redis_cli.llen(source.source_name)
            logger.info(f'{cache_amount, source}')
            if cache_amount < CACHE_AMOUNT:
                Thread(target=get_targets_list_from_source_to_cache, args=(source, 5000)).start()
        time.sleep(10)


if __name__ == '__main__':
    check_that_cache_is_not_empty()
