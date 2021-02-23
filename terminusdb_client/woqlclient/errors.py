class Error(Exception):
    """Exception that is base class for all other error exceptions."""

    def __init__(self, msg=None, url=None, err_obj=None):
        super().__init__()
        self.msg = msg
        self.url = url
        self.errorObj = err_obj

    def __str__(self):
        return self.msg


class InterfaceError(Error):
    """Exception for errors related to the interface."""

    def __init__(self, message):
        self.message = message


class DatabaseError(Error):
    """Exception for errors related to the database."""


class AccessDeniedError(DatabaseError):
    pass


class APIError(DatabaseError):
    """Exceptions to do with return messages from HTTP"""

    def __init__(self, msg=None, url=None, err_obj=None, status_code=None):
        super().__init__()
        self.msg = msg
        self.url = url
        self.errorObj = err_obj
        self.status_code = status_code


class InvalidURIError(Error):
    pass
