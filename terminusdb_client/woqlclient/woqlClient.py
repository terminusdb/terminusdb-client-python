"""woqlClient.py"""
import copy
import json

from ..__version__ import __version__
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
    """Client for querying a TerminusDB server using WOQL queries."""

    def __init__(self, server_url, **kwargs):
        r"""The WOQLClient constructor.

        Parameters
        ----------
        server_url : str
            URL of the server that this client will connect to.
        \**kwargs
            Configuration options used to construct a :class:`ConnectionConfig` instance.
            Passing insecure=True will skip HTTPS certificate checking.
        """
        self.conConfig = ConnectionConfig(server_url, **kwargs)
        self.conCapabilities = ConnectionCapabilities()
        self.insecure = kwargs.get("insecure")

    def connect(self, **kwargs):
        r"""Connect to a Terminus server at the given URI with an API key.

        Stores the terminus:ServerCapability document returned
        in the conCapabilities register which stores, the url, key, capabilities,
        and database meta-data for the connected server.

        If the ``serverURL`` argument is omitted,
        :attr:`self.conConfig.serverURL` will be used if present
        or an error will be raise.

        Parameters
        ----------
        \**kwargs
            Configuration options added to :attr:`conConfig`.

        Returns
        -------
        dict

        Examples
        -------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.connect(server_url="http://localhost:6363", key="<key>")
        dict
        """
        if len(kwargs) > 0:
            self.conConfig.update(**kwargs)
        if self.insecure is None:
            self.insecure = kwargs.get("insecure")

        json_obj = self.dispatch(APIEndpointConst.CONNECT, self.conConfig.api)
        self.conCapabilities.set_capabilities(json_obj)
        return json_obj

    def copy(self):
        """Create a deep copy of this client.

        Returns
        -------
        WOQLClient
            The copied client instance.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> clone = client.copy()
        >>> assert client is not clone
        """
        return copy.deepcopy(self)

    def basic_auth(self, key=None, user=None):
        """Set or get the ``user:password`` for basic HTTP authentication to the server.

        If ``key`` is not provided, then the config will not be updated.

        Parameters
        ----------
        key : str, optional
            Optional password to use when authenticating to the server.
        user : str, optional
            Optional user name to use when authenticating to the server.

        Returns
        -------
        str:
            The basic authentication credentials in ``user:password`` format.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.basic_auth()
        False
        >>> client.basic_auth("password", "admin")
        'admin:password'
        >>> client.basic_auth()
        'admin:password'
        """
        if key:
            self.conConfig.set_basic_auth(key, user)
        return self.conConfig.basic_auth

    def remote_auth(self, auth_info=None):
        """Set or get the Basic auth or JWT token used for authenticating to the server.

        If ``auth_info`` is not provided, then the config will not be updated.

        Parameters
        ----------
        auth_info : dict, optional
            Optional dict of authentication info containing
            ``"type"``, ``"user"`` and ``"key"`` keys.

        Returns
        -------
        dict
            The remote authentication info.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.remote_auth()
        >>> client.remote_auth({"type": "jwt", "user": "admin", "key": "<token>"})
        {'type': 'jwt', 'user': 'admin', 'key': '<token>'}
        """
        if auth_info:
            self.conConfig.set_remote_auth(auth_info)
        return self.conConfig.remote_auth

    def set_db(self, dbid):
        """Set and return the current database.

        Parameters
        ----------
        dbid : str, optional
            Database identifer to set in the config.

        Returns
        -------
        str
            The current database identifier.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.set_db("<database>")
        '<database>'
        """
        return self.db(dbid)

    def db(self, dbid=None):
        """Set or get the current database.

        If ``dbid`` is not provided, then the config will not be updated.

        Parameters
        ----------
        dbid : str, optional
            Optional database identifier to set in the config.

        Returns
        -------
        str
            The current database identifier.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.db()
        False
        >>> client.db("<database>")
        '<database>'
        >>> client.db()
        '<database>'
        """
        if dbid:
            self.conConfig.db = dbid
        return self.conConfig.db

    def account(self, accountid=None):
        """Set or get the account identifier.

        If ``accountid`` is not provided, then the config will not be updated.

        Parameters
        ----------
        accountid : str, optional
            Optional account identifier to set in the config.

        Returns
        -------
        str
            The current account name.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.account()
        False
        >>> client.account("<account>")
        '<account>'
        >>> client.account()
        '<account>'
        """
        if accountid:
            self.conConfig.account = accountid
        return self.conConfig.account

    def user_account(self):
        """Get the current user identifier.

        Returns
        -------
        str
            User identifier.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.user_account()
        '<uid>'
        """
        u = self.conCapabilities.get_user()
        return u.id

    def user(self):
        """Get the current user's information.

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.user()
        {'id': '<uid>', 'author': '<author>', 'roles': [], 'label': '<label>', 'comment': '<comment>'}
        """
        return self.conCapabilities.get_user()

    def repo(self, repoid=None):
        """Set or get the repository identifier.

        If ``repoid`` is not provided, then the config will not be updated.

        Parameters
        ----------
        repoid : str, optional
            Optional repository identifier to set in the config.

        Returns
        -------
        str
            The current repository identifier.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.repo()
        'local'
        >>> client.repo("<repository>")
        '<repository>'
        >>> client.repo()
        '<repository>'
        """
        if repoid:
            self.conConfig.repo = repoid

        return self.conConfig.repo

    def ref(self, refid=None):
        """Set or get the ref pointer (pointer to a commit within the branch).

        If ``refid`` is not provided, then the config will not be updated.

        Parameters
        ----------
        refid : str, optional
            Optional ref pointer to set in the config.

        Returns
        -------
        str
            The current ref pointer.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.ref()
        False
        >>> client.ref("<branch>")
        '<branch>'
        >>> client.ref()
        '<branch>'
        """
        if refid:
            self.conConfig.ref = refid
        return self.conConfig.ref

    def checkout(self, branchid=None):
        """Set or get the current branch identifier.

        If ``branchid`` is not provided, then the config will not be updated.

        Parameters
        ----------
        branchid : str, optional
            Optional branch identifier to set in the config.

        Returns
        -------
        str
            The current branch identifier.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.checkout()
        'main'
        >>> client.checkout("<branch>")
        '<branch>'
        >>> client.checkout()
        '<branch>'
        """
        if branchid:
            self.conConfig.branch = branchid
        return self.conConfig.branch

    def uid(self, ignore_jwt=True):
        """Get the current user identifier.

        Parameters
        ----------
        ignore_jwt : bool, optional
            If ``True``, the local user identifier will be returned rather than the one set in the JWT.

        Returns
        -------
        str
            The local or JWT user identifier.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.uid()
        '<uid>'
        >>> client.uid(False)
        '<jwt_uid>'
        """
        return self.conConfig.user(ignore_jwt)

    def resource(self, ttype, val=None):
        """Create a resource identifier string based on the current config.

        Parameters
        ----------
        ttype : str
            Type of resource. One of ["db", "meta", "repo", "commits", "ref", "branch"].
        val : str, optional
            Branch or commit identifier.

        Returns
        -------
        str
            The constructed resource string.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.account("<account>")
        '<account>'
        >>> client.db("<db>")
        '<db>'
        >>> client.repo("<repo>")
        '<repo>'
        >>> client.resource("db")
        '<account>/<db>/'
        >>> client.resource("meta")
        '<account>/<db>/_meta'
        >>> client.resource("commits")
        '<account>/<db>/<repo>/_commits'
        >>> client.resource("repo")
        '<account>/<db>/<repo>/_meta'
        >>> client.resource("ref", "<reference>")
        '<account>/<db>/<repo>/commit/<reference>'
        >>> client.resource("branch", "<branch>")
        '<account>/<db>/<repo>/branch/<branch>'
        """
        base = self.account() + "/" + self.db() + "/"
        if ttype == "db":
            return base
        elif ttype == "meta":
            return base + "_meta"
        base = base + self.repo()
        if ttype == "repo":
            return base + "/_meta"
        elif ttype == "commits":
            return base + "/_commits"
        if val is None:
            if ttype == "ref":
                val = self.ref()
            else:
                val = self.checkout()
        if ttype == "branch":
            return base + "/branch/" + val
        if ttype == "ref":
            return base + "/commit/" + val

    def set(self, **kwargs):  # bad naming
        r"""Update multiple config values on the current context.

        Parameters
        ----------
        \**kwargs
            Dict of config options to set.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.set({"account": "<account>", "branch": "<branch>"})
        """
        self.conConfig.update(**kwargs)

    def create_database(
        self,
        dbid,
        accountid=None,
        label=None,
        description=None,
        prefixes=None,
        include_schema=True,
    ):
        """Create a TerminusDB database by posting
        a terminus:Database document to the Terminus Server.

        Parameters
        ----------
        dbid : str
            Unique identifier of the database.
        accountid : str
            ID of the organization in which to create the DB (defaults to 'admin')
        label : str, optional
            Database name.
        description : str, optional
            Database description.
        prefixes : dict, optional
            Optional dict containing ``"doc"`` and ``"scm"`` keys.

            doc (str)
                IRI to use when ``doc:`` prefixes are expanded. Defaults to ``terminusdb:///data``.
            scm (str)
                IRI to use when ``scm:`` prefixes are expanded. Defaults to ``terminusdb:///schema``.
        include_schema : bool
            If ``True``, a main schema graph will be created, otherwise only a main instance graph will be created.

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.create_database("someDB", "Database Label", "password")
        """
        details = {}
        if label:
            details["label"] = label
        else:
            details["label"] = dbid
        if description:
            details["comment"] = description
        else:
            details["comment"] = ""
        if include_schema:
            details["schema"] = True
        if prefixes:
            details["prefixes"] = prefixes
        if accountid is None:
            accountid = self.user_account()

        self.db(dbid)
        self.account(accountid)
        return self.dispatch(
            APIEndpointConst.CREATE_DATABASE, self.conConfig.db_url(), details
        )

    def delete_database(self, dbid, accountid=None):
        """Delete a TerminusDB database.

        If ``accountid`` is provided, then the account in the config will be updated
        and the new value will be used in future requests to the server.

        Parameters
        ----------
        dbid : str
            ID of the database to delete
        accountid : str, optional
            the account id in which the database resides (defaults to "admin")

        Returns
        -------
        dict

        Examples
        -------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.delete_database("<database>", "<account>")
        dict
        """

        self.db(dbid)
        if accountid:
            self.account(accountid)

        json_response = self.dispatch(
            APIEndpointConst.DELETE_DATABASE, self.conConfig.db_url()
        )
        return json_response

    def create_graph(self, graph_type, graph_id, commit_msg):
        """Create a new graph in the current database context.

        Parameters
        ----------
        graph_type : str
            Graph type, either ``"inference"``, ``"instance"`` or ``"schema"``.
        graph_id : str
            Graph identifier.
        commit_msg : str
            Commit message.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If the value of ``graph_type`` is invalid.
        """
        if graph_type in ["inference", "schema", "instance"]:
            commit = self._generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.CREATE_GRAPH,
                self.conConfig.graph_url(graph_type, graph_id),
                commit,
            )

        raise ValueError(
            "Create graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
        )

    def delete_graph(self, graph_type, graph_id, commit_msg):
        """Delete a graph from the current database context.

        Parameters
        ----------
        graph_type : str
            Graph type, either ``"inference"``, ``"instance"`` or ``"schema"``.
        graph_id : str
            Graph identifier.
        commit_msg : str
            Commit message.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If the value of ``graph_type`` is invalid.
        """
        if graph_type in ["inference", "schema", "instance"]:
            commit = self._generate_commit(commit_msg)
            return self.dispatch(
                APIEndpointConst.DELETE_GRAPH,
                self.conConfig.graph_url(graph_type, graph_id),
                commit,
            )

        raise ValueError(
            "Delete graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
        )

    def get_triples(self, graph_type, graph_id):
        """Retrieves the contents of the specified graph as triples encoded in turtle format

        Parameters
        ----------
        graph_type : str
            Graph type, either ``"inference"``, ``"instance"`` or ``"schema"``.
        graph_id : str
            Graph identifier.

        Returns
        -------
        dict
        """
        return self.dispatch(
            APIEndpointConst.GET_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
        )

    def update_triples(self, graph_type, graph_id, turtle, commit_msg):
        """Updates the contents of the specified graph with the triples encoded in turtle format Replaces the entire graph contents

        Parameters
        ----------
        graph_type : str
            Graph type, either ``"inference"``, ``"instance"`` or ``"schema"``.
        graph_id : str
            Graph identifier.
        turtle
            Valid set of triples in Turtle format.
        commit_msg : str
            Commit message.

        Returns
        -------
        dict
        """
        commit = self._generate_commit(commit_msg)
        commit["turtle"] = turtle
        return self.dispatch(
            APIEndpointConst.UPDATE_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
            commit,
        )

    def insert_triples(self, graph_type, graph_id, turtle, commit_msg):
        """Inserts into the specified graph with the triples encoded in turtle format.

        Parameters
        ----------
        graph_type : str
            Graph type, either ``"inference"``, ``"instance"`` or ``"schema"``.
        graph_id : str
            Graph identifier.
        turtle
            Valid set of triples in Turtle format.
        commit_msg : str
            Commit message.

        Returns
        -------
        dict
        """
        commit = self._generate_commit(commit_msg)
        commit["turtle"] = turtle
        return self.dispatch(
            APIEndpointConst.INSERT_TRIPLES,
            self.conConfig.triples_url(graph_type, graph_id),
            commit,
        )

    def query(self, woql_query, commit_msg=None, file_dict=None):
        """Updates the contents of the specified graph with the triples encoded in turtle format Replaces the entire graph contents

        Parameters
        ----------
        woql_query : dict or WOQLQuery object
            A woql query as an object or dict
        commit_mg : str
            A message that will be written to the commit log to describe the change
        file_dict:
            File dictionary to be associated with post name => filename, for multipart POST

        Examples
        -------
        >>> WOQLClient(server="http://localhost:6363").query(woql, "updating graph")
        """
        if (
            hasattr(woql_query, "_contains_update_check")
            and woql_query._contains_update_check()
        ):
            if not commit_msg:
                commit_msg = f"Update Query generated by python client {__version__}"
            query_obj = self._generate_commit(commit_msg)
        elif type(woql_query) == dict and commit_msg:
            query_obj = self._generate_commit(commit_msg)
        else:
            query_obj = {}
        if type(woql_query) != dict and hasattr(woql_query, "to_dict"):
            woql_query = woql_query.to_dict()
        woql_query["@context"] = self.conCapabilities.get_context_for_outbound_query(
            None, self.db()
        )
        query_obj["query"] = woql_query
        if type(file_dict) == dict:
            request_file_dict = {}
            for name in query_obj:
                query_obj_value = query_obj[name]
                request_file_dict[name] = (
                    name,
                    json.dumps(query_obj_value),
                    "application/json",
                )
            for name in file_dict:
                path = file_dict[name]
                request_file_dict[name] = (name, open(path, "rb"), "application/binary")
            payload = None
        else:
            request_file_dict = None
            payload = query_obj

        return self.dispatch(
            APIEndpointConst.WOQL_QUERY,
            self.conConfig.query_url(),
            payload,
            request_file_dict,
        )

    def branch(self, new_branch_id, empty=False):
        """Create a branch starting from the current branch.

        Parameters
        ----------
        new_branch_id : str
            New branch identifier.
        empty : bool
            Create an empty branch if true (no starting commit)

        Returns
        -------
        dict
        """
        if empty:
            source = {}
        elif self.ref():
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

    def pull(self, remote_source_repo):
        """Pull updates from a remote repository to the current database.

        Parameters
        ----------
        remote_source_repo : dict
            Remote repository identifier containing ``"remote"`` and ``"remote_branch"`` keys.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If the ``remote_source_repo`` is missing required keys.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.pull({"remote": "<remote>", "remote_branch": "<branch>"})
        """
        rc_args = self._prepare_revision_control_args(remote_source_repo)
        if rc_args and rc_args.get("remote") and rc_args.get("remote_branch"):
            return self.dispatch(
                APIEndpointConst.PULL, self.conConfig.pull_url(), rc_args
            )
        else:
            raise ValueError(
                "Pull parameter error - you must specify a valid remote source and branch to pull from"
            )

    def fetch(self, remote_id):
        return self.dispatch(
            APIEndpointConst.FETCH, self.conConfig.fetch_url(remote_id)
        )

    def push(self, remote_target_repo):
        """Push changes from a branch to a remote repo

        Parameters
        ----------
        remote_source_repo : dict
            details of the remote to push to [remote, remote_branch, message]

        Examples
        -------
        >>> WOQLClient(server="http://localhost:6363").push({remote: "origin", "remote_branch": "main", "author": "admin", "message": "message"})
        """
        rc_args = self._prepare_revision_control_args(remote_target_repo)
        if rc_args and rc_args.get("remote") and rc_args.get("remote_branch"):
            return self.dispatch(
                APIEndpointConst.PUSH, self.conConfig.push_url(), rc_args
            )
        else:
            raise ValueError(
                "Push parameter error - you must specify a valid remote target"
            )

    def rebase(self, rebase_source):
        """Rebase the current branch onto the specified remote branch.

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        rebase_source : dict
            Dict containing a ``"rebase_from"`` key.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If the ``rebase_source`` is missing required keys.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.rebase({"rebase_from": "<branch>"})
        """
        rc_args = self._prepare_revision_control_args(rebase_source)
        if rc_args and rc_args.get("rebase_from"):
            return self.dispatch(
                APIEndpointConst.REBASE, self.conConfig.rebase_url(), rc_args
            )
        else:
            raise ValueError(
                "Rebase parameter error - you must specify a valid rebase source to rebase from"
            )

    def reset(self, commit_path):
        """Reset the current branch HEAD to the specified commith path.

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        commit_path : string
            Path to the commit, for instance admin/database/local/commit/234980523ffaf93.

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.checkout("some_branch")
        >>> client.reset('admin/database/local/commit/234980523ffaf93')
        """

        return self.dispatch(
            APIEndpointConst.RESET,
            self.conConfig.reset_url(),
            {"commit_descriptor": commit_path},
        )

    def optimize(self, path):
        """Optimize the specified path.

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        path : string
            Path to optimize, for instance admin/database/_meta for the repo graph.

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.optimize('admin/database/_meta')
        """
        return self.dispatch(APIEndpointConst.RESET, self.conConfig.optimize_url(path))

    def squash(self, msg, author=None):
        """Squash the current branch HEAD into a commit

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        msg : string
            Message for the newly created squash commit
        author : string
            Author of the commit

        Returns
        -------
        dict
            A dict with the new commit id:
            {'@type' : 'api:SquashResponse',
             'api:commit' : Commit,
             'api:old_commit' : Old_Commit,
             'api:status' : "api:success"}

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.connect(user="admin", key="root", account="admin", db="some_db")
        >>> client.squash('This is a squash commit message!')
        """
        commit_object = self._generate_commit(msg, author)
        return self.dispatch(
            APIEndpointConst.SQUASH, self.conConfig.squash_url(), commit_object
        )

    def clonedb(self, clone_source, newid):
        """Clone a remote repository and create a local copy.

        Parameters
        ----------
        clone_source : dict
            Dict containing a ``"remote_url"`` key.
        newid : str
            Identifier of the new repository to create.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If the ``clone_source`` is missing required keys.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.clonedb({"remote_url": "<remote_url>"}, "<newid>")
        """
        rc_args = self._prepare_revision_control_args(clone_source)
        if rc_args and rc_args.get("remote_url"):
            return self.dispatch(
                APIEndpointConst.CLONE, self.conConfig.clone_url(newid), rc_args
            )
        else:
            raise ValueError(
                "Clone parameter error - you must specify a valid id for the cloned database"
            )

    def _generate_commit(self, msg, author=None):
        """Pack the specified commit info into a dict format expected by the server.

        Parameters
        ----------
        msg : str
            Commit message.
        author : str
            Commit author.

        Returns
        -------
        dict
            Formatted commit info.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client._generate_commit("<message>", "<author>")
        {'commit_info': {'author': '<author>', 'message': '<message>'}}
        """
        if author:
            mes_author = author
        else:
            mes_author = self.conCapabilities.author()

        ci = {"commit_info": {"author": mes_author, "message": msg}}
        return ci

    def _prepare_revision_control_args(self, rc_args=None):
        """Ensure the ``"author"`` field in the specified argument dict is set.
        If ``"author"`` is not in ``rc_args``, the current author value will be set.

        Parameters
        ----------
        rc_args : dict, optional
            Optional dict containing arguments used in revision control actions.

        Returns
        -------
        dict or bool
            ``False`` if ``rc_args`` is not provided, other the modified ``rc_args``.
        """
        if rc_args is None:
            return False
        if not rc_args.get("author"):
            rc_args["author"] = self.conCapabilities.author()
        return rc_args

    def dispatch(self, action, url, payload=None, file_dict=None):
        """Directly dispatch to a TerminusDB database.

        Parameters
        ----------
        action
            The action to perform on the server.
        url : str
            The server URL to point the action at.
        payload : dict
            Payload to send to the server.
        file_dict : dict, optional
            Dict of files to include in the query.

        Returns
        -------
        dict
        """

        # check if we can perform this action or raise an AccessDeniedError error
        # review the access control
        # self.conCapabilities.capabilitiesPermit(action)
        # url, action, payload={}, basic_auth, jwt=None, file_dict=None)

        if payload is None:
            payload = {}

        return DispatchRequest.send_request_by_action(
            url,
            action,
            payload,
            self.basic_auth(),
            self.remote_auth(),
            file_dict,
            self.insecure,
        )

    def get_database(self, dbid, account):
        """
        Returns metadata (id, organization, label, comment) about the requested database
        Parameters
        ----------
        dbid : str
            The id of the database
        account : str
            The account / organization id that the user is acting through

        Returns
        -------
        dict or None if not found
        """
        return self.conCapabilities.get_database(dbid, account)

    def get_databases(self):
        """
        Returns a list of database metadata records for all databases the user has access to

        Returns
        -------
        list of dicts
        """
        return self.conCapabilities.get_databases()

    def get_metadata(self, dbid, account):
        """
        Alias of get_database above - deprecated - included for backwards compatibility
        """
        return self.get_database(dbid, account)

    def server(self):
        """
        Returns the URL of the currently connected server
        """
        return self.conConfig.server

    def api(self):
        """
        Returns the URL of the currently connected server
        """
        return self.conConfig.api

    """
    Unstable / Experimental Endpoints

    The below API endpoints are not yet officially released

    They are part of the server API (not desktop) and will be finalized and
    officially released when that package is released. They should be considered
    unreliable and unstable until then and use is unsupported and at your own risk
    """

    def get_class_frame(self, class_name):
        opts = {"class": class_name}
        return self.dispatch(
            APIEndpointConst.CLASS_FRAME,
            self.conConfig.class_frame_url(),
            opts,
        )
