import urllib.parse

STANDARD_URLS = {
    rdf: "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    rdfs: "http://www.w3.org/2000/01/rdf-schema#",
    xsd: "http://www.w3.org/2001/XMLSchema#",
    owl: "http://www.w3.org/2002/07/owl#",
    tcs: "http://terminusdb.com/schema/tcs#",
    xdd: "http://terminusdb.com/schema/xdd#",
    v: "http://terminusdb.com/woql/variable/",
    terminus: "http://terminusdb.com/schema/terminus#",
    vio: "http://terminusdb.com/schema/vio#",
}


def encode_uri_component(value):
    return urllib.parse.urlencode(value, doseq=True)


def uri_encode_payload(self, payload):
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

    return "&".join(payloadArr)


def add_params_to_url(self, url, payload):
    if payload:
        params = self.URIEncodePayload(payload)
        if params:
            url = "{}?{}".format(url, params)
    return url


# below are utils for WOQLQuery


def add_namespaces_to_variable(self, var):
    if var[:2] != "v:":
        return "v:" + var
    return var


def add_namespaces_to_variables(self, vars):
    nvars = []
    for v_item in vars:
        nvars.append(self.addNamespacesToVariable(v_item))
    return nvars
