from optparse import OptionParser
from urllib import urlencode, urlopen
from urlparse import urlparse
import cgi
import sys
import unittest

import hatena


class Test(unittest.TestCase):
    def __init__(self, *argv, **kwargv):
        super(Test, self).__init__(*argv, **kwargv)
        self.api_key = api_key
        self.secret = secret
        self.cert = cert
        self.realtest = realtest

    def setApi(self, *argv):
        self.api = hatena.api.Auth(*argv)

    def setUp(self):
        self.setApi("test", "hoge")

    def test_api_sig(self):
        self.assertEqual("8d03c299aa049c9e47e4f99e03f2df53",
            self.api.api_sig(api_key="test"))

    def test_login_failure(self):
        self.assertEqual(False, bool(self.api.login("invalidfrob")))
        self.assertEqual("Invalid API key", self.api.errstr)

    def test_login_success(self):
        self.api._get_auth_as_json = lambda cert: dict(
            has_error = False,
            user = dict(
                name = "naoya",
                image_url = "http://www.hatena.ne.jp/users/na/naoya/profile.gif",
                thumbnail_url = "http://www.hatena.ne.jp/users/na/naoya/profile_s.gif",
            ),
        )
        result = self.api.login(cert="dummy_frob")
        self.assertTrue(bool(result))
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["user"].get("name"), "naoya")
        self.assertEqual(result["user"].get("image_url"),
            "http://www.hatena.ne.jp/users/na/naoya/profile.gif")
        self.assertEqual(result["user"].get("thumbnail_url"),
            "http://www.hatena.ne.jp/users/na/naoya/profile_s.gif")

    def test_realtest(self):
        if not self.realtest:
            return
        self.setApi(self.api_key, self.secret)
        self.assertEqual("", self.api.login(self.cert))

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
        self.assertEqual(['api_sig', 'api_key', 'bar', 'foo'],
            query.keys())


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--realtest", dest="api_keys", default="")
    options, args = parser.parse_args()
    api_key, secret, cert = ("%s::" % options.api_keys).split(":")[:3]
    import sys
    if dict(enumerate(sys.argv)).get(1) == "--realtest":
        argv = list((sys.argv[0],))
        argv.extend(sys.argv[3:])
        sys.argv = argv
        if not secret:
            print "SECRET: ",
            secret = sys.stdin.readline().strip()
        if not cert:
            api = hatena.api.Auth(api_key=api_key, secret=secret)
            print "URI to Login: %s\nCERT: " % api.uri_to_login() ,
            cert = sys.stdin.readline().strip()
        realtest = True
    else:
        realtest = False
    unittest.main()
