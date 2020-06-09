# errorMessage.py


class ErrorMessage:
    def __init__(self):
        pass

    @staticmethod
    def get_error_as_message(url, api, err):
        message = "Code: " + str(err["status"])
        if "body" in err:
            message += ", Message: " + err["body"]
        if "action" in err:
            message += ", Action: " + err["action"]
        if "type" in err:
            message += ", Type: " + err["type"]
        if url:
            message += ", url: " + url
        if api and "method" in api:
            message += ", method: " + api["method"]
        return message

    @staticmethod
    def access_denied_err_obj(action, db, server):
        err = {}
        err["status"] = 403
        err["url"] = (server or "") + (db or "")
        err["type"] = "client"
        err["action"] = action
        err["body"] = err["action"] + " not permitted for" + err["url"]
        return err

    @classmethod
    def get_api_error_message(cls, url, api, err):
        return "API Error" + cls.get_error_as_message(url, api, err)

    @classmethod
    def get_access_denied_message(cls, action, dbid, server):
        error_obj = cls.access_denied_err_obj(action, dbid, server)
        return "Access Denied" + cls.get_error_as_message(None, None, error_obj)

    @staticmethod
    def get_invalid_key_message(extra_message=""):
        message = "The Api KEY is Undefined " + extra_message
        return message

    @staticmethod
    def get_invalid_url_message(url, call):
        message = "Invalid argument to {}, {} is not a valid Terminus DB API endpoint".format(
            url, call
        )
        return message
