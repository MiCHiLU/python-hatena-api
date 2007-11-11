import md5
from urllib import urlencode, urlopen
from urlparse import urlunparse

try:
    import simplejson
except ImportError:
    raise Warning('Require simplejson. \
                    http://cheeseshop.python.org/pypi/simplejson')


class Auth(object):
    api_path = "/api/auth.json"
    errstr = None
    host = "auth.hatena.ne.jp"
    path = "/auth"
    schema = "http"

    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    def _booleanize(self, obj):
        class Dict(dict):
            def __nonzero__(self):
                return not self["has_error"]
        result = Dict()
        result.update(obj)
        return result

    def _get_auth_as_json(self, **kwargv):
        return simplejson.loads(
            urlopen(self.build_uri(self.api_path, **kwargv)).read())

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

    def build_uri(self, path, **kwargv):
        query = dict(
            api_key = self.api_key,
            api_sig = self.api_sig(**kwargv),
        )
        query.update(kwargv)
        params = fragment = ""
        return urlunparse((self.schema, self.host, path, params,
            urlencode(query), fragment))

    def login(self, cert):
        result = self._booleanize(self._get_auth_as_json(cert=cert))
        if not result:
            self.errstr = result["error"]["message"]
        return result

    def uri_to_login(self, **kwargv):
        return self.build_uri(self.path, **kwargv)
