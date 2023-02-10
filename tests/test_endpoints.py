from unittest import TestCase

import httpx

from config import PORT


class TestEndpoints(TestCase):

    def test_status(self):
        resp = httpx.get('http://localhost:%s' % PORT)
        success = resp.status_code
        self.assertTrue(success < 400)
