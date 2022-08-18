import unittest
import settings

from utils import archive_file


class TestArchiveFile(unittest.TestCase):

    def test_archive(self):
        archive_dir = settings.ARCHIVE_DIR
        test_file = settings.TEST_DIR.joinpath('test.txt')
        if not test_file.exists():
            with open(test_file, 'w') as f:
                f.write('this is test file')
        file = archive_file(test_file, archive_dir)
        
        self.assertTrue(file.exists(), 'archive file does not exist')
        self.assertFalse(test_file.exists(), 'test_file was not delete')


if __name__ == '__main__':
    unittest.main()
