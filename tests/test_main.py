from unittest import TestCase
from main import create_parser


class TestMain(TestCase):

    def setUp(self):
        self.parser = create_parser()

    def test_countre_argument(self):
        args = ['--country', ['test_country']]

        with self.assertRaises(SystemExit):
            self.parser.parse_args(args)
