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

    """
        The WOQLClient constructor

        :param **kwargs Connection arguments used to configure the Client. (db=terminusDBName | server=terminusServerURL | doc=docName | key=apiKey)

    """

    def __init__(self, server_url, **kwargs):
        # current conCapabilities context variables
        """
        Parameters
        ----------
        server_url str 
        key        str option key 
        user
        jwt
        jwt_user
        account
        db: set cursor to this db
        repo: set cursor to this repo
        branch: set branch to this id

        """
        self.conConfig = ConnectionConfig(server_url,**kwargs)
        self.conCapabilities = ConnectionCapabilities()




    def connect(self, **kwargs):
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
        key        str option key 
        user
        jwt
        jwt_user
        account
        db: set cursor to this db
        repo: set cursor to this repo
        branch: set branch to this id


        Returns
        -------
        dict or raise an InvalidURIError

        Examples
        -------
        >>> woql.WOQLClient().connect(serverUrl, key)
        dict
        """
        if len(kwarg) > 0:
            self.connectionConfig.update(**kwargs)
        
        jsonObj = self.dispatch(self.conConfig.serverURL, const.CONNECT)
        self.conCapabilities.addConnection(jsonObj)
        return jsonObj


    def key (self,key=None, user=None): 
        if key :
            self.connectionConfig.set_key(key, user)
        return self.connectionConfig.key
    
    def jwt (self,jwt=None, accountUser=None):
        if jwt :   
            self.connectionConfig.set_jwt(jwt, accountUser)
        return self.connectionConfig.jwt


    def db (self,dbid=None):
        if dbid :
            self.connectionConfig.db = dbid
        return self.connectionConfig.db

    def account (self,accountid=None) :
        if accountid :
            self.connectionConfig.account=accountid
        self.connectionConfig.account

    def repo (self,repoid=None) :
        if repoid :
            self.connectionConfig.repo= repoid
    
        return self.connectionConfig.repo

    def ref (self,refid=None):
        if refid :
            self.connectionConfig.ref=refid
        return self.connectionConfig.ref


    def checkout (self, branchid):
        if branchid :
          self.connectionConfig.branch=branchid  
        return self.connectionConfig.branch

    def uid (self,ignore_jwt):
        return self.connectionConfig.user(ignore_jwt)

    """
    Parameters
        ----------
        key        str option key 
        user
        jwt
        jwt_user
        account
        db: set cursor to this db
        repo: set cursor to this repo
        branch: set branch to this id
    """

    def set (self,**kwargs):
        self.connectionConfig.update(**kwargs)

    def create_database = function(self, dbid, label, **kwargs):
        """
        Create a Terminus Database by posting
        a terminus:Database document to the Terminus Server

        Parameters
        ----------
        dbid : str
            ID of the specific database to create
        label : str
            Terminus label
        key : str, optional
            you can omit the key if you have set it before
        kwargs
            Optional arguments that ``createDatabase`` takes

        Returns
        -------
        dict

        Examples
        --------
        WOQLClient(server="http://localhost:6363").createDatabase("someDB", "Database Label", "password")
        """

        self.db(dbid)
        if kwargs.get('accountid'): 
            self.account(accountid)

        comment = kwargs.get("comment",label);
        username=self.account();

        doc={"label":label,
               "comment":comment,
               "prefixes":{"scm":f"terminus://{username}/{dbid}/schema#",
                           "doc":f"terminus://{username}/{dbid}/data/"}}

        
        return this.dispatch(self.connectionConfig.db_url(), const.CREATE_DATABASE,  doc)
    
    
    def delete_database(self, dbid , accountid=None):
        """Delete a TerminusDB database

        Parameters
        ----------
        dbID : str
            ID of the database to delete
        key : str, optional
            you need the key if you didn't set before

        Returns
        -------
        dict

        Examples
        -------
        >>> WOQLClient(server="http://localhost:6363").deleteDatabase("someDBToDelete", "password")
        """
        self.db(dbid)
        jsonResponse = self.dispatch(
            self.conConfig.db_url(), const.DELETE_DATABASE)
        self.conCapabilities.removeDB(self.db(), self.account())
        return jsonResponse

    def create_graph (self, graph_type, graph_id, commit_msg):
        if graph_type in ["inference", "schema", "instance"] :
            commit = self.generate_commit(commit_msg)
            return self.dispatch(CONST.CREATE_GRAPH, self.connectionConfig.graph_url(graph_type, graph_id), commit_msg)
    
        raise ValueError('Create graph parameter error - you must specify a valid type (inference, instance, schema), graph id and commit message')
    
    def generate_commit(self,msg, author):
        mes_author
        if author : 
            mes_author=author
        else 
            mes_author=self.uid()

        ci = {"commit_info": {author: mes_author, message: msg}}
        return ci


    
    def get_schema(self, dbID=None, key=None, options={"terminus:encoding": "terminus:turtle"}):
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

   
    def update_schema(self, docObj, dbID=None, key=None, opts={"terminus:encoding": "terminus:turtle"}):
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
        Returns
        -------
        dict
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

        Returns
        -------
        dict or raise an InvalidURIError
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

        Returns
        -------
        dict
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

        Returns
        -------
        dict or raise an InvalidURIError
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

        Returns
        -------
        dict
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

        Returns
        -------
        dict or raise an InvalidURIError
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

        Returns
        -------
        dict
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

        Returns
        -------
        dict or raise an InvalidURIError
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)
        idParser.parseDocumentID(documentID)

        return DispatchRequest.sendRequestByAction(idParser.docURL(), const.DELETE_DOCUMENT, key)

    def select(self, woqlQuery, dbID=None, key=None,fileList=None):
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
        fileList : list, optional
            List of files that are needed for the query

        Returns
        -------
        dict
        """
        if(dbID):
            self.conConfig.setDB(dbID)

        payload = {'terminus:query': json.dumps(woqlQuery)}
        if type(fileList) == dict:
            payload.update(fileList);

        return self.dispatch(self.conConfig.queryURL(), const.WOQL_SELECT, key, payload)

    @staticmethod
    def directSelect(woqlQuery, dbURL, key, fileList=None):
        """
        Static function that executes a read-only WOQL query on the specified database
        and returns the results

        Parameters
        ----------
        woqlQuery : WOQLQuery object
            woql query select statement
        dbId : str
            a valid full TerminusDB database URL
        key : str, optional
            API key
        fileList : list, optional
            List of files that are needed for the query

        Returns
        -------
        dict or raise an InvalidURIError
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)

        payload = {'terminus:query': json.dumps(woqlQuery)}
        if type(fileList) == dict:
            payload.update(fileList);
        return DispatchRequest.sendRequestByAction(idParser.queryURL(), const.WOQL_SELECT, key, payload)

    def update(self, woqlQuery, dbID=None, key=None ,fileList=None):
        """
        Executes a WOQL query on the specified database which updates the state and returns the results

        Parameters
        ----------
        woqlQuery : WOQLQuery object
            woql query select statement
        dbId : str
            a valid TerminusDB database ID
        key : str, optional
            API key
        fileList : list, optional
            List of files that are needed for the query

        Returns
        -------
        dict
        """
        if(dbID):
            self.conConfig.setDB(dbID)
            # raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Update"))
        if type(fileList) == dict:
            file_dict = {}
            for name in fileList:
                path = fileList[name]
                stream = open(path, 'rb')
                print(name)
                file_dict[name] = (name,stream,'text/plain')
            file_dict['terminus:query'] = (None,json.dumps(woqlQuery),'application/json')
            payload = None
        else:
            file_dict = None
            payload = {'terminus:query': json.dumps(woqlQuery)}

        return self.dispatch(self.conConfig.queryURL(), const.WOQL_UPDATE, key, payload, file_dict)

    @staticmethod
    def directUpdate(woqlQuery, dbURL, key,fileList=None):
        """
        Static function that executes a WOQL query on the specified database which
        updates the state and returns the results

        Parameters
        ----------
        woqlQuery : WOQLQuery object
            woql query select statement
        dbURL : str
            a valid full TerminusDB database URL
        key : str, optional
            API key
        fileList : list, optional
            List of files that are needed for the query

        Returns
        -------
        dict or raise an InvalidURIError
        """
        idParser = IDParser()
        idParser.parseDBURL(dbURL)

        if type(fileList) == dict:
            file_dict = {}
            for name in fileList:
                path = fileList[name]
                stream = open(path, 'rb')
                print(name)
                file_dict[name] = (name,stream,'text/plain')
            file_dict['terminus:query'] = (None,json.dumps(woqlQuery),'application/json')
            payload = None
        else:
            file_dict = None
            payload = {'terminus:query': json.dumps(woqlQuery)}

        return DispatchRequest.sendRequestByAction(idParser.queryURL(), const.WOQL_UPDATE, key, payload, file_dict)

    
    def dispatch(self, url, action, payload={}, file_dict = None):
        """
        Directly dispatch to a Terminus database.

        Parameters
        ----------
        url : str
            The server URL to point the action at
        connectionKey : str
            API key to the document
        payload : dict
            Payload to send to the server
        file_dict : list, optional
            List of files that are needed for the query


        Returns
        -------
        dict or raise an InvalidURIError
        """
       
       

        #check if we can perform this action or raise an AccessDeniedError error
        #review the access control
        #self.conCapabilities.capabilitiesPermit(action)
        return DispatchRequest.sendRequestByAction(url, action, self.key(), payload, file_dict, self.jwt())
