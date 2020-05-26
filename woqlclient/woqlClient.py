# woqlClient.py
import json

from .connectionCapabilities import ConnectionCapabilities

# from .errorMessage import *
from .connectionConfig import ConnectionConfig
from .api_endpoint_const import APIEndpointConst
from .dispatchRequest import DispatchRequest
from .documentTemplate import DocumentTemplate

# from .errors import (InvalidURIError)
# from .errors import doc, opts
from .id_parser import IDParser

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
        self.conConfig = ConnectionConfig(server_url, **kwargs)
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
        if len(kwargs) > 0:
            self.connectionConfig.update(**kwargs)

        json_obj = self.dispatch(self.conConfig.server_url, APIEndpointConst.CONNECT)
        self.conCapabilities.set_capabilities(json_obj)
        return json_obj

    def key(self, key=None, user=None):
        if key:
            self.connectionConfig.set_key(key, user)
        return self.connectionConfig.key

    def jwt(self, jwt=None, account_user=None):
        if jwt:
            self.connectionConfig.set_jwt(jwt, account_user)
        return self.connectionConfig.jwt

    def db(self, dbid=None):
        if dbid:
            self.connectionConfig.db = dbid
        return self.connectionConfig.db

    def account(self, accountid=None):
        if accountid:
            self.connectionConfig.account = accountid
        self.connectionConfig.account

    def repo(self, repoid=None):
        if repoid:
            self.connectionConfig.repo = repoid

        return self.connectionConfig.repo

    def ref(self, refid=None):
        if refid:
            self.connectionConfig.ref = refid
        return self.connectionConfig.ref

    def checkout(self, branchid):
        if branchid:
            self.connectionConfig.branch = branchid
        return self.connectionConfig.branch

    def uid(self, ignore_jwt):
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

    def set(self, **kwargs): #bad naming
        self.connectionConfig.update(**kwargs)

    def create_database(self, dbid, label, **kwargs):
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
        if kwargs.get("accountid"):
            self.account(accountid) #where does accountid comes from

        comment = kwargs.get("comment", label)
        username = self.account()

        doc = {
            "label": label,
            "comment": comment,
            "prefixes": {
                "scm": f"terminus://{username}/{dbid}/schema#",
                "doc": f"terminus://{username}/{dbid}/data/",
            },
        }

        return self.dispatch(self.connectionConfig.db_url(), APIEndpointConst.CREATE_DATABASE, doc)

    def delete_database(self, dbid, accountid=None):
        """Delete a TerminusDB database

        Parameters
        ----------
        dbid : str
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
        json_response = self.dispatch(self.conConfig.db_url(), APIEndpointConst.DELETE_DATABASE)
        self.conCapabilities.remove_db(self.db(), self.account())
        return json_response

    def create_graph(self, graph_type, graph_id, commit_msg):
        if graph_type in ["inference", "schema", "instance"]:
            self.generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.CREATE_GRAPH,
                self.connectionConfig.graph_url(graph_type, graph_id),
                commit_msg,
            )

        raise ValueError(
            "Create graph parameter error - you must specify a valid type (inference, instance, schema), graph id and commit message"
        )

    def generate_commit(self, msg, author):
        if author:
            mes_author = author
        else:
            mes_author = self.uid()

        ci = {"commit_info": {"author": mes_author, "message": msg}}
        return ci

    def get_schema(
        self, dbid=None, key=None, options={"terminus:encoding": "terminus:turtle"}
    ): #don't use dict as default
        self.conConfig.setDB(dbid)
        json_response = self.dispatch(self.conConfig.db_url(), APIEndpointConst.DELETE_DATABASE, key)
        self.conCapabilities.removeDB()
        return json_response

    @staticmethod
    def direct_delete_database(db_url, key):
        """Delete a TerminusDB with settings

        Parameters
        ----------
        db_url : str
            TerminusDB full URL like http://localhost:6363/myDB
        key : str
            the server API key
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)
        return DispatchRequest.sendRequestByAction(
            id_parser.db_url(), APIEndpointConst.DELETE_DATABASE, key
        )

    def update_schema(
        self, doc_obj, dbid=None, key=None, opts={"terminus:encoding": "terminus:turtle"}
    ):
        """Updates the Schema of the specified database

        opts.format is used to specify which format is being used (*json / turtle)

        Parameters
        ----------
        doc_obj : dict
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
        if dbid:
            self.conConfig.setDB(dbid)
        doc_obj = DocumentTemplate.formatDocument(doc_obj, False, opts)
        return self.dispatch(
            self.conConfig.schemaURL(), APIEndpointConst.UPDATE_SCHEMA, key, doc_obj
        )

    @staticmethod
    def direct_update_schema(
        db_url, doc_obj, key, opts={"terminus:encoding": "terminus:turtle"}
    ):
        """Updates the Schema of the specified database with settings

        opts.format is used to specify which format is being used (*json / turtle)

        Parameters
        ----------
        db_url : str
            a valid TerminusDB full URL
        doc_obj : dict
            valid owl ontology in json-ld or turtle format
        key : str
            API key
        opts : dict
            options object

        Returns
        -------
        dict
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)
        doc_obj = DocumentTemplate.formatDocument(doc_obj, False, opts)
        return DispatchRequest.sendRequestByAction(
            id_parser.schemaURL(), APIEndpointConst.UPDATE_SCHEMA, key, doc_obj
        )

    def create_document(self, doc_obj, documentID, dbid=None, key=None):
        """Creates a new document in the specified database

        Parameters
        ----------
        doc_obj : dict
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
        if dbid:
            self.conConfig.setDB(dbid)
        self.conConfig.setDocument(documentID)
        doc_obj = DocumentTemplate.formatDocument(
            doc, None, None, self.conConfig.docURL()
        )
        return self.dispatch(
            self.conConfig.docURL(), APIEndpointConst.CREATE_DOCUMENT, key, doc_obj
        )

    @staticmethod
    def direct_create_document(doc_obj, documentID, db_url, key):
        """Creates a new document in the specified database

        Parameters
        ----------
        doc_obj : dict
            a valid document in json-ld
        documentID : str
            a valid Terminus document id
        db_url : str
            a valid TerminusDB full URL
        key : str, optional
            API key

        Returns
        -------
        dict or raise an InvalidURIError
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)
        id_parser.parseDocumentID(documentID)

        doc_obj = DocumentTemplate.formatDocument(doc_obj, None, None, id_parser.docURL())
        return DispatchRequest.sendRequestByAction(
            id_parser.docURL(), APIEndpointConst.CREATE_DOCUMENT, key, doc_obj
        )

    def get_document(
        self,
        documentID,
        dbid=None,
        key=None,
        opts={"terminus:encoding": "terminus:frame"},
    ):
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
        if dbid:
            self.conConfig.setDB(dbid)

        self.conConfig.setDocument(documentID)
        return self.dispatch(self.conConfig.docURL(), APIEndpointConst.GET_DOCUMENT, key, opts)

    @staticmethod
    def directGetDocument(
        documentID, db_url, key, opts={"terminus:encoding": "terminus:frame"}
    ):
        """Retrieves a document from the specified database with URL

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        db_url : str
            a valid TerminusDB full URL
        key : str, optional
            API key
        opts : dict
            options object

        Returns
        -------
        dict or raise an InvalidURIError
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)
        id_parser.parseDocumentID(documentID)
        return DispatchRequest.sendRequestByAction(
            id_parser.docURL(), APIEndpointConst.GET_DOCUMENT, key, opts
        )

    def updateDocument(self, documentID, doc_obj, dbid=None, key=None):
        """
        Updates a document in the specified database with a new version

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        doc_obj : dict
            a valid document in json-ld
        dbId : str
            a valid TerminusDB id
        key : str, optional
            API key

        Returns
        -------
        dict
        """
        if dbid:
            self.conConfig.setDB(dbid)

        self.conConfig.setDocument(documentID)
        doc_obj = DocumentTemplate.formatDocument(
            doc_obj, None, None, self.conConfig.docURL()
        )
        return self.dispatch(
            self.conConfig.docURL(), APIEndpointConst.UPDATE_DOCUMENT, key, doc_obj
        )

    @staticmethod
    def direct_update_document(documentID, db_url, key, doc_obj):
        """
        Updates a document in the specified database with URL

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        db_url : str
            a valid TerminusDB full URL
        key : str, optional
            API key
        doc_obj : dict
            a valid document in json-ld

        Returns
        -------
        dict or raise an InvalidURIError
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)
        id_parser.parseDocumentID(documentID)
        doc_obj = DocumentTemplate.formatDocument(doc_obj, None, None, id_parser.docURL())
        return DispatchRequest.sendRequestByAction(
            id_parser.docURL(), APIEndpointConst.GET_DOCUMENT, key, doc_obj
        )

    def deleteDocument(self, documentID, dbid=None, key=None):
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
        if dbid:
            self.conConfig.setDB(dbid)

        self.conConfig.setDocument(documentID)

        return self.dispatch(self.conConfig.docURL(), APIEndpointConst.DELETE_DOCUMENT, key)

    @staticmethod
    def directDeleteDocument(self, documentID, db_url, key):
        """
        Deletes a document from the specified database with URL

        Parameters
        ----------
        documentID : str
            a valid Terminus document id
        db_url : str
            a valid TerminusDB full URL
        key : str, optional
            API key

        Returns
        -------
        dict or raise an InvalidURIError
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)
        id_parser.parseDocumentID(documentID)

        return DispatchRequest.sendRequestByAction(
            id_parser.docURL(), APIEndpointConst.DELETE_DOCUMENT, key
        )

    def select(self, woql_query, dbid=None, key=None, fileList=None):
        """
        Executes a read-only WOQL query on the specified database and returns the results

        Parameters
        ----------
        woql_query : WOQLQuery object
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
        if dbid:
            self.conConfig.setDB(dbid)

        payload = {"terminus:query": json.dumps(woql_query)}
        if type(fileList) == dict:
            payload.update(fileList)

        return self.dispatch(self.conConfig.queryURL(), APIEndpointConst.WOQL_SELECT, key, payload)

    @staticmethod
    def directSelect(woql_query, db_url, key, fileList=None):
        """
        Static function that executes a read-only WOQL query on the specified database
        and returns the results

        Parameters
        ----------
        woql_query : WOQLQuery object
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
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)

        payload = {"terminus:query": json.dumps(woql_query)}
        if type(fileList) == dict:
            payload.update(fileList)
        return DispatchRequest.sendRequestByAction(
            id_parser.queryURL(), APIEndpointConst.WOQL_SELECT, key, payload
        )

    def update(self, woql_query, dbid=None, key=None, fileList=None):
        """
        Executes a WOQL query on the specified database which updates the state and returns the results

        Parameters
        ----------
        woql_query : WOQLQuery object
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
        if dbid:
            self.conConfig.setDB(dbid)
            # raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Update"))
        if type(fileList) == dict:
            file_dict = {}
            for name in fileList:
                path = fileList[name]
                stream = open(path, "rb")
                print(name)
                file_dict[name] = (name, stream, "text/plain")
            file_dict["terminus:query"] = (
                None,
                json.dumps(woql_query),
                "application/json",
            )
            payload = None
        else:
            file_dict = None
            payload = {"terminus:query": json.dumps(woql_query)}

        return self.dispatch(
            self.conConfig.queryURL(), APIEndpointConst.WOQL_UPDATE, key, payload, file_dict
        )

    @staticmethod
    def direct_update(woql_query, db_url, key, fileList=None):
        """
        Static function that executes a WOQL query on the specified database which
        updates the state and returns the results

        Parameters
        ----------
        woql_query : WOQLQuery object
            woql query select statement
        db_url : str
            a valid full TerminusDB database URL
        key : str, optional
            API key
        fileList : list, optional
            List of files that are needed for the query

        Returns
        -------
        dict or raise an InvalidURIError
        """
        id_parser = IDParser()
        id_parser.parseDBURL(db_url)

        if type(fileList) == dict:
            file_dict = {}
            for name in fileList:
                path = fileList[name]
                stream = open(path, "rb")
                print(name)
                file_dict[name] = (name, stream, "text/plain")
            file_dict["terminus:query"] = (
                None,
                json.dumps(woql_query),
                "application/json",
            )
            payload = None
        else:
            file_dict = None
            payload = {"terminus:query": json.dumps(woql_query)}

        return DispatchRequest.sendRequestByAction(
            id_parser.queryURL(), APIEndpointConst.WOQL_UPDATE, key, payload, file_dict
        )

    def dispatch(self, url, action, payload={}, file_dict=None):
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

        # check if we can perform this action or raise an AccessDeniedError error
        # review the access control
        # self.conCapabilities.capabilitiesPermit(action)
        return DispatchRequest.sendRequestByAction(
            url, action, self.key(), payload, file_dict, self.jwt()
        )
