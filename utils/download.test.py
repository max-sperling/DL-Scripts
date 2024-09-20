from utils import download

import unittest

class test_get_link_without_resource(unittest.TestCase):
    def test_without_resource(self):
        link = "https://example.com"
        expected = "https://example.com"
        self.assertEqual(download.get_link_without_resource(link), expected)

    def test_with_filename(self):
        link = "https://example.com/path/index.html"
        expected = "https://example.com/path"
        self.assertEqual(download.get_link_without_resource(link), expected)

class test_get_resource_without_webargs(unittest.TestCase):
    def test_without_resource(self):
        link = "https://example.com"
        expected = ""
        self.assertEqual(download.get_resource_without_webargs(link), expected)

    def test_with_resource_and_webargs(self):
        link = "https://example.com/path/index.html?param1=value1&param2=value2"
        expected = "index.html"
        self.assertEqual(download.get_resource_without_webargs(link), expected)

class test_get_resource_with_webargs(unittest.TestCase):
    def test_without_resource(self):
        link = "https://example.com"
        expected = ""
        self.assertEqual(download.get_resource_with_webargs(link), expected)

    def test_with_resource_and_webargs(self):
        link = "https://example.com/path/index.html?param1=value1&param2=value2"
        expected = "index.html?param1=value1&param2=value2"
        self.assertEqual(download.get_resource_with_webargs(link), expected)

if __name__ == '__main__':
    unittest.main()
