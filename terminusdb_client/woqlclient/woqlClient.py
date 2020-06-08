# woqlClient.py
import json

from .api_endpoint_const import APIEndpointConst
from .connectionCapabilities import ConnectionCapabilities

# from .errorMessage import *
from .connectionConfig import ConnectionConfig
from .dispatchRequest import DispatchRequest

# from .errors import (InvalidURIError)
# from .errors import doc, opts

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
            self.conConfig.update(**kwargs)

        json_obj = self.dispatch(APIEndpointConst.CONNECT, self.conConfig.server)
        self.conCapabilities.set_capabilities(json_obj)
        return json_obj

    def copy(self):
        return copy(self)

    def basic_auth(self, key=None, user=None):
        if key:
            self.conConfig.set_basic_auth(key, user)
        return self.conConfig.basic_auth

    def jwt(self, jwt=None, account_user=None):
        if jwt:
            self.conConfig.set_jwt(jwt, account_user)
        return self.conConfig.jwt

    def db(self, dbid=None):
        if dbid:
            self.conConfig.db = dbid
        return self.conConfig.db

    def account(self, accountid=None):
        if accountid:
            self.conConfig.account = accountid
        return self.conConfig.account

    def repo(self, repoid=None):
        if repoid:
            self.conConfig.repo = repoid

        return self.conConfig.repo

    def ref(self, refid=None):
        if refid:
            self.conConfig.ref = refid
        return self.conConfig.ref

    def checkout(self, branchid=None):
        if branchid:
            self.conConfig.branch = branchid
        return self.conConfig.branch

    def uid(self, ignore_jwt=True):
        return self.conConfig.user(ignore_jwt)

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

    def set(self, **kwargs):  # bad naming
        self.conConfig.update(**kwargs)

    def create_database(self, dbid, accountid, details):
        """
        Create a Terminus Database by posting
        a terminus:Database document to the Terminus Server

        Parameters
        ----------
        dbid : str
            ID of the specific database to create
        details : dictionary with the following properties: 
            label: textual name of db
            comment: text description of db
            base_uri: uri to use for prefixing internal documents 
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
        self.account(accountid)  

        return self.dispatch(
            APIEndpointConst.CREATE_DATABASE, self.conConfig.db_url(), details
        )

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
        if accountid:
            self.account(accountid)

        json_response = self.dispatch(
            APIEndpointConst.DELETE_DATABASE, self.conConfig.db_url()
        )
        self.conCapabilities.remove_db(self.db(), self.account())
        return json_response

    def create_graph(self, graph_type, graph_id, commit_msg):
        if graph_type in ["inference", "schema", "instance"]:
            commit = self.generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.CREATE_GRAPH,
                self.conConfig.graph_url(graph_type, graph_id),
                commit,
            )

        raise ValueError(
            "Create graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
        )

    def delete_graph(self, graph_type, graph_id, commit_msg):
        if graph_type in ["inference", "schema", "instance"]:
            commit = self.generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.DELETE_GRAPH,
                self.conConfig.graph_url(graph_type, graph_id),
                commit,
            )

        raise ValueError(
            "Delete graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
        )

    def get_triples(self, graph_type, graph_id):
        return self.dispatch(
            APIEndpointConst.GET_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
        )

    def update_triples(self, graph_type, graph_id, turtle, commit_msg):
        commit = self.generate_commit(commit_msg)
        commit.turtle = turtle
        return self.dispatch(
            APIEndpointConst.UPDATE_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
            commit,
        )

    def get_class_frame(self, class_name):
        opts = {"class": class_name}
        return self.dispatch(
            APIEndpointConst.CLASS_FRAME,
            self.conConfig.class_frame_url(class_name),
            opts,
        )

    def query(
        self, woql_query, commit_msg="Automatically Added Commit", file_list=None
    ):
        # woql.containsUpdate()
        query_obj = self.generate_commit(commit_msg)

        if type(file_list) == dict:
            file_dict = query_obj
            for name in file_list:
                path = file_list[name]
                stream = open(path, "rb")
                file_dict[name] = (name, stream, "text/plain")
            file_dict["query"] = (
                None,
                woql_query.to_json(),
                "application/json",
            )
            payload = None
        else:
            file_dict = None
            query_obj["query"] = woql_query.to_json()
            payload = query_obj

        return self.dispatch(
            APIEndpointConst.WOQL_QUERY, self.conConfig.query_url(), payload, file_dict
        )

    def branch(self, new_branch_id):
        if self.ref():
            source = {
                "origin": f"{self.account()}/{self.db()}/{self.repo()}/commit/{self.ref()}"
            }
        else:
            source = {
                "origin": f"{self.account()}/{self.db()}/{self.repo()}/branch/{self.checkout()}"
            }

        return self.dispatch(
            APIEndpointConst.BRANCH, self.conConfig.branch_url(new_branch_id), source
        )

    def fetch(self, repo_id):
        return self.dispatch(APIEndpointConst.FETCH, self.conConfig.fetch_url(repo_id))

    def push(self, target_repo, target_branch):
        return self.dispatch(
            APIEndpointConst.PUSH, self.conConfig.push_url(target_repo, target_branch)
        )

    def rebase(self, remote_repo_id, remote_branch_id):
        return self.dispatch(
            APIEndpointConst.REBASE,
            self.conConfig.rebase_url(remote_repo_id, remote_branch_id),
        )

    def clonedb(self, clone_source, newid):
        return self.dispatch(
            APIEndpointConst.CLONE, self.conConfig.clone_url(newid), clone_source
        )

    def generate_commit(self, msg, author=None):
        if author:
            mes_author = author
        else:
            mes_author = self.uid()

        ci = {"commit_info": {"author": mes_author, "message": msg}}
        return ci

    def dispatch(
        self, action, url, payload={}, file_dict=None
    ):  # don't use dict as default
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
        # url, action, payload={}, basic_auth, jwt=None, file_dict=None)
        return DispatchRequest.send_request_by_action(
            url, action, payload, self.basic_auth(), self.jwt(), file_dict
        )
