import asyncio
import time
from datetime import datetime
from multiprocessing import Process
from typing import Callable

from app.config import logger
from app.stats import utils


def sync_update_stats():
    asyncio.run(utils.update_api_data())


def inf_check(func: Callable):
    logger.info(f'creating stats update process...')
    while True:
        now = datetime.now()
        if now.second >= 50:
            process = Process(target=func)
            process.start()
            process.join()
        time.sleep(.5)


if __name__ == '__main__':
    inf_check(sync_update_stats)
