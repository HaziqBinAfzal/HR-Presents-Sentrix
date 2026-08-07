import unittest

from config import Config


class EmailConfigurationTests(unittest.TestCase):
    def test_mail_defaults_are_well_formed(self):
        self.assertIsInstance(Config.MAIL_SERVER, str)
        self.assertTrue(Config.MAIL_SERVER)
        self.assertIsInstance(Config.MAIL_PORT, int)
        self.assertGreater(Config.MAIL_PORT, 0)
        self.assertIsInstance(Config.PASSWORD_RESET_MAX_AGE, int)
        self.assertGreater(Config.PASSWORD_RESET_MAX_AGE, 0)


if __name__ == "__main__":
    unittest.main()
