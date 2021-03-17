class Error(Exception):
    """Exception that is base class for all other error exceptions.

    """

    def __init__(self, msg=None, url=None, err_obj=None):
        super().__init__()
        self.msg = msg
        self.url = url
        self.error_obj = err_obj

    def __str__(self):
        return self.msg


class InterfaceError(Error):
    """Exception for errors related to the interface."""

    def __init__(self, message):
        self.message = message


class DatabaseError(Error):
    """Exception for errors related to the database."""
    def __init__(self, reponse=None):
        super().__init__()
        if reponse.headers['content-type'][len()"application/json"):] == "application/json":
            self.error_obj = reponse.json()
            if self.error_obj.get(["api:message"]):
                self.msg = self.error_obj["api:message"]
            elif self.error_obj.get(["vio:message"]):
                self.msg = self.error_obj["vio:message"]
            else:
                self.msg = "Unknown Error: check DatabaseError.error_obj for details"
        else:
            self.error_obj =None
            self.msg = reponse.text
        self.status_code = reponse.status_code

    def __str__():
        return self.msg

class OperationalError(DatabaseError):
    """Exception for operational errors related to the database."""


class AccessDeniedError(DatabaseError):
    pass


class APIError(DatabaseError):
    """Exceptions to do with return messages from HTTP"""

    def __init__(self, msg=None, url=None, err_obj=None, status_code=None):
        super().__init__()
        self.msg = msg
        self.url = url
        self.error_obj = err_obj
        self.status_code = status_code


class InvalidURIError(Error):
    pass
