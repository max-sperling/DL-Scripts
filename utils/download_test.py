from utils import download

import unittest

class test_get_url_file(unittest.TestCase):
    def test_without_extension(self):
        link = "https://example.com/path/file"
        expected = "file"
        self.assertEqual(download.get_url_file(link), expected)

    def test_with_arguments(self):
        link = "https://example.com/path/file.txt?param1=value1"
        expected = "file.txt"
        self.assertEqual(download.get_url_file(link), expected)

if __name__ == '__main__':
    unittest.main()
