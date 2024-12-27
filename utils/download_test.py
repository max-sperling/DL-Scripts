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

class test_find_url_overlap(unittest.TestCase):
    def test_with_nothing_same(self):
        url1 = "https://example1.com/dir1/file.m3u8"
        url2 = "https://example2.com/dir2/file_1.ts"
        self.assertEqual(download.find_url_overlap(url1, url2), download.URL_Overlap.NONE)

    def test_with_same_base_1(self):
        url1 = "https://example.com/dir1/file.m3u8"
        url2 = "https://example.com/dir2/file_1.ts"
        self.assertEqual(download.find_url_overlap(url1, url2), download.URL_Overlap.BASE)

    def test_with_same_base_2(self):
        url1 = "https://example.com/dir1/file.m3u8"
        url2 = "/dir2/file_1.ts"
        self.assertEqual(download.find_url_overlap(url1, url2), download.URL_Overlap.BASE)

    def test_with_same_base_dirs_1(self):
        url1 = "https://example.com/dir/file.m3u8"
        url2 = "https://example.com/dir/file_1.ts"
        self.assertEqual(download.find_url_overlap(url1, url2), download.URL_Overlap.DIRS)

    def test_with_same_base_dirs_2(self):
        url1 = "https://example.com/dir/file.m3u8"
        url2 = "/dir/file_1.ts"
        self.assertEqual(download.find_url_overlap(url1, url2), download.URL_Overlap.DIRS)

    def test_with_same_base_dirs_3(self):
        url1 = "https://example.com/dir/file.m3u8"
        url2 = "file_1.ts"
        self.assertEqual(download.find_url_overlap(url1, url2), download.URL_Overlap.DIRS)

if __name__ == '__main__':
    unittest.main()
