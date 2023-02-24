import unittest

from module import database, services, models


class TestServices(unittest.TestCase):

    def setUp(self) -> None:
        self.session = database.SessionLocal()

    def test_get_pool(self):

        source = 'turk'
        limit = 100

        pool = services.get_pool(self.session, source, limit)
        for email in pool:
            print(email)
            self.assertTrue(issubclass(models.Email, type(email)))

    def test_get_info(self):
        source = 'turk'
        info: dict = services.info(self.session, source)
        print(info)
        self.assertTrue(info['lang'] is not None)
        self.assertTrue(info['available'] is not None)

    def test_pop_email_from_db(self):
        source = 'turk'

        for _ in range(20):
            email = services.get_email_from_pool(self.session, source)
            self.assertTrue(issubclass(models.Email, type(email)))
