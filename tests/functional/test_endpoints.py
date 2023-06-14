from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import httpx

from app.config import PORT


def check_target(_):
    target = httpx.get('http://localhost:%s/targets/ukgoo' % PORT, params={'method': 'pop'}).text
    print(target)
    return target


class TestEndpoints(TestCase):

    def test_status(self):
        resp = httpx.get('http://localhost:%s' % PORT)
        success = resp.status_code
        self.assertTrue(success < 400)

    def test_pop_target_multithreaded(self):  # 1000 200 thrds for ~8.2-4 | 200 200 thrds for ~2.8 | 1000 1000 thrds for ~3.6
        with ThreadPoolExecutor(200) as worker:
            targets = worker.map(check_target, [_ for _ in range(200)])
        for target in targets:
            self.assertTrue('@' in target)

    def test_pop_target(self):
        url = 'http://localhost:8281/targets/ukgoo?method=pop'
        target = httpx.get(url).text
        print(target)
        self.assertTrue('@' in target)
