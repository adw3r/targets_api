from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import httpx

from config import PORT


def check_target(_):
    resp = httpx.get('http://localhost:%s/targets/turk' % PORT, params={'method': 'pop'}).text
    print(resp)
    return '@' in resp


class TestEndpoints(TestCase):

    def test_status(self):
        resp = httpx.get('http://localhost:%s' % PORT)
        success = resp.status_code
        self.assertTrue(success < 400)

    def test_targets_pool(self):
        resp = httpx.get('http://localhost:%s/targets/turk' % PORT, params={'method': 'pool'}).text.splitlines()
        for line in resp:
            print(line)
            self.assertTrue('@' in line)

    def test_get_info(self):
        resp = httpx.get('http://localhost:%s/targets/turk' % PORT, params={'method': 'info'}).json()
        print(resp)
        self.assertTrue(resp['lang'] is not None)
        self.assertTrue(resp['available'] is not None)

    def test_pop_target(self):  # 4 multithreaded
        with ThreadPoolExecutor(200) as worker:
            results = [res for res in worker.map(check_target, [_ for _ in range(1000)])]
        print(results)
