import multiprocessing
import time
from threading import Thread

import redis

from app import database, models, config
from app.config import logger


redis_cli = redis.Redis(password=config.REDIS_PASSWORD, port=config.REDIS_PORT, host=config.REDIS_HOST)
caching_processes: list[multiprocessing.Process] = []


def kill_cache():
    for p in caching_processes:
        p.kill()


def create_cache():
    cache_process = multiprocessing.Process(target=check_that_cache_is_not_empty)
    cache_process.start()
    caching_processes.append(cache_process)


def get_targets_list_from_source_to_cache(source: models.Source, limit: int = config.CACHE_AMOUNT):
    with database.create_sync_session() as session:
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
    with database.create_sync_session() as session:
        sources_list = session.query(models.Source).where(models.Source.is_available).all()
    return sources_list


def check_that_cache_is_not_empty():
    logger.info('creating cache...')
    logger.info(f'Redis status {redis_cli.ping()}')
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
            if current_cache_amount < config.CACHE_AMOUNT and source.source_name not in [t.name for t in active_threads]:
                thread = Thread(target=get_targets_list_from_source_to_cache, args=(source, config.CACHE_AMOUNT / 4),
                                name=source.source_name)
                thread.start()
                active_threads.append(thread)
        time.sleep(0.5)
