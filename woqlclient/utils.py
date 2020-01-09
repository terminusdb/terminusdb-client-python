import urllib.parse


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def encodeURIComponent(value):
        return urllib.parse.urlencode(value, doseq=True)

    @classmethod
    def URIEncodePayload(self, payload):
        if isinstance(payload, str):
            return self.encodeURIComponent(payload)
        payloadArr = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                """
                    if dictionary inside dictionary
                """
                if isinstance(value, dict):
                    # for keyElement,valueElement in value.items():
                    payloadArr.append(self.encodeURIComponent(value))
                else:
                    payloadArr.append(self.encodeURIComponent({key: value}))

        return '&'.join(payloadArr)

    @classmethod
    def addParamsToUrl(self, url, payload):
        if (payload):
            params = self.URIEncodePayload(payload)
            if (params):
                url = ('%s?%s' % (url, params))
        return url

    # below are utils for WOQLQuery

    @classmethod
    def addNamespacesToVariable(self, v):
        if (v[:2] != "v:"):
            return "v:" + v
        return v

    @classmethod
    def addNamespacesToVariables(self, vars):
        nvars = []
        for v in vars:
            nvars.append(self.addNamespacesToVariable(v))
        return nvars
