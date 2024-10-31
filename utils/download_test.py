from utils import download

import unittest

class test_get_url_base(unittest.TestCase):
    def test_without_path_and_arg(self):
        link = "https://example.com/"
        expected = "https://example.com"
        self.assertEqual(download.get_url_base(link), expected)

    def test_with_path_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "https://example.com"
        self.assertEqual(download.get_url_base(link), expected)

class test_get_url_base_dirs(unittest.TestCase):
    def test_without_file_and_arg(self):
        link = "https://example.com/dir/"
        expected = "https://example.com/dir"
        self.assertEqual(download.get_url_base_dirs(link), expected)

    def test_with_file_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "https://example.com/dir"
        self.assertEqual(download.get_url_base_dirs(link), expected)

class test_get_url_file(unittest.TestCase):
    def test_without_extension_and_arg(self):
        link = "https://example.com/dir/file"
        expected = "file"
        self.assertEqual(download.get_url_file(link), expected)

    def test_with_extension_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "file.ts"
        self.assertEqual(download.get_url_file(link), expected)

class test_get_url_file_args(unittest.TestCase):
    def test_without_extension_and_arg(self):
        link = "https://example.com/dir/file"
        expected = "file"
        self.assertEqual(download.get_url_file_args(link), expected)

    def test_with_extension_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "file.ts?param1=value1"
        self.assertEqual(download.get_url_file_args(link), expected)

class test_get_url_path_args(unittest.TestCase):
    def test_without_extension_and_arg(self):
        link = "https://example.com/dir/file"
        expected = "/dir/file"
        self.assertEqual(download.get_url_path_args(link), expected)

    def test_with_extension_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "/dir/file.ts?param1=value1"
        self.assertEqual(download.get_url_path_args(link), expected)

if __name__ == '__main__':
    unittest.main()
