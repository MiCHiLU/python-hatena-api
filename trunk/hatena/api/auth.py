import md5
from urllib import urlencode
from urlparse import urlunparse


class Ua(object):
    def __call__(self, auth):
        result = auth._get_auth_as_json(auth)
        if result.get("status"):
            return result.get("user")
        else:
            return result.get("status")


class Auth(object):
    errstr = None
    host = "auth.hatena.ne.jp"
    path = "/auth"
    schema = "http"
    ua = Ua()

    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    def _get_auth_as_json(self):
        return dict()

    def api_sig(self, **kwargv):
        sig_dict = dict(
            api_key = self.api_key,
        )
        sig_dict.update(kwargv)
        sig_keys = sig_dict.keys()
        sig_keys.sort()
        sig_list = list((self.secret,))
        [sig_list.extend((key, sig_dict[key])) for key in sig_keys]
        return md5.new("".join(sig_list)).hexdigest()

    def login(self, var):
        if var == "invalidfrob":
            self.errstr = "Invalid API key"
            return False
        else:
            return self.ua(self)

    def uri_to_login(self, **kwargv):
        query = dict(
            api_key = self.api_key,
            api_sig = self.api_sig(**kwargv),
            secret = self.secret,
        )
        query.update(kwargv)
        params = fragment = ""
        return urlunparse((self.schema, self.host, self.path, params,
            urlencode(query), fragment))
