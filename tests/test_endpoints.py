from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import httpx

from config import PORT


def check_target(_):
    resp = httpx.get('http://localhost:%s/targets/turk' % PORT, params={'method': 'pop'}, timeout=60).text
    print(resp)
    return '@' in resp


class TestEndpoints(TestCase):

    def test_status(self):
        resp = httpx.get('http://localhost:%s' % PORT)
        success = resp.status_code
        success_ = success < 400
        print(success_)
        self.assertTrue(success_)

    def test_targets_pool(self):
        params = {'method': 'pool', 'limit': '100'}
        resp = httpx.get('http://localhost:%s/targets/turk' % PORT, params=params).text.splitlines()
        for line in resp:
            print(line)
            self.assertTrue('@' in line)

    def test_get_info(self):
        params = {'method': 'info'}
        resp = httpx.get('http://localhost:%s/targets/turk' % PORT, params=params).json()
        print(resp)
        self.assertTrue(resp['lang'] is not None)
        self.assertTrue(resp['amount'] is not None)

    def test_pop_target(self):  # 4 multithreaded
        threads_amount = 20
        with ThreadPoolExecutor(threads_amount) as worker:
            results = [res for res in worker.map(check_target, [_ for _ in range(threads_amount)])]
        for res in results:
            self.assertTrue(res)

    def test_get_all_sources_info(self):
        params = {'method': 'info'}
        infos: dict = httpx.get('http://localhost:%s/targets' % PORT, params=params).json()
        print(infos)
        for info in infos.values():
            self.assertTrue(info['lang'] is not None)
            self.assertTrue(info['amount'] is not None)
