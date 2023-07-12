import asyncio
import time
from datetime import datetime
from multiprocessing import Process

from app.config import logger
from app.stats import utils


def inf_update_stats():
    asyncio.run(utils.update_api_data())


def inf_check():
    logger.info(f'creating stats update process...')

    while True:
        now = datetime.now()
        if now.second == 58:
            process = Process(target=inf_update_stats)
            process.start()
            process.join()
        time.sleep(.5)


if __name__ == '__main__':
    inf_check()
