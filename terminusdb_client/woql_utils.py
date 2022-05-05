import json
import urllib.parse
from datetime import datetime

from .errors import DatabaseError

STANDARD_URLS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "xdd": "http://terminusdb.com/schema/xdd#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "terminus": "http://terminusdb.com/schema/terminus#",
    "vio": "http://terminusdb.com/schema/vio#",
    "repo": "http://terminusdb.com/schema/repository#",
    "layer": "http://terminusdb.com/schema/layer#",
    "woql": "http://terminusdb.com/schema/woql#",
    "ref": "http://terminusdb.com/schema/ref#",
}


def encode_uri_component(value):
    """Encode a URI.

    Parameters
    ----------
    value: Value which needs to be encoded

    Returns
    -------
        Encoded Value
    """
    return urllib.parse.urlencode(value, doseq=True)


def uri_encode_payload(payload):
    """Encode the given payload

    Parameters
    ----------
    payload: dict

    Returns
    -------
        Encoded payload array
    """
    if isinstance(payload, str):
        return encode_uri_component(payload)
    payload_arr = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            """
            if dictionary inside dictionary
            """
            if isinstance(value, dict):
                # for keyElement,valueElement in value.items():
                payload_arr.append(encode_uri_component(value))
            else:
                payload_arr.append(encode_uri_component({key: value}))

    return "&".join(payload_arr)


def add_params_to_url(url, payload):
    """Add params / payload to given url

    Parameters
    ----------
    url: str
    payload: dict

    Returns
    -------
        Url with payload appended
    """
    if payload:
        params = uri_encode_payload(payload)
        if params:
            url = f"{url}?{params}"
    return url


# below are utils for WOQLQuery


def add_namespaces_to_variable(var):
    """Adds namespace to given variable

    Parameters
    ----------
    var: str
        Variable

    Returns
    -------
        Variable attached with namespace
    """
    if var[:2] != "v:":
        return "v:" + var
    return var


def add_namespaces_to_variables(variables):
    """Adds namespace to given variables

    Parameters
    ----------
    variables: list [str]

    Returns
    -------
        Variables attached with namespace
    """
    nvars = []
    for v_item in variables:
        nvars.append(add_namespaces_to_variable(v_item))
    return nvars


def empty(obj):
    """* is the object empty?
    * returns true if the json object is empty
    """
    if not obj:
        # Assume if it has a length property with a non-zero value
        # that that property is correct.
        return True
    if len(obj) > 0:
        return False
    if len(obj) == 0:
        return True
    # Otherwise, does it have any properties of its own?
    # if type(obj) == dict:
    #     for key in obj.keys():
    #         if hasattr(obj,key):
    #             return False
    return True


def shorten(url, prefixes=None):
    """Get shortened url

    Parameters
    ----------
    url: str
    prefixes: dict

    Returns
    -------
        Url with prefixes added and shortened
    """
    prefixes = prefixes if prefixes else STANDARD_URLS
    for pref, val in prefixes.items():
        short_url = url[: len(val)]
        if val == short_url:
            return f"{pref}:{short_url}"
    return url


def is_data_type(stype):
    """Checks if the given type is a datatype or not

    Parameters
    ----------
    stype: str

    Returns
    -------
    bool
    """
    sh = shorten(stype)
    if sh and (sh[:4] == "xsd:" or sh[:4] == "xdd:"):
        return True
    return False


def valid_url(string):
    """Checks if the given url is valid

    Parameters
    ----------
    string: str
        Url which needs to be validated

    Returns
    -------
    bool
    """
    if string and (string[:7] == "http://" or string[:8] == "https://"):
        return True
    return False


def url_fraqment(url):
    """Gets the url fragment

    Parameters
    ----------
    url: str

    Returns
    -------
    str
        url fragment

    """
    bits = url.split("#")
    if len(bits) > 1:
        return bits[1]
    return url


def label_from_url(url):
    """Get the label from url

    Parameters
    ----------
    url: str

    Returns
    -------
    str
        Label
    """
    nurl = url_fraqment(url)
    nurl = nurl if nurl else url
    last_char = nurl.rfind("/")
    if last_char < len(nurl) - 1:
        nurl = nurl[last_char + 1 :]
    nurl = nurl.replace("_", " ")
    return nurl[0].upper() + nurl[1:]


def _result2stream(result):
    """turning JSON string into a interable that give you a stream of dictionary"""
    decoder = json.JSONDecoder()

    idx = 0
    result_length = len(result)
    while True:
        if idx >= result_length:
            return
        data, offset = decoder.raw_decode(result[idx:])
        idx += offset
        while idx < result_length and result[idx].isspace():
            idx += 1
        yield data


def _finish_response(request_response, get_version=False):
    """Get the response text

    Parameters
    ----------
    request_response: Response Object

    Returns
    -------
    str
        Response text

    Raises
    ------
    DatabaseError
        For status codes 400 to 598

    """
    if request_response.status_code == 200:
        if get_version:
            return request_response.text, request_response.headers.get(
                "Terminusdb-Data-Version"
            )
        return request_response.text  # if not a json it raises an error
    elif request_response.status_code > 399 and request_response.status_code < 599:
        raise DatabaseError(request_response)


def _clean_list(obj):
    cleaned = []
    for item in obj:
        if isinstance(item, str):
            cleaned.append(item)
        elif hasattr(item, "items"):
            cleaned.append(_clean_dict(item))
        elif not isinstance(item, str) and hasattr(item, "__iter__"):
            cleaned.append(_clean_list(item))
        elif hasattr(item, "isoformat"):
            cleaned.append(item.isoformat())
        else:
            cleaned.append(item)
    return cleaned


def _clean_dict(obj):
    cleaned = {}
    for key, item in obj.items():
        if isinstance(item, str):
            cleaned[key] = item
        elif hasattr(item, "items"):
            cleaned[key] = _clean_dict(item)
        elif hasattr(item, "__iter__"):
            cleaned[key] = _clean_list(item)
        elif hasattr(item, "isoformat"):
            cleaned[key] = item.isoformat()
        else:
            cleaned[key] = item
    return cleaned


def _dt_list(obj):
    cleaned = []
    for item in obj:
        if isinstance(item, str):
            try:
                cleaned.append(datetime.fromisoformat(item))
            except ValueError:
                cleaned.append(item)
        elif hasattr(item, "items"):
            cleaned.append(_clean_dict(item))
        elif hasattr(item, "__iter__"):
            cleaned.append(_clean_list(item))
        else:
            cleaned.append(item)
    return cleaned


def _dt_dict(obj):
    cleaned = {}
    for key, item in obj.items():
        if isinstance(item, str):
            try:
                cleaned[key] = datetime.fromisoformat(item)
            except ValueError:
                cleaned[key] = item
        elif hasattr(item, "items"):
            cleaned[key] = _dt_dict(item)
        elif hasattr(item, "__iter__"):
            cleaned[key] = _dt_list(item)
        else:
            cleaned[key] = item
    return cleaned
