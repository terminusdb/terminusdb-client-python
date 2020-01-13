# idParser.py

from .errorMessage import ErrorMessage
from .errors import (InvalidURIError)
import re


class IDParser:

    def __init__(self):
        self.__server_url = False
        self.__db = False
        self.__doc = False

    def resetDocument(self):
        self.__doc = False

    def resetDBID(self):
        self.__db = False
        self.__doc = False

    def resetServer(self):
        self.__server_url = False
        self.__db = False
        self.__doc = False

    @property
    def serverURL(self):
        if self.__server_url is False:
            raise InvalidURIError(ErrorMessage.getInvalidURIMessage(
                "Undefined", "Get Server URL"))
        return self.__server_url

    @property
    def dbID(self):
        if self.__db is False:
            raise InvalidURIError(ErrorMessage.getInvalidURIMessage(
                "Undefined", "TerminusDB Id"))
        return self.__db

    @property
    def docID(self):
        return self.__doc

    def dbURL(self):
        return self.serverURL + self.dbID

    def schemaURL(self):
        return self.dbURL() + '/schema'

    def queryURL(self):
        return self.dbURL() + '/woql'

    def frameURL(self):
        return self.dbURL() + '/frame'

    def docURL(self):
        doc = ''
        if self.docID:
            doc = self.docID
        return self.dbURL() + '/document/' + doc

    def parseServerURL(self, strURL):
        self.resetServer()

        if (self.validURL(strURL)):
            self.__server_url = strURL
        else:
            raise InvalidURIError(
                ErrorMessage.getInvalidURIMessage(strURL, "Parse ServerURL"))
        # add / at the  end of the URL
        if (self.__server_url.rfind('/') != (len(self.__server_url) - 1)):
            self.__server_url = self.__server_url + '/'

    def parseDBURL(self, dbFullUrl):
        if self.validURL(dbFullUrl):
            lastPos = dbFullUrl.rfind('/')
            if (lastPos == (len(dbFullUrl) - 1)):
                # trim trailing slash
                dbFullUrl = dbFullUrl[0:(len(dbFullUrl) - 1)]

            serverUrl = dbFullUrl[0:lastPos]
            dbid = dbFullUrl[(lastPos + 1):]
            self.parseServerURL(serverUrl)
        else:
            raise InvalidURIError(ErrorMessage.getInvalidURIMessage(
                dbFullUrl, "Parse TerminusDB Full URL"))
        self.parseDBID(dbid)

    # @param {string} str Terminus server URI or a TerminusID or None

    def parseDBID(self, strDBID):
        self.resetDBID()
        if (self.validIDString(strDBID)):
            self.__db = strDBID
        else:
            raise InvalidURIError(
                ErrorMessage.getInvalidURIMessage(strDBID, "Parse DBID"))

    # @param {string} docName Terminus Document URL or Terminus Document ID

    def parseDocumentID(self, docID):
        self.resetDocument()
        if (self.validIDString(docID)):
            self.__doc = docID
        else:
            raise InvalidURIError(ErrorMessage.getInvalidURIMessage(
                docID, "Parse Terminus Document ID"))

    """
        :param {string} preURL is a valid perfix in the context like doc:document
        :param {dict} context
        return the namespace URI from the context
    """

    @classmethod
    def validPrefixedURL(cls, preURL, context):
        if isinstance(preURL, str) is False:
            return False
        parts = preURL.split(':')
        if (len(parts) != 2):
            return False
        if (len(parts[0]) < 1 or len(parts[1]) < 1):
            return False
        if (context.get(parts[0]) and cls.validIDString(parts[1])):
            return parts[1]
        return False

    @staticmethod
    def validIDString(strID):
        if isinstance(strID, str) is False:
            return False

        regex = re.compile(r'[\s\t\r\n\f\/\:]+$', re.IGNORECASE)

        if re.search(regex, strID) is None:
            return True
        return False

    @staticmethod
    def validURL(strURL):
        if isinstance(strURL, str) is False:
            return False
        regex = re.compile(
            r'^(?:http)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, strURL) is not None:
            return True
        return False
