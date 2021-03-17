class Error(Exception):
    """Exception that is base class for all other error exceptions."""

    def __init__(self):
        super().__init__()


class InterfaceError(Error):
    """Exception for errors related to the interface.

    Attributes
    ----------
    message  : str
        Error message.

    """

    def __init__(self, message):
        self.message = message


class DatabaseError(Error):
    """Exception for errors related to the database.

    Attributes
    ----------
    message  : str
        Error message.
    error_obj : dict
        Whole error object in json format
    status_code : int
        status_code from the request.Response
    """

    def __init__(self, reponse=None):
        """Exception for errors related to the database.

        Parameters
        ----------
        reponse : request.Response
            response from the api call
        """
        super().__init__()
        if (
            reponse.headers["content-type"][len("application/json") :]
            == "application/json"
        ):
            self.error_obj = reponse.json()
            if self.error_obj.get(["api:message"]):
                self.message = self.error_obj["api:message"]
            elif self.error_obj.get(["vio:message"]):
                self.message = self.error_obj["vio:message"]
            else:
                self.message = (
                    "Unknown Error: check DatabaseError.error_obj for details"
                )
        else:
            self.error_obj = None
            self.message = reponse.text
        self.status_code = reponse.status_code

    def __str__(self):
        return self.message


class OperationalError(DatabaseError):
    """Exception for operational errors related to the database."""


class AccessDeniedError(DatabaseError):
    pass


class APIError(DatabaseError):
    """Exceptions to do with return messages from HTTP

    Attributes
    ----------
    message  : str
        Error message.
    error_obj : dict
        Whole error object in json format
    status_code : int
        status_code from the request.Response
    url : str
        url causeing the Error
    """

    def __init__(self, message=None, url=None, err_obj=None, status_code=None):
        """Exceptions to do with return messages from HTTP

        Parameters
        ----------
        message  : str
            Error message.
        error_obj : dict
            Whole error object in json format
        status_code : int
            status_code from the request.Response
        url : str
            url causeing the Error
        """
        super().__init__()
        self.message = message
        self.url = url
        self.error_obj = err_obj
        self.status_code = status_code


class InvalidURIError(Error):
    pass
