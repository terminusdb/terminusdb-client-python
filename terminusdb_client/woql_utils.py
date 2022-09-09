import json
from datetime import datetime

from .errors import DatabaseError


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

def _args_as_payload(args: dict) -> dict:
    return { k: v for k,v in args.items() if v }

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
