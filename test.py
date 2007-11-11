import unittest
from urlparse import urlparse
import cgi

import hatena


class Test(unittest.TestCase):
    api = hatena.api.Auth(
        api_key = "test",
        secret = "hoge",
    )

    def test_api_sig(self):
        self.assertEqual("8d03c299aa049c9e47e4f99e03f2df53",
            self.api.api_sig(api_key="test"))

    def test_uri_to_login(self):
        self.assertEqual("auth.hatena.ne.jp",
            urlparse(self.api.uri_to_login())[1])
        self.assertEqual("8d03c299aa049c9e47e4f99e03f2df53",
            cgi.parse_qs(
                urlparse(self.api.uri_to_login())[4]).get("api_sig")[0]
            )

        query = cgi.parse_qs(
            urlparse(self.api.uri_to_login(foo="bar"))[4]
        )
        self.assertEqual("59d7fb76ceeacc8850ccd2428fd2b0f0",
            query.get("api_sig")[0])
        self.assertEqual("bar", query.get("foo")[0])

        query = cgi.parse_qs(
            urlparse(self.api.uri_to_login(foo="bar", bar="baz"))[4]
        )
        self.assertEqual("c166e2ea4984224375a88e080cd7cce6",
            query.get("api_sig")[0])
        self.assertEqual("bar", query.get("foo")[0])
        self.assertEqual("baz", query.get("bar")[0])


if __name__ == "__main__":
    unittest.main()
