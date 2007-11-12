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

    def test_ignore_true(self):
        class DummyAuth(hatena.api.Auth):
            host = "non-host"
        self.api = DummyAuth("spam", "bacon")
        self.assertEqual(False, self.api.login("egg").is_valid())
        self.assertEqual(None, self.api.login("egg").has_error)
        self.assertEqual('', self.api.login("egg").error["message"])

    def test_ignore_false(self):
        class DummyAuth(hatena.api.Auth):
            host = "non-host"
        self.api = DummyAuth("spam", "bacon", ignore=False)
        self.assertRaises(Exception, self.api.login, "egg")

    def test_login_failure(self):
        self.api._get_auth_as_json = lambda cert: dict(
            has_error = True,
            error = dict(
                message ="Invalid signature",
            ),
        )
        self.assertEqual(False, self.api.login("invalidfrob").is_valid())
        self.assertEqual("Invalid signature", self.api.errstr)

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
        self.assertEqual(True, result.is_valid())
        self.assertTrue(isinstance(result, hatena.api.auth.ResultDict))
        self.assertEqual(result.user.get("name"), "naoya")
        self.assertEqual(result.user.get("image_url"),
            "http://www.hatena.ne.jp/users/na/naoya/profile.gif")
        self.assertEqual(result.user.get("thumbnail_url"),
            "http://www.hatena.ne.jp/users/na/naoya/profile_s.gif")

    def test_realtest(self):
        if not self.realtest:
            return
        self.setApi(self.api_key, self.secret)
        result = self.api.login(self.cert)
        self.assertEqual(False, result.has_error)
        self.assertEqual([u'thumbnail_url', u'image_url', u'name'],
            result.user.keys())
        result = self.api.login("failure")
        self.assertEqual(True, result.has_error)
        self.assertEqual(u'Invalid cert', result.error["message"])

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
            print "URI to Login:\n %s\nCERT: " % api.uri_to_login() ,
            cert = sys.stdin.readline().strip()
        realtest = True
    else:
        realtest = False
    unittest.main()
