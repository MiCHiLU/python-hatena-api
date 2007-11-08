import md5


class Auth(object):
    host = "auth.hatena.ne.jp"
    path = "auth"
    schema = "http"

    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    def api_sig(self, api_key=None, **kwargv):
        api_key = api_key or self.api_key

        sig_dict = dict(
            api_key = api_key,
        )
        sig_dict.update(**kwargv)
        sig_keys = sig_dict.keys()
        sig_keys.sort()

        sig_list = list()
        for key in sig_keys:
            sig_list.extend((
                key,
                sig_dict[key],
            ))
        sig_string = "".join(sig_list)

        m = md5.new()
        m.update("%s%s" % (
            self.secret,
            sig_string,
        ))
        return m.hexdigest()

    def uri_to_login(self, **kwargv):
        query = dict(
            api_key = self.api_key,
            api_sig = self.api_sig(**kwargv),
            secret = self.secret,
        )
        query.update(**kwargv)
        query_string = "&".join(["%s=%s" % (key, value)
            for key, value in query.items()])
        return "%s://%s/%s?%s" % \
            (self.schema, self.host, self.path, query_string)
