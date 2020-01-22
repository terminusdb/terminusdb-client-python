# woqlClient.py
from .dispatchRequest import DispatchRequest

#from .errorMessage import *
from .connectionConfig import ConnectionConfig
from .connectionCapabilities import ConnectionCapabilities

from .const import Const as const
from .errorMessage import ErrorMessage
#from .errors import (InvalidURIError)
from .errors import *

from .documentTemplate import DocumentTemplate

from .idParser import IDParser
import json

# WOQL client object
# license Apache Version 2
# summary Python module for accessing the Terminus DB API


class WOQLClient:

    def __init__(self, params={}):
        # current conCapabilities context variables
        key = params.get('key')
        self.conConfig = ConnectionConfig(params)
        self.conCapabilities = ConnectionCapabilities(self.conConfig, key)



    def connect(self, serverURL=None, key=None):
        """
        Connect to a Terminus server at the given URI with an API key
        Stores the terminus:ServerCapability document returned
        in the conCapabilities register which stores, the url, key, capabilities,
        and database meta-data for the connected server

        If the serverURL argument is omitted,
        self.conConfig.serverURL will be used if present
        or an error will be raise.

        Parameters
        ----------
        serverURL : str
            Terminus server URI
        key : str
            API key

        Returns
        -------
        dict or raise an InvalidURIError
        """
        if serverURL:
            self.conConfig.setServer(serverURL)

        if key:
            self.conCapabilities.setClientKey(key)

        jsonObj = self.dispatch(self.conConfig.serverURL, const.CONNECT, key)
        self.conCapabilities.addConnection(jsonObj)
        return jsonObj

    @staticmethod
    def directConnect(serverURL, key):
        """
        connect directly without create a new class instance

        Parameters
        ----------
        serverURL : str
            Terminus server URI
        key : str
            API key

        Returns
        -------
        dict or raise an InvalidURIError
        """
        idParser = IDParser()
        idParser.parseServerURL(serverURL)
        return DispatchRequest.sendRequestByAction(idParser.serverURL, const.CONNECT, key)

    def createDatabase(self, dbID, label, key=None, **kwargs):
        """
        Create a Terminus Database by posting
        a terminus:Database document to the Terminus Server

        Parameters
        ----------
        dbID : str
            TerminusDB id
        label : str
            Terminus label
        key : str, optional
            you can omit the key if you have set it before
        kwargs
            Optional arguments that ``createDatabase`` takes

        Returns
        -------
        dict
        """
        self.conConfig.setDB(dbID)
        createDBTemplate = DocumentTemplate.createDBTemplate(
            self.conConfig.serverURL, self.conConfig.dbID, label, **kwargs)
        #after create db the server could send back the capabilities of the new db, we can add the new capability at the
        #capabilities list
        return self.dispatch(self.conConfig.dbURL(), const.CREATE_DATABASE, key, createDBTemplate)

    @staticmethod
    def directCreateDatabase(dbURL, label, key, **kwargs):
        """Create Terminus Database with settings

        Parameters
        ----------
        dbURL : str
            TerminusDB full URL like http://localhost:6363/myDB
        label : str
            the terminus db title
        key : str
            the server API key
        kwargs
            Optional arguments that ``createDatabase`` takes

        Returns
        -------
        dict
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        createDBTemplate = DocumentTemplate.createDBTemplate(
            idParser.serverURL, idParser.dbID, label, **kwargs)
        DispatchRequest.sendRequestByAction(
            idParser.dbURL(), const.CREATE_DATABASE, key, createDBTemplate)

    def deleteDatabase(self, dbID, key=None):
        """Delete a TerminusDB

        Parameters
        ----------
        dbID : str
            terminusDB Id
        key : str, optional
            you need the key if you didn't set before

        Returns
        -------
        dict
        """
        self.conConfig.setDB(dbID)
        jsonResponse = self.dispatch(
            self.conConfig.dbURL(), const.DELETE_DATABASE, key)
        self.conCapabilities.removeDB()
        return jsonResponse

    @staticmethod
    def directDeleteDatabase(dbURL, key):
        """Delete a TerminusDB with settings

        Parameters
        ----------
        dbURL : str
            TerminusDB full URL like http://localhost:6363/myDB
        key : str
            the server API key
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        return DispatchRequest.sendRequestByAction(
            idParser.dbURL(), const.DELETE_DATABASE, key)

    def getSchema(self, dbID=None, key=None, options={"terminus:encoding": "terminus:turtle"}):
        """Retrieves the schema of the specified database

        opts.format defines which format is requested, default is turtle(*json / turtle)

        Parameters
        ----------
        dbId : str
            TerminusDB Id or omitted (get last select database)
        key : str
            the server API key
        options : dict
            options object

        Returns
        -------
        str or dict
        """
        if (dbID):
            self.conConfig.setDB(dbID)

        return self.dispatch(self.conConfig.schemaURL(), const.GET_SCHEMA, key, options)

    @staticmethod
    def directGetSchema(dbURL, key, options={"terminus:encoding": "terminus:turtle"}):
        """Retrieves the schema of the specified database with settings

        opts.format defines which format is requested, default is turtle(*json / turtle)

        Parameters
        ----------
        dbId : str
            TerminusDB Id or omitted (get last select database)
        key : str
            the server API key
        options : dict
            options object

        Returns
        -------
        str or dict
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        return DispatchRequest.sendRequestByAction(
            idParser.schemaURL(), const.GET_SCHEMA, key, options)

    def updateSchema(self, docObj, dbID=None, key=None, opts={"terminus:encoding": "terminus:turtle"}):
        """Updates the Schema of the specified database

        opts.format is used to specify which format is being used (*json / turtle)

        Parameters
        ----------
        docObj : dict
            valid owl ontology in json-ld or turtle format
        dbid : str
            TerminusDB Id or omitted
        key : str
            API key
        opts : dict
            options object

        Returns
        -------
        dict
        """
        if (dbID):
            self.conConfig.setDB(dbID)
        docObj = DocumentTemplate.formatDocument(
            docObj, False, opts)
        return self.dispatch(self.conConfig.schemaURL(), const.UPDATE_SCHEMA, key, docObj)

    @staticmethod
    def directUpdateSchema(dbURL, docObj, key, opt={"terminus:encoding": "terminus:turtle"}):
        """Updates the Schema of the specified database with settings

        opts.format is used to specify which format is being used (*json / turtle)

        Parameters
        ----------
        dbURL : str
            a valid TerminusDB full URL
        docObj : dict
            valid owl ontology in json-ld or turtle format
        key : str
            API key
        opts : dict
            options object

        Returns
        -------
        dict
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        docObj = DocumentTemplate.formatDocument(
            docObj, False, opts)
        return DispatchRequest.sendRequestByAction(
            idParser.schemaURL(), const.UPDATE_SCHEMA, key, docObj)

    def createDocument(self, docObj, documentID, dbID=None, key=None):
        """Creates a new document in the specified database

        Parameters
        ----------
        docObj : dict
            a valid document in json-ld
        documentID : str
            a valid Terminus document id
        dbId : str
            a valid TerminusDB id
        key : str, optional
            API key
        """
        if(dbID):
            self.conConfig.setDB(dbID)
        self.conConfig.setDocument(documentID)
        docObj = DocumentTemplate.formatDocument(
            doc, None, None, self.conConfig.docURL())
        return self.dispatch(self.conConfig.docURL(), const.CREATE_DOCUMENT, key, docObj)

    @staticmethod
    def directCreateDocument(docObj, documentID, dbURL, key):
        """Creates a new document in the specified database

        Parameters
        ----------
        docObj : dict
            a valid document in json-ld
        documentID : str
            a valid Terminus document id
        dbURL : str
            a valid TerminusDB full URL
        key : str, optional
            API key
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        idParser.parseDocumentID(documentID)

        docObj = DocumentTemplate.formatDocument(doc, None, None, idParser.docURL())
        return DispatchRequest.sendRequestByAction(idParser.docURL(), const.CREATE_DOCUMENT, key, docObj)

    def getDocument(self, documentID, dbID=None, key=None, opts={"terminus:encoding": "terminus:frame"}):
        """Retrieves a document from the specified database

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        dbId : str
            a valid TerminusDB id
        key : str, optional
            API key
        opts : dict
            options object
        """
        if(dbID):
            self.conConfig.setDB(dbID)

        self.conConfig.setDocument(documentID)
        return self.dispatch(self.conConfig.docURL(), const.GET_DOCUMENT, key, opts)

    @staticmethod
    def directGetDocument(documentID, dbURL, key, opts={"terminus:encoding": "terminus:frame"}):
        """Retrieves a document from the specified database with URL

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        dbURL : str
            a valid TerminusDB full URL
        key : str, optional
            API key
        opts : dict
            options object
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        idParser.parseDocumentID(documentID)
        return DispatchRequest.sendRequestByAction(idParser.docURL(), const.GET_DOCUMENT, key, opts)

    def updateDocument(self, documentID, docObj, dbID=None, key=None):
        """
        Updates a document in the specified database with a new version

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        docObj : dict
            a valid document in json-ld
        dbId : str
            a valid TerminusDB id
        key : str, optional
            API key
        """
        if(dbID):
            self.conConfig.setDB(dbID)

        self.conConfig.setDocument(documentID)
        docObj = DocumentTemplate.formatDocument(
            docObj, None, None, self.conConfig.docURL())
        return self.dispatch(self.conConfig.docURL(), const.UPDATE_DOCUMENT, key, docObj)

    @staticmethod
    def directUpdateDocument(documentID, dbURL, key, docObj):
        """
        Updates a document in the specified database with URL

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        dbURL : str
            a valid TerminusDB full URL
        key : str, optional
            API key
        docObj : dict
            a valid document in json-ld
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        idParser.parseDocumentID(documentID)
        docObj = DocumentTemplate.formatDocument(
            docObj, None, None, idParser.docURL())
        return DispatchRequest.sendRequestByAction(idParser.docURL(), const.GET_DOCUMENT, key, docObj)

    def deleteDocument(self, documentID, dbID=None, key=None):
        """
        Deletes a document from the specified database

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        dbId : str
            a valid TerminusDB id
        key : str, optional
            API key
        """
        if(dbID):
            self.conConfig.setDB(dbID)

        self.conConfig.setDocument(documentID)

        return self.dispatch(self.conConfig.docURL(), const.DELETE_DOCUMENT, key)

    @staticmethod
    def directDeleteDocument(self, documentID, dbURL, key):
        """
        Deletes a document from the specified database with URL

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        dbURL : str
            a valid TerminusDB full URL
        key : str, optional
            API key
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        idParser.parseDocumentID(documentID)

        return DispatchRequest.sendRequestByAction(idParser.docURL(), const.DELETE_DOCUMENT, key)

    def select(self, woqlQuery, dbID=None, key=None):
        """
        Executes a read-only WOQL query on the specified database and returns the results

        Parameters
        ----------
        woqlQuery : WOQLQuery object
            woql query select statement
        dbId : str
            a valid TerminusDB id
        key : str, optional
            API key
        """
        if(dbID):
            self.conConfig.setDB(dbID)

        payload = {'terminus:query': json.dumps(woqlQuery)}
        return self.dispatch(self.conConfig.queryURL(), const.WOQL_SELECT, key, payload)

    @staticmethod
    def directSelect(woqlQuery, dbURL, key):
        idParser = IDParser()
        idParser.parseDBURL(dbURL)

        payload = {'terminus:query': json.dumps(woqlQuery)}
        return DispatchRequest.sendRequestByAction(idParser.queryURL(), const.WOQL_SELECT, key, payload)

    def update(self, woqlQuery, dbID=None, key=None):
        """
        Executes a WOQL query on the specified database which updates the state and returns the results

        The first (qurl) argument can be
        1) a valid URL of a terminus database or
        2) omitted - the current database will be used
        the second argument (woql) is a woql select statement encoded as a string
        the third argument (opts) is an options json - opts.key is an optional API key
        """
        if(dbID):
            self.conConfig.setDB(dbID)
            # raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Update"))
        payload = {'terminus:query': json.dumps(woqlQuery)}
        return self.dispatch(self.conConfig.queryURL(), const.WOQL_UPDATE, key, payload)

    @staticmethod
    def directUpdate(woqlQuery, dbURL, key):
        idParser = IDParser()
        idParser.parseDBURL(dbURL)

        payload = {'terminus:query': json.dumps(woqlQuery)}
        return DispatchRequest.sendRequestByAction(idParser.queryURL(), const.WOQL_UPDATE, key, payload)

    def dispatch(self, url, action, connectionKey, payload={}):
        if connectionKey is None:
            # if the api key is not setted the method raise an APIerror
            connectionKey = self.conCapabilities.getClientKey()

        #if (action != const.CONNECT and self.conConfig.connectedMode and self.conCapabilities.serverConnected() is False):

            #key = payload.key if isinstance(payload,dict) and key in payload else False
            #self.connect(self.conConfig.serverURL, connectionKey)
            #print("CONNCT BEFORE ACTION", action)

        #check if we can perform this action or raise an AccessDeniedError error
        #review the access control
        #self.conCapabilities.capabilitiesPermit(action)
        return DispatchRequest.sendRequestByAction(url, action, connectionKey, payload)
