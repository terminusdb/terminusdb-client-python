# connectionConfig.py
from .idParser import IDParser


class ConnectionConfig:

    def __init__(self, params={}):
        self.__idParser = IDParser()

        """
          client configuration options - connected_mode = true
          tells the client to first connect to the server before invoking other services
        """
        self.__connected_mode = True
        # include a terminus:user_key API key in the calls
        self.__include_key = True
        # client side checking of access control (in addition to server-side access control)
        self.__checks_capabilities = True

        if 'server' in params:
            self.setServer(params['server'])
        if 'db' in params:
            self.setDB(params['db'])
        if 'doc' in params:
            self.setDocument(params['doc'])
        if 'connected_mode' in params and params['connected_mode'] is False:
            self.__connected_mode = False
        if 'include_key' in params and params['include_key'] is False:
            self.__include_key = False
        if 'checks_capabilities' in params and params['checks_capabilities'] is False:
            self.__checks_capabilities = False

    def deletedbID(self, dbName):
        if self.__idParser.dbID == dbName:
            self.__idParser.resetDBID()

    @property
    def serverURL(self):
        return self.__idParser.serverURL

    @property
    def dbID(self):
        return self.__idParser.dbID

    @property
    def connectedMode(self):
        return self.__connected_mode

    @property
    def checkCapabilities(self):
        return self.__checks_capabilities

    @property
    def includeKey(self):
        return self.__include_key

    def schemaURL(self):
        return self.__idParser.schemaURL()

    def queryURL(self):
        return self.__idParser.queryURL()

    def frameURL(self):
        return self.__idParser.frameURL()

    def docURL(self):
        return self.__idParser.docURL()

    def dbURL(self, call=None):
        return self.__idParser.dbURL()

    """
      Utility functions for setting and parsing urls and determining
      the current server, database and document
    """

    def setServer(self, serverURL):
        self.__idParser.parseServerURL(serverURL)
    """
      @param {string} inputStr Terminus server URI or a TerminusID
    """

    def setDB(self, dbID):
        self.__idParser.parseDBID(dbID)

    def setDocument(self, documentID):
        self.__idParser.parseDocumentID(documentID)
