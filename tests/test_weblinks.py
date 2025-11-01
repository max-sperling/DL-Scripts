from utils import weblinks

import unittest

class test_url_is_file(unittest.TestCase):
    def test_for_file_with_suffix(self):
        link = "https://example.com/dir/file.ts"
        self.assertTrue(weblinks.url_is_file(link))

    def test_for_file_without_suffix(self):
        link = "https://example.com/dir/file"
        self.assertTrue(weblinks.url_is_file(link))

    def test_for_folder_with_suffix(self):
        link = "https://example.com/dir.ts/"
        self.assertFalse(weblinks.url_is_file(link))

    def test_for_folder_without_suffix(self):
        link = "https://example.com/dir/"
        self.assertFalse(weblinks.url_is_file(link))

class test_get_url_base(unittest.TestCase):
    def test_without_path_and_arg(self):
        link = "https://example.com/"
        expected = "https://example.com"
        self.assertEqual(weblinks.get_url_base(link), expected)

    def test_with_path_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "https://example.com"
        self.assertEqual(weblinks.get_url_base(link), expected)

class test_get_url_base_dirs(unittest.TestCase):
    def test_without_file_and_arg(self):
        link = "https://example.com/dir/"
        expected = "https://example.com/dir"
        self.assertEqual(weblinks.get_url_base_dirs(link), expected)

    def test_with_file_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "https://example.com/dir"
        self.assertEqual(weblinks.get_url_base_dirs(link), expected)

class test_get_url_file(unittest.TestCase):
    def test_without_extension_and_arg(self):
        link = "https://example.com/dir/file"
        expected = "file"
        self.assertEqual(weblinks.get_url_file(link), expected)

    def test_with_extension_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "file.ts"
        self.assertEqual(weblinks.get_url_file(link), expected)

    def test_for_folder(self):
        link = "https://example.com/dir/"
        expected = ""
        self.assertEqual(weblinks.get_url_file(link), expected)

class test_get_url_file_args(unittest.TestCase):
    def test_without_extension_and_arg(self):
        link = "https://example.com/dir/file"
        expected = "file"
        self.assertEqual(weblinks.get_url_file_args(link), expected)

    def test_with_extension_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "file.ts?param1=value1"
        self.assertEqual(weblinks.get_url_file_args(link), expected)

    def test_for_folder(self):
        link = "https://example.com/dir/?param1=value1"
        expected = "?param1=value1"
        self.assertEqual(weblinks.get_url_file_args(link), expected)

class test_get_url_path_args(unittest.TestCase):
    def test_without_extension_and_arg(self):
        link = "https://example.com/dir/file"
        expected = "/dir/file"
        self.assertEqual(weblinks.get_url_path_args(link), expected)

    def test_with_extension_and_arg(self):
        link = "https://example.com/dir/file.ts?param1=value1"
        expected = "/dir/file.ts?param1=value1"
        self.assertEqual(weblinks.get_url_path_args(link), expected)

class test_url_join(unittest.TestCase):
    def test_with_nothing_same(self):
        url_1 = "https://example1.com/dir1/file.m3u8"
        url_2 = "https://example2.com/dir2/file_1.ts"
        url_res = "https://example2.com/dir2/file_1.ts"
        self.assertEqual(weblinks.join_url(url_1, url_2), url_res)

    def test_with_same_base_abs(self):
        url_1 = "https://example.com/dir1/file.m3u8"
        url_2 = "https://example.com/dir2/file_1.ts"
        url_res = "https://example.com/dir2/file_1.ts"
        self.assertEqual(weblinks.join_url(url_1, url_2), url_res)

    def test_with_same_base_rel(self):
        url_1 = "https://example.com/dir1/file.m3u8"
        url_2 = "/dir2/file_1.ts"
        url_res = "https://example.com/dir2/file_1.ts"
        self.assertEqual(weblinks.join_url(url_1, url_2), url_res)

    def test_with_same_base_dirs_abs(self):
        url_1 = "https://example.com/dir/file.m3u8"
        url_2 = "https://example.com/dir/file_1.ts"
        url_res = "https://example.com/dir/file_1.ts"
        self.assertEqual(weblinks.join_url(url_1, url_2), url_res)

    def test_with_same_base_dirs_rel_1(self):
        url_1 = "https://example.com/dir/file.m3u8"
        url_2 = "/dir/file_1.ts"
        url_res = "https://example.com/dir/file_1.ts"
        self.assertEqual(weblinks.join_url(url_1, url_2), url_res)

    def test_with_same_base_dirs_rel_2(self):
        url_1 = "https://example.com/dir/file.m3u8"
        url_2 = "file_1.ts"
        url_res = "https://example.com/dir/file_1.ts"
        self.assertEqual(weblinks.join_url(url_1, url_2), url_res)

if __name__ == '__main__':
    unittest.main()
