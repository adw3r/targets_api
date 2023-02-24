import unittest

from module import services, models


class TestServices(unittest.TestCase):

    def setUp(self) -> None:
        self.session = next(services.get_db())
        self.source = 'test'
        self.limit = 10000

    def test_get_info(self):
        info: dict = services.info(self.session, self.source)
        print(info)
        self.assertTrue(info['lang'] is not None)
        self.assertTrue(info['amount'] is not None)

    def test_get_pool(self):
        pool = services.get_pool(self.session, self.source, self.limit)
        for email in pool:
            print(email)
            self.assertTrue(issubclass(models.Email, type(email)))

    def test_get_all_sources_info(self):
        infos: dict = services.get_all_sources_info(self.session)
        for info in infos.values():
            self.assertTrue(info['lang'] is not None)
            self.assertTrue(info['amount'] is not None)

    def test_pop_email_from_db(self):
        for _ in range(10):
            email = services.get_available_email_from_pool(self.session, self.source)
            print(email)
            self.assertTrue(issubclass(models.Email, type(email)))

    def test_get_all_emails(self):
        emails = services.get_all_available_emails(self.session, self.source)
        print(emails)
