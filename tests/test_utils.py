import unittest

import settings
import utils


class TestArchiveFile(unittest.TestCase):

    def test_archive(self):
        archive_dir = settings.ARCHIVE_DIR
        test_file = settings.TEST_DIR.joinpath('test.txt')
        if not test_file.exists():
            with open(test_file, 'w') as f:
                f.write('this is test file')
        file = utils.archive_file(test_file, archive_dir)

        self.assertTrue(file.exists(), 'archive file does not exist')
        self.assertFalse(test_file.exists(), 'test_file was not delete')


class TestGetBaseSettings(unittest.TestCase):
    def test_get_settings(self):
        base_settings = utils.get_base_settings()

        self.assertIsInstance(base_settings, utils.BaseSettings)


class TestGetLatviaSettings(unittest.TestCase):
    def test_get_latvia_settings(self):
        lat_settings = utils.get_latvia_settings()

        self.assertIsInstance(lat_settings, utils.LatSettings)


if __name__ == '__main__':
    unittest.main()
