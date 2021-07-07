"""woqlClient.py
WOQLClient is the Python public API for TerminusDB"""
import copy
import json
import os
import pprint as pp
import warnings
from base64 import b64encode
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
from urllib3.exceptions import InsecureRequestWarning

from ..__version__ import __version__
from ..errors import DatabaseError, InterfaceError
from ..woql_utils import _finish_reponse, _result2stream
from ..woqlquery.woql_query import WOQLQuery

# WOQL client object
# license Apache Version 2
# summary Python module for accessing the Terminus DB API


class NoRequestWarning:
    def __init__(self, insecure):
        self.insecure = insecure

    def __enter__(self):
        if self.insecure:
            warnings.simplefilter("ignore", InsecureRequestWarning)

    def __exit__(self, type, value, traceback):
        if self.insecure:
            warnings.resetwarnings()


class WOQLClient:
    """Client for querying a TerminusDB server using WOQL queries."""

    def __init__(self, server_url: str, insecure=False, **kwargs) -> None:
        r"""The WOQLClient constructor.

        Parameters
        ----------
        server_url : str
            URL of the server that this client will connect to.
        insecure : bool
            weather or not the connection is insecure. Passing insecure=True will skip HTTPS certificate checking.
        \**kwargs
            Extra configuration options

        """
        self._server_url = server_url.strip("/")
        self._api = f"{self._server_url}/api"
        self._connected = False
        self.insecure = insecure

    def connect(
        self,
        account: str = "admin",
        db: Optional[str] = None,
        remote_auth: str = None,
        key: str = "root",
        user: str = "admin",
        branch: str = "main",
        ref: Optional[str] = None,
        repo: str = "local",
        **kwargs,
    ) -> None:
        r"""Connect to a Terminus server at the given URI with an API key.

        Stores the connection settings and necessary meta-data for the connected server. You need to connect before most database operations.

        Parameters
        ----------
        account: str
            Name of the organization account, default to be "admin"
        db: optional, str
            Name of the database connected
        remote_auth: optional, str
            Remote Auth setting
        key: optional, str
            API key for connecting, default to be "root"
        user: optional, str
            Name of the user, default to be "admin"
        branch: optional, str
            Branch to be connected, default to be "main"
        ref: optional, str
            Ref setting
        repo: optional, str
            Local or remote repo, default to be "local"
        \**kwargs
            Extra configuration options.

        Examples
        -------
        >>> client = WOQLClient("https://127.0.0.1:6363", insecure=True)
        >>> client.connect(key="root", account="admin", user="admin", db="example_db")
        """

        self._account = account
        self._db = db
        self._remote_auth = remote_auth
        self._key = key
        self._user = user
        self._branch = branch
        self._ref = ref
        self._repo = repo

        self._connected = True

        # capabilities = self._dispatch_json("get", self._api)
        # self._uid = capabilities["@id"]
        with NoRequestWarning(self.insecure):
            self._all_avaliable_db = json.loads(
                _finish_reponse(
                    requests.get(
                        self._api, auth=self._auth(), verify=(not self.insecure)
                    )
                )
            )

        #
        # Get the current user's identifier, if logged in to Hub, it will be their email otherwise it will be the user provided
        # if capabilities.get("system:user_identifier"):
        #     self._author = capabilities["system:user_identifier"]["@value"]
        # else:
        #     self._author = self._user

        self._author = self._user

        # if self._db is not None:
        #     self._context = self._get_prefixes()

    def close(self) -> None:
        """Undo connect and close the connection.

        The connection will be unusable from this point forward; an Error (or subclass) exception will be raised if any operation is attempted with the connection, unless connect is call again."""
        self._connected = False

    def _check_connection(self, check_db=True) -> None:
        """Raise connection InterfaceError if not connected
        Defaults to check if a db is connected"""
        if not self._connected:
            raise InterfaceError("Client is not connected to a TerminusDB server.")
        if check_db and self._db is None:
            raise InterfaceError(
                "No database is connected. Please either connect to a database or create a new database."
            )

    def get_commit_history(self, max_history: int = 500) -> list:
        """Get the whole commit history.
                Commit history - Commit id, author of the commit, commit message and the commit time, in the current branch from the current commit, ordered backwards in time, will be returned in a dictionary in the follow format:
                {"commit_id":
                    {"author": "commit_author",
                     "message": "commit_message",
                     "timestamp: <datetime object of the timestamp>" }
                }

                Parameters
                ----------
                max_history: int, optional
                    maximum number of commit that would return, counting backwards from your current commit. Default is set to 500. It need to be nop-negitive, if input is 0 it will still give the last commit.

                Example
                -------
                >>> from terminusdb_client import WOQLClient
                >>> client = WOQLClient("https://127.0.0.1:6363"
                >>> client.connect(db="bank_balance_example")
                >>> client.get_commit_history()
                [{'commit': 's90wike9v5xibmrb661emxjs8k7ynwc', 'author': 'admin', 'message': 'Adding Jane', 'timstamp': datetime.da
        tetime(2020, 9, 3, 15, 29, 34)}, {'commit': '1qhge8qlodajx93ovj67kvkrkxsw3pg', 'author': 'gavin@terminusdb.com', 'm
        essage': 'Adding Jim', 'timstamp': datetime.datetime(2020, 9, 3, 15, 29, 33)}, {'commit': 'rciy1rfu5foj67ch00ow6f6n
        njjxe3i', 'author': 'gavin@terminusdb.com', 'message': 'Update mike', 'timstamp': datetime.datetime(2020, 9, 3, 15,
         29, 33)}, {'commit': 'n4d86u8juzx852r2ekrega5hl838ovh', 'author': 'gavin@terminusdb.com', 'message': 'Add mike', '
        timstamp': datetime.datetime(2020, 9, 3, 15, 29, 33)}, {'commit': '1vk2i8k8xce26p9jpi4zmq1h5vdqyuj', 'author': 'gav
        in@terminusdb.com', 'message': 'Label for balance was wrong', 'timstamp': datetime.datetime(2020, 9, 3, 15, 29, 33)
        }, {'commit': '9si4na9zv2qol9b189y92fia7ac3hbg', 'author': 'gavin@terminusdb.com', 'message': 'Adding bank account
        object to schema', 'timstamp': datetime.datetime(2020, 9, 3, 15, 29, 33)}, {'commit': '9egc4h0m36l5rbq1alr1fki6jbfu
        kuv', 'author': 'TerminusDB', 'message': 'internal system operation', 'timstamp': datetime.datetime(2020, 9, 3, 15,
         29, 33)}]

                Result
                ------
                list
        """
        if max_history < 0:
            raise ValueError("max_history needs to be non-negative.")
        if max_history > 1:
            limit_history = max_history - 1
        else:
            limit_history = 1
        woql_query = (
            WOQLQuery()
            .using("_commits")
            .limit(limit_history)
            .select(
                "v:cid",
                "v:author",
                "v:message",
                "v:timestamp",
                "v:cur_cid",
                "v:cur_author",
                "v:cur_message",
                "v:cur_timestamp",
            )
            .triple("v:branch", "ref:branch_name", self.checkout())
            .triple("v:branch", "ref:ref_commit", "v:commit")
            .woql_or(
                WOQLQuery()
                .path(
                    "v:commit",
                    "ref:commit_parent+",
                    "v:target_commit",
                    "v:path",
                )
                .triple("v:target_commit", "ref:commit_id", "v:cid")
                .triple("v:target_commit", "ref:commit_author", "v:author")
                .triple("v:target_commit", "ref:commit_message", "v:message")
                .triple("v:target_commit", "ref:commit_timestamp", "v:timestamp")
                .triple("v:commit", "ref:commit_id", "v:cur_cid")
                .triple("v:commit", "ref:commit_author", "v:cur_author")
                .triple("v:commit", "ref:commit_message", "v:cur_message")
                .triple("v:commit", "ref:commit_timestamp", "v:cur_timestamp"),
                WOQLQuery()
                .triple("v:commit", "ref:commit_id", "v:cur_cid")
                .triple("v:commit", "ref:commit_author", "v:cur_author")
                .triple("v:commit", "ref:commit_message", "v:cur_message")
                .triple("v:commit", "ref:commit_timestamp", "v:cur_timestamp"),
            )
        )
        result = self.query(woql_query).get("bindings")
        result_item = result[0]
        cid_list = [result_item["cur_cid"]["@value"]]
        result_list = [
            {
                "commit": result_item["cur_cid"]["@value"],
                "author": result_item["cur_author"]["@value"],
                "message": result_item["cur_message"]["@value"],
                "timstamp": datetime.fromtimestamp(
                    int(result_item["cur_timestamp"]["@value"])
                ),
            }
        ]
        if max_history > 1:
            for result_item in result:
                if (
                    result_item["cid"] != "system:unknown"
                    and result_item["cid"]["@value"] not in cid_list
                ):
                    result_list.append(
                        {
                            "commit": result_item["cid"]["@value"],
                            "author": result_item["author"]["@value"],
                            "message": result_item["message"]["@value"],
                            "timstamp": datetime.fromtimestamp(
                                int(result_item["timestamp"]["@value"])
                            ),
                        }
                    )
                    cid_list.append(result_item["cid"]["@value"])
        return result_list

    def _get_current_commit(self):
        woql_query = (
            WOQLQuery()
            .using("_commits")
            .triple("v:branch", "ref:branch_name", self.checkout())
            .triple("v:branch", "ref:ref_commit", "v:commit")
        )
        result = self.query(woql_query)
        current_commit = result.get("bindings")[0].get("commit")
        return current_commit

    def _get_target_commit(self, step):
        woql_query = (
            WOQLQuery()
            .using("_commits")
            .path(
                "v:commit",
                f"ref:commit_parent{{{step},{step}}}",
                "v:target_commit",
                "v:path",
            )
            .triple("v:branch", "ref:branch_name", self.checkout())
            .triple("v:branch", "ref:ref_commit", "v:commit")
            .triple("v:target_commit", "ref:commit_id", "v:cid")
        )
        result = self.query(woql_query)
        target_commit = result.get("bindings")[0].get("cid").get("@value")
        return target_commit

    def rollback(self, steps=1) -> None:
        """Curently not implementated. Please check back later.

        Raises
        ----------
        NotImplementedError
            Since TerminusDB currently does not support open transactions. This method is not applicable to it's usage. To reset commit head, use WOQLClient.reset

        """
        raise NotImplementedError(
            "Open transactions are currently not supported. To reset commit head, check WOQLClient.reset"
        )

    def copy(self) -> "WOQLClient":
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

    def basic_auth(self, key: Optional[str] = None, user: Optional[str] = None):
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
        None
        >>> client.basic_auth("password", "admin")
        'admin:password'
        >>> client.basic_auth()
        'admin:password'
        """
        if not self._connected:
            return None
        if key is not None:
            self._key = key
        if user is not None:
            self._user = user
        return f"{self._user}:{self._key}"

    def remote_auth(self, auth_info: Optional[Dict[str, str]] = None) -> Dict[str, str]:
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
        if not self._connected:
            return None
        if auth_info is not None:
            self._remote_auth = auth_info
        return self._remote_auth

    def set_db(self, dbid: str, account: Optional[str] = None) -> str:
        """Set the connection to another database. This will reset the connection.

        Parameters
        ----------
        dbid : str
            Database identifer to set in the config.
        account : str
            User identifer to set in the config. If not passed in, it will use the current one.

        Returns
        -------
        str
            The current database identifier.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.set_db("database1")
        'database1'
        """
        self._check_connection(check_db=False)

        if account is None:
            account = self._account

        return self.connect(
            account=account,
            db=dbid,
            remote_auth=self._remote_auth,
            key=self._key,
            user=self._user,
            branch=self._branch,
            ref=self._ref,
            repo=self._repo,
        )

    def db(self) -> str:
        """Get the current database.

        Returns
        -------
        str
            The current database identifier.

        Examples
        --------
        >>> client = WOQLClient(""https://127.0.0.1:6363"")
        >>> client.db()
        None
        >>> client.connect('database')
        >>> client.db()
        'database'
        """
        return self._db

    def account(self) -> str:
        """Get the account identifier.

        Returns
        -------
        str
            The current account name.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.account()
        None
        >>> client.account()
        admin
        """
        return self._account

    def user_account(self) -> str:
        """**Deprecatied**

        Get the current user identifier.

        .. deprecated:: 1.0.0

        Returns
        -------
        str
            User identifier.

        """
        warnings.warn("user_account() is deprecated.", DeprecationWarning)
        return self._uid

    def user(self) -> str:
        """Get the current user's information.

        Returns
        -------
        str

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.connect()
        >>> client.user()
        "admin"
        """
        return self._user

    def repo(self, repoid: Optional[str] = None) -> str:
        """Set or get the repository identifier.

        If repoid is not provided, then the config will not be updated.

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
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.repo()
        'local'
        >>> client.repo("repository1")
        repository1
        >>> client.repo()
        repository1
        """
        if repoid:
            self._repo = repoid

        return self._repo

    def ref(self, refid: Optional[str] = None) -> str:
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
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.ref()
        None
        >>> client.ref('main')
        main
        >>> client.ref()
        main
        """
        if refid:
            self._ref = refid
        return self._ref

    def checkout(self, branchid: Optional[str] = None) -> str:
        """Set or get the current branch identifier.

        If branchid is not provided, then the config will not be updated.

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
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.checkout()
        'main'
        >>> client.checkout("other_branch")
        other_branch
        >>> client.checkout()
        other_branch
        """
        if branchid:
            self._branch = branchid
        return self._branch

    def uid(self, ignore_jwt: Optional[bool] = True) -> str:
        """**Deprecated**
        Get the current user identifier.

        .. deprecated:: 1.0.0

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
        >>> client = WOQLClient("https://127.0.0.1:6363")
        >>> client.uid()
        '<uid>'
        >>> client.uid(False)
        '<jwt_uid>'
        """
        warnings.warn("uid() is deprecated.", DeprecationWarning)
        return self._uid

    def resource(self, ttype: str, val: Optional[str] = None) -> str:
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
        >>> client = WOQLClient("https://127.0.0.1:6363")
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
        base = self._account + "/" + self._db + "/"
        if ttype == "db":
            return base
        elif ttype == "meta":
            return base + "_meta"
        base = base + self._repo
        if ttype == "repo":
            return base + "/_meta"
        elif ttype == "commits":
            return base + "/_commits"
        if val is None:
            if ttype == "ref":
                val = self._ref
            else:
                val = self._branch
        if ttype == "branch":
            return base + "/branch/" + val
        if ttype == "ref":
            return base + "/commit/" + val

    def set(self, **kwargs: Dict[str, Any]):  # bad naming
        r"""**deprecated**

        Update multiple config values on the current context.

        .. deprecated:: 1.0.0
            use `connect` instead

        Parameters
        ----------
        \**kwargs
            Dict of config options to set.

        Examples
        --------
        >>> client = WOQLClient("http://localhost:6363")
        >>> client.set({"account": "<account>", "branch": "<branch>"})
        """
        warnings.warn("set() is deprecated; use connect().", DeprecationWarning)
        self.connect(**kwargs)

    def _get_prefixes(self):
        """Get the prefixes for a given database"""
        return self._dispatch_json("get", self._db_base("prefixes")).get("@context")

    def create_database(
        self,
        dbid: str,
        accountid: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        prefixes: Optional[dict] = None,
        include_schema: bool = True,
    ) -> None:
        """Create a TerminusDB database by posting
        a terminus:Database document to the Terminus Server.

        Parameters
        ----------
        dbid : str
            Unique identifier of the database.
        accountid : str, optional
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

        Raises
        ------
        InterfaceError
            if the client does not connect to a server

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.create_database("someDB", "admin", "Database Label", "My Description")
        """

        self._check_connection(check_db=False)

        details: Dict[str, Any] = {}
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
            accountid = self._account

        self._account = accountid
        self._connected = True
        self._db = dbid
        # self._dispatch("post", self._db_url(), details)
        # self._context = self._get_prefixes()

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._db_url(),
                json=details,
                auth=self._auth(),
                verify=(not self.insecure),
            )

    def delete_database(
        self,
        dbid: Optional[str] = None,
        accountid: Optional[str] = None,
        force: bool = False,
    ) -> None:
        """Delete a TerminusDB database.

        If ``accountid`` is provided, then the account in the config will be updated
        and the new value will be used in future requests to the server.

        Parameters
        ----------
        dbid : str
            ID of the database to delete
        accountid : str, optional
            the account id in which the database resides (defaults to "admin")
        force: bool

        Raises
        ------
        UserWarning
            If the value of dbid is None.
        InterfaceError
            if the client does not connect to a server.

        Examples
        -------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.delete_database("<database>", "<account>")
        """

        self._check_connection(check_db=False)

        if dbid is None:
            raise UserWarning(
                f"You are currently using the database: {self._account}/{self._db}. If you want to delete it, please do 'delete_database({self._db},{self._account})' instead."
            )

        self._db = dbid
        if accountid is None:
            warnings.warn(
                f"Delete Database Warning: You have not specify the accountid, assuming {self._account}/{self._db}"
            )
        else:
            self._account = accountid
        payload = {"force": force}
        self._dispatch("delete", self._db_url(), payload)
        self._db = None

    def create_graph(
        self, graph_type: str, graph_id: str, commit_msg: Optional[str] = None
    ) -> None:
        """Create a new graph in the current database context.

        Parameters
        ----------
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        graph_id : str
            Graph identifier.
        commit_msg : str
            Commit message.

        Raises
        ------
        ValueError
            If the value of graph_type is invalid.
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        if graph_type in ["inference", "schema", "instance"]:
            commit = self._generate_commit(commit_msg)
            self._dispatch(
                "post",
                self._graph_url(graph_type, graph_id),
                commit,
            )
        else:
            raise ValueError(
                "Create graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
            )

    def delete_graph(
        self, graph_type: str, graph_id: str, commit_msg: Optional[str] = None
    ) -> None:
        """Delete a graph from the current database context.

        Parameters
        ----------
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        graph_id : str
            Graph identifier.
        commit_msg : str
            Commit message.

        Raises
        ------
        ValueError
            If the value of graph_type is invalid.
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        if graph_type in ["inference", "schema", "instance"]:
            commit = self._generate_commit(commit_msg)
            self._dispatch(
                "delete",
                self._graph_url(graph_type, graph_id),
                commit,
            )
        else:
            raise ValueError(
                "Delete graph parameter error - you must specify a valid graph_type (inference, instance, schema), graph_id and commit message"
            )

    def get_triples(self, graph_type: str, graph_id: str) -> str:
        """Retrieves the contents of the specified graph as triples encoded in turtle format

        Parameters
        ----------
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        graph_id : str
            Graph identifier.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        str
        """
        self._check_connection()
        return self._dispatch(
            "get",
            self._triples_url(graph_type, graph_id),
        )

    def update_triples(
        self, graph_type: str, graph_id: str, turtle, commit_msg: str
    ) -> None:
        """Updates the contents of the specified graph with the triples encoded in turtle format Replaces the entire graph contents

        Parameters
        ----------
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        graph_id : str
            Graph identifier.
        turtle
            Valid set of triples in Turtle format.
        commit_msg : str
            Commit message.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        commit = self._generate_commit(commit_msg)
        commit["turtle"] = turtle
        self._dispatch(
            "post",
            self._triples_url(graph_type, graph_id),
            commit,
        )

    def insert_triples(
        self, graph_type: str, graph_id: str, turtle, commit_msg: Optional[str] = None
    ) -> None:
        """Inserts into the specified graph with the triples encoded in turtle format.

        Parameters
        ----------
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        graph_id : str
            Graph identifier.
        turtle
            Valid set of triples in Turtle format.
        commit_msg : str
            Commit message.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        commit = self._generate_commit(commit_msg)
        commit["turtle"] = turtle
        self._dispatch(
            "put",
            self._triples_url(graph_type, graph_id),
            commit,
        )

    def get_document(self, iri_id: str, graph_type: str = "instance", **kwargs) -> dict:
        """Retrieves the document of the iri_id

        Parameters
        ----------
        iri_id : str
            Iri id for the docuemnt that is retriving
        graph_type : str, optional
            Graph type, either "instance" or "schema".
        kwargs:
            Additional boolean flags for retriving. Currently avaliable: "prefixed", "minimized", "unfold"

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        dict
        """
        add_args = ["prefixed", "minimized", "unfold"]
        self._check_connection()
        payload = {"id": iri_id, "graph_type": graph_type}
        for the_arg in add_args:
            if the_arg in kwargs:
                payload[the_arg] = kwargs[the_arg]

        with NoRequestWarning(self.insecure):
            result = requests.get(
                self._documents_url(graph_type),
                verify=(not self.insecure),
                params=payload,
                auth=self._auth(),
            )
        return json.loads(_finish_reponse(result))

    def get_documents_by_type(
        self,
        doc_type: str,
        graph_type: str = "instance",
        skip: int = 0,
        count: Optional[int] = None,
        **kwargs,
    ) -> Iterable:
        # TODO: make return iterable
        """Retrieves the documents by type

        Parameters
        ----------
        doc_type : str
            Specific type for the docuemnts that is retriving
        graph_type : str, optional
            Graph type, either "instance" or "schema".
        skip: int
            The starting posiion of the returning results, default to be 0
        count: int or None
            The maximum number of returned result, if None (default) it will return all of the avalible result.
        kwargs:
            Additional boolean flags for retriving. Currently avaliable: "prefixed", "unfold"

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        iterable
            Stream of dictionaries
        """
        add_args = ["prefixed", "unfold"]
        self._check_connection()
        payload = {"type": doc_type, "graph_type": graph_type}
        if count is None:
            count = "unlimited"
        payload["skip"] = skip
        payload["count"] = count
        for the_arg in add_args:
            if the_arg in kwargs:
                payload[the_arg] = kwargs[the_arg]
        with NoRequestWarning(self.insecure):
            result = requests.get(
                self._documents_url(graph_type),
                verify=(not self.insecure),
                params=payload,
                auth=self._auth(),
            )
        return _result2stream(_finish_reponse(result))

    def get_all_documents(
        self,
        graph_type: str = "instance",
        skip: int = 0,
        count: Optional[int] = None,
        **kwargs,
    ) -> Iterable:
        # TODO: make return iterable
        """Retrieves all avalibale the documents

        Parameters
        ----------
        graph_type : str, optional
            Graph type, either "instance" or "schema".
        skip: int
            The starting posiion of the returning results, default to be 0
        count: int or None
            The maximum number of returned result, if None (default) it will return all of the avalible result.
        kwargs:
            Additional boolean flags for retriving. Currently avaliable: "prefixed", "unfold"

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        iterable
            Stream of dictionaries
        """
        add_args = ["prefixed", "unfold"]
        self._check_connection()
        payload = {"graph_type": graph_type}
        payload["skip"] = skip
        if count is not None:
            payload["count"] = count
        for the_arg in add_args:
            if the_arg in kwargs:
                payload[the_arg] = kwargs[the_arg]
        with NoRequestWarning(self.insecure):
            result = requests.get(
                self._documents_url(),
                verify=(not self.insecure),
                params=payload,
                auth=self._auth(),
            )
        return _result2stream(_finish_reponse(result))

    def insert_document(
        self,
        document: Union[
            dict, List[dict], "WOQLSchema", "ObjectTemplate", List["ObjectTemplate"]
        ],
        graph_type: str = "instance",
        commit_msg: Optional[str] = None,
    ) -> None:
        """Inserts the specified document(s)

        Parameters
        ----------
        document: dict or list of dict
            Document(s) to be inserted.
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        commit_msg : str
            Commit message.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        list
            list of ids of the inseted docuemnts
        """
        self._check_connection()
        params = self._generate_commit(commit_msg)["commit_info"]
        params["graph_type"] = graph_type

        def conv_to_dict(object):
            if isinstance(object, dict):
                return object
            elif hasattr(object, "to_dict"):
                return object.to_dict()
            elif hasattr(object, "_obj_to_dict"):
                if (
                    not hasattr(object, "_id")
                    and not hasattr(object.__class__, "_subdocument")
                    and hasattr(object.__class__._key, "idgen")
                ):
                    object._id = object.__class__._key.idgen(object)
                return object._obj_to_dict()
            else:
                raise ValueError("Object cannot convert to dictionary")

        if isinstance(document, list):
            new_doc = []
            for item in document:
                # while document:
                #     item = document.pop()
                item_dict = conv_to_dict(item)
                new_doc.append(item_dict)
                # id_list.append(item_dict['@id'])
            document = new_doc
        else:
            document = conv_to_dict(document)
        pp.pprint(document)
        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._documents_url(),
                params=params,
                json=document,
                auth=self._auth(),
                verify=(not self.insecure),
            )
        return json.loads(_finish_reponse(result))

    def replace_document(
        self,
        document: Union[dict, List[dict]],
        graph_type: str,
        commit_msg: Optional[str] = None,
    ) -> None:
        """Updates the specified document(s)

        Parameters
        ----------
        document: dict or list of dict
            Document(s) to be updated.
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        commit_msg : str
            Commit message.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        params = self._generate_commit(commit_msg)["commit_info"]
        params["graph_type"] = graph_type
        with NoRequestWarning(self.insecure):
            _finish_reponse(
                requests.put(
                    self._documents_url(graph_type),
                    params=params,
                    json=document,
                    auth=self._auth(),
                    verify=(not self.insecure),
                )
            )

    def delete_document(
        self,
        doc_id: Union[str, List[str]],
        graph_type: str,
        commit_msg: Optional[str] = None,
    ) -> None:
        """Delete the specified document(s)

        Parameters
        ----------
        doc_id: str or list of str
            Id(s) of document(s) to be updated.
        graph_type : str
            Graph type, either "inference", "instance" or "schema".
        commit_msg : str
            Commit message.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        params = self._generate_commit(commit_msg)["commit_info"]
        params["graph_type"] = graph_type
        with NoRequestWarning(self.insecure):
            _finish_reponse(
                requests.delete(
                    self._documents_url(),
                    params=params,
                    json=doc_id,
                    auth=self._auth(),
                    verify=(not self.insecure),
                )
            )

    # def get_csv(
    #     self,
    #     csv_name: str,
    #     csv_directory: Optional[str] = None,
    #     csv_output_name: Optional[str] = None,
    #     graph_type: Optional[str] = "instance",
    #     graph_id: Optional[str] = "main",
    # ):
    #     """Retrieves the contents of the specified graph as a CSV
    #
    #     Parameters
    #     ----------
    #     csv_name : str
    #         Name of csv to dump from the specified database to extract.
    #     csv_directory : str, optional
    #         CSV output directory path. (defaults to current directory).
    #     csv_output_name: str, optional
    #         CSV output file name. (defaults to same csv name).
    #     graph_type : str
    #         Graph type, either "inference", "instance" or "schema". Default to be "instance"
    #     graph_id : str, optional
    #         Graph identifier. Default to be "main"
    #
    #     Raises
    #     ------
    #     InterfaceError
    #         if the client does not connect to a database
    #     """
    #     self._check_connection()
    #     options = {}
    #     if csv_directory is None:
    #         csv_directory = os.getcwd()
    #     if csv_output_name is None:
    #         csv_output_name = csv_name
    #     options["name"] = csv_name
    #
    #     result = self._dispatch(
    #         "get",
    #         self._csv_url(graph_type, graph_id),
    #         options,
    #     )
    #
    #     stream = open(f"{csv_directory}/{csv_output_name}", "w")
    #     stream.write(result)
    #     stream.close()
    #
    # def update_csv(
    #     self,
    #     csv_paths: Union[str, List[str]],
    #     commit_msg: Optional[str] = None,
    #     graph_type: Optional[str] = "instance",
    #     graph_id: Optional[str] = "main",
    # ) -> None:
    #     """Updates the contents of the specified graph with the csv. Replaces the entire file contents
    #
    #     Parameters
    #     ----------
    #     csv_paths : str or list of str
    #         csv path or list of csv paths to load. (required)
    #     commit_msg : str
    #         Commit message.
    #     graph_type : str
    #         Graph type, either "inference", "instance" or "schema". Default to be "instance"
    #     graph_id : str, optional
    #         Graph identifier. Default to be "main"
    #
    #     Raises
    #     ------
    #     InterfaceError
    #         if the client does not connect to a database
    #     """
    #     self._check_connection()
    #     if commit_msg is None:
    #         commit_msg = f"Update csv from {csv_paths} by python client {__version__}"
    #     commit = self._generate_commit(commit_msg)
    #     if isinstance(csv_paths, str):
    #         csv_paths_list = [csv_paths]
    #     else:
    #         csv_paths_list = csv_paths
    #
    #     self._dispatch(
    #         "post",
    #         self._csv_url(graph_type, graph_id),
    #         commit,
    #         file_list=csv_paths_list,
    #     )
    #
    # def insert_csv(
    #     self,
    #     csv_paths: Union[str, List[str]],
    #     commit_msg: Optional[str] = None,
    #     graph_type: Optional[str] = "instance",
    #     graph_id: Optional[str] = "main",
    # ) -> None:
    #     """Inserts into the specified graph with the csv.
    #
    #     Parameters
    #     ----------
    #     csv_paths : str or list
    #         CSV or list of csvs to upload
    #     commit_msg : str
    #         Commit message.
    #     graph_type : str
    #         Graph type, either "inference", "instance" or "schema". Default to be "instance"
    #     graph_id : str, optional
    #         Graph identifier. Default to be "main"
    #
    #     Raises
    #     ------
    #     InterfaceError
    #         if the client does not connect to a database
    #     """
    #     self._check_connection()
    #     if commit_msg is None:
    #         commit_msg = f"Insert csv from {csv_paths} by python client {__version__}"
    #     commit = self._generate_commit(commit_msg)
    #     if isinstance(csv_paths, str):
    #         csv_paths_list = [csv_paths]
    #     else:
    #         csv_paths_list = csv_paths
    #
    #     self._dispatch(
    #         "put",
    #         self._csv_url(graph_type, graph_id),
    #         commit,
    #         file_list=csv_paths_list,
    #     )

    def commit(self):
        """Not implementated: open transactions currently not suportted. Please check back later."""

    def query(
        self,
        woql_query: Union[dict, WOQLQuery],
        commit_msg: Optional[str] = None,
        # file_dict: Optional[dict] = None,
    ) -> Union[dict, str]:
        """Updates the contents of the specified graph with the triples encoded in turtle format Replaces the entire graph contents

        Parameters
        ----------
        woql_query : dict or WOQLQuery object
            A woql query as an object or dict
        commit_mg : str
            A message that will be written to the commit log to describe the change
        file_dict: **deprecated**
            File dictionary to be associated with post name => filename, for multipart POST

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Examples
        -------
        >>> WOQLClient(server="http://localhost:6363").query(woql, "updating graph")

        Returns
        -------
        dict
        """
        self._check_connection()
        query_obj = self._generate_commit(commit_msg)
        if isinstance(woql_query, WOQLQuery):
            request_woql_query = woql_query.to_dict()
        else:
            request_woql_query = woql_query
        # if request_woql_query.get("@context") and isinstance(
        #     request_woql_query.get("@context"), dict
        # ):
        #     request_woql_query["@context"].update(self._context)
        # else:
        #     request_woql_query["@context"] = self._context
        query_obj["query"] = request_woql_query
        # request_file_dict: Optional[Dict[str, Tuple[str, Union[str, BinaryIO], str]]]
        # if file_dict is not None and type(file_dict) is dict:
        #     request_file_dict = {}
        #     for name in query_obj:
        #         query_obj_value = query_obj[name]
        #         request_file_dict[name] = (
        #             name,
        #             json.dumps(query_obj_value),
        #             "application/json",
        #         )
        #     file_list = []
        #     for name in file_dict:
        #         file_list.append(os.path.join(file_dict[name], name))
        #         # path = file_dict[name]
        #         # request_file_dict[name] = (name, open(path, "rb"), "application/binary")
        #     payload = None
        # else:
        #     file_list = None
        #     payload = query_obj

        # result = self._dispatch_json(
        #     "post",
        #     self._query_url(),
        #     payload,
        #     file_list,
        # )
        # if result.get("inserts") or result.get("deletes"):
        #     return "Commit successfully made."
        # return result

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._query_url(),
                json=query_obj,
                auth=self._auth(),
                verify=(not self.insecure),
            )
        fin_reqult = json.loads(_finish_reponse(result))

        if fin_reqult.get("inserts") or fin_reqult.get("deletes"):
            return "Commit successfully made."
        return fin_reqult

    def branch(self, new_branch_id: str, empty: bool = False) -> None:
        """Create a branch starting from the current branch.

        Parameters
        ----------
        new_branch_id : str
            New branch identifier.
        empty : bool
            Create an empty branch if true (no starting commit)

        Raises
        ------
        InterfaceError
            if the client does not connect to a database
        """
        self._check_connection()
        if empty:
            source = {}
        elif self._ref:
            source = {
                "origin": f"{self._account}/{self._db}/{self._repo}/commit/{self._ref}"
            }
        else:
            source = {
                "origin": f"{self._account}/{self._db}/{self._repo}/branch/{self._branch}"
            }

        # self._dispatch("post", self._branch_url(new_branch_id), source)

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._branch_url(new_branch_id),
                json=source,
                auth=self._auth(),
                verify=(not self.insecure),
            )

    def pull(
        self,
        remote: str = "origin",
        remote_branch: Optional[str] = None,
        message: Optional[str] = None,
        author: Optional[str] = None,
    ) -> dict:
        """Pull updates from a remote repository to the current database.

        Parameters
        ----------
        remote: str
            remote to pull from, default "origin"
        remote_branch: str, optional
            remote branch to pull from, default to be your current barnch
        message: str, optional
            optional commit message
        author: str, optional
            option to overide the author of the operation

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.pull()
        """
        self._check_connection()
        if remote_branch is None:
            remote_branch = self._branch
        if author is None:
            author = self._author
        if message is None:
            message = (
                f"Pulling from {remote}/{remote_branch} by Python client {__version__}"
            )
        rc_args = {
            "remote": remote,
            "remote_branch": remote_branch,
            "author": author,
            "message": message,
        }

        # return self._dispatch_json(
        #     "post",
        #     self._pull_url(),
        #     rc_args,
        # )

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._pull_url(),
                json=rc_args,
                auth=self._auth(),
                verify=(not self.insecure),
            )

        return json.loads(_finish_reponse(result))

    def fetch(self, remote_id: str) -> dict:
        """Fatch the brach from a remote

        Parameters
        ----------
        remote_id: str
            id of the remote

        Raises
        ------
        InterfaceError
            if the client does not connect to a database"""
        self._check_connection()
        # return self._dispatch_json("post", self._fetch_url(remote_id))

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._fetch_url(remote_id),
                auth=self._auth(),
                verify=(not self.insecure),
            )

        return json.loads(_finish_reponse(result))

    def push(
        self,
        remote: str = "origin",
        remote_branch: Optional[str] = None,
        message: Optional[str] = None,
        author: Optional[str] = None,
    ) -> dict:
        """Push changes from a branch to a remote repo

        Parameters
        ----------
        remote: str
            remote to push to, default "origin"
        remote_branch: str, optional
            remote branch to push to, default to be your current barnch
        message: str, optional
            optional commit message
        author: str, optional
            option to overide the author of the operation

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Examples
        -------
        >>> WOQLClient(server="http://localhost:6363").push(remote="origin", remote_branch = "main", author = "admin", message = "commit message"})

        Returns
        -------
        dict
        """
        self._check_connection()
        if remote_branch is None:
            remote_branch = self._branch
        if author is None:
            author = self._author
        if message is None:
            message = (
                f"Pushing to {remote}/{remote_branch} by Python client {__version__}"
            )
        rc_args = {
            "remote": remote,
            "remote_branch": remote_branch,
            "author": author,
            "message": message,
        }
        # return self._dispatch_json("post", self._push_url(), rc_args)

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._push_url(),
                json=rc_args,
                auth=self._auth(),
                verify=(not self.insecure),
            )

        return json.loads(_finish_reponse(result))

    def rebase(
        self,
        rebase_source: str,
        message: Optional[str] = None,
        author: Optional[str] = None,
    ) -> dict:
        """Rebase the current branch onto the specified remote branch.

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        rebase_source : str
            the source branch for the rebase
        message : str, optional
            the commit message
        author : str, optional
            the commit author

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Returns
        -------
        dict

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.rebase("the_branch")
        """
        self._check_connection()

        if author is None:
            author = self._author
        if message is None:
            message = f"Rebase from {rebase_source} by Python client {__version__}"
        rc_args = {"rebase_from": rebase_source, "author": author, "message": message}
        # return self._dispatch_json("post", self._rebase_url(), rc_args)

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._rebase_url(),
                json=rc_args,
                auth=self._auth(),
                verify=(not self.insecure),
            )

        return json.loads(_finish_reponse(result))

    def reset(self, commit: str, use_path: bool = False) -> None:
        """Reset the current branch HEAD to the specified commit path. Doing it will reset the internal commit counter (self._commit_made) back to zero.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        commit: string
            Commit id or path to the commit (if use_path is True), for instance '234980523ffaf93' or 'admin/database/local/commit/234980523ffaf93'.
        use_path : bool
            Wheather or not the commit given is an id or path. Default using id and use_path is False.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.checkout("some_branch")
        >>> client.reset('234980523ffaf93')
        >>> client.reset('admin/database/local/commit/234980523ffaf93', use_path=True)
        """

        self._check_connection()
        if use_path:
            commit_path = commit
        else:
            commit_path = f"{self._account}/{self._db}/{self._repo}/commit/{commit}"
        # self._dispatch(
        #     "post",
        #     self._reset_url(),
        #     {"commit_descriptor": commit_path},
        # )

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._reset_url(),
                json={"commit_descriptor": commit_path},
                auth=self._auth(),
                verify=(not self.insecure),
            )

    def optimize(self, path: str) -> None:
        """Optimize the specified path.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        path : string
            Path to optimize, for instance admin/database/_meta for the repo graph.

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.optimize('admin/database/_meta')
        """
        self._check_connection()
        # self._dispatch("post", self._optimize_url(path))

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._optimize_url(path),
                auth=self._auth(),
                verify=(not self.insecure),
            )

    def squash(
        self, message: Optional[str] = None, author: Optional[str] = None
    ) -> dict:
        """Squash the current branch HEAD into a commit

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Notes
        -----
        The "remote" repo can live in the local database.

        Parameters
        ----------
        message : string
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
        self._check_connection()
        # commit_object = self._generate_commit(message, author)
        # return self._dispatch_json("post", self._squash_url(), commit_object)

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._squash_url(),
                json=self._generate_commit(message, author),
                auth=self._auth(),
                verify=(not self.insecure),
            )

        return json.loads(_finish_reponse(result))

    def clonedb(
        self, clone_source: str, newid: str, description: Optional[str] = None
    ) -> None:
        """Clone a remote repository and create a local copy.

        Parameters
        ----------
        clone_source : str
            The source url of the repo to be cloned.
        newid : str
            Identifier of the new repository to create.
        Description : str, optional
            Optional description about the cloned database.

        Raises
        ------
        InterfaceError
            if the client does not connect to a database

        Examples
        --------
        >>> client = WOQLClient("https://127.0.0.1:6363/")
        >>> client.clonedb("http://terminusdb.com/some_user/test_db", "my_test_db")
        """
        self._check_connection()
        if description is None:
            description = f"New database {newid}"
        rc_args = {"remote_url": clone_source, "label": newid, "comment": description}
        # self._dispatch("post", self._clone_url(newid), rc_args)

        with NoRequestWarning(self.insecure):
            result = requests.post(
                self._clone_url(newid),
                json=rc_args,
                auth=self._auth(),
                verify=(not self.insecure),
            )

    def _generate_commit(
        self, msg: Optional[str] = None, author: Optional[str] = None
    ) -> dict:
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
            mes_author = self._author
        if not msg:
            msg = f"Commit via python client {__version__}"
        ci = {"commit_info": {"author": mes_author, "message": msg}}
        return ci

    def _dispatch_json(
        self,
        action: str,  # get, post, put, delete
        url: str,
        payload: Optional[dict] = None,
        file_list: Optional[list] = None,
    ) -> dict:
        """Directly dispatch to a TerminusDB database with the returned result parsed into a dictionary.

        Parameters
        ----------
        action
            The action to perform on the server. It will be one of the followig: get, post, put, delete
        url : str
            The server URL to point the action at.
        payload : dict, optional
            Payload to send to the server.
        file_list : list, optional
            List of files to include in the query.

        Returns
        -------
        dict
            Dictionary convered from the json string that is passed from a successful dispatch call.
        """
        result = self._dispatch(action, url, payload, file_list)
        return json.loads(result)

    def _auth(self):
        if self._connected and self._key and self._user:
            return (self._user, self._key)
        # TODO: remote_auth

    def _dispatch(
        self,
        action: str,  # get, post, put, delete
        url: str,
        payload: Optional[dict] = None,
        file_list: Optional[list] = None,
        data: Optional[list] = None,
    ) -> str:
        """Directly dispatch to a TerminusDB database.

        Parameters
        ----------
        action
            The action to perform on the server. It will be one of the followig: get, post, put, delete
        url : str
            The server URL to point the action at.
        payload : dict, optional
            Payload to send to the server.
        file_list : list, optional
            List of files to include in the query.

        Returns
        -------
        str
            If it sccessed (status code 200) then it will return a json string that is convertable to a dictionary.
        """

        # check if we can perform this action or raise an AccessDeniedError error
        # review the access control
        # self.conCapabilities.capabilitiesPermit(action)
        # url, action, payload={}, basic_auth, jwt=None, file_dict=None)

        if payload is None:
            payload = {}
        if file_list is None:
            file_list = []
        request_response = None
        headers = {}
        # url = utils.add_params_to_url(url, payload)
        if url[:17] == "https://127.0.0.1" or url[:7] == "http://" or self.insecure:
            verify = False
        else:
            verify = True

        if not verify:
            warnings.simplefilter("ignore", InsecureRequestWarning)

        # if (payload and ('terminus:user_key' in  payload)):
        # utils.encodeURIComponent(payload['terminus:user_key'])}
        basic_auth = self.basic_auth()
        remote_auth = self.remote_auth()
        if basic_auth:
            headers["Authorization"] = "Basic %s" % b64encode(
                (basic_auth).encode("utf-8")
            ).decode("utf-8")
        if remote_auth and remote_auth["type"] == "jwt":
            headers["Authorization-Remote"] = "Bearer %s" % remote_auth["key"]
        elif remote_auth and remote_auth["type"] == "basic":
            rauthstr = remote_auth["user"] + ":" + remote_auth["key"]
            headers["Authorization-Remote"] = "Basic %s" % b64encode(
                (rauthstr).encode("utf-8")
            ).decode("utf-8")

        if action == "get":
            request_response = requests.get(
                url, headers=headers, verify=verify, params=payload
            )

        elif action == "delete":
            request_response = requests.delete(
                url, headers=headers, verify=verify, json=payload
            )

        elif action in ["post", "put"]:

            if file_list:
                file_dict = {}
                streams = []
                for path in file_list:
                    name = os.path.basename(os.path.normpath(path))
                    stream = open(path, "rb")
                    file_dict[name] = (name, stream, "application/binary")
                    streams.append(stream)
                file_dict["payload"] = (
                    "payload",
                    json.dumps(payload),
                    "application/json",
                )
                try:
                    if action == "post":
                        request_response = requests.post(
                            url,
                            headers=headers,
                            files=file_dict,
                            verify=verify,
                            params=payload,
                        )
                    else:
                        request_response = requests.put(
                            url,
                            headers=headers,
                            files=file_dict,
                            verify=verify,
                            params=payload,
                        )
                finally:
                    # Close the files
                    for stream in streams:
                        stream.close()
            else:
                # headers["content-type"] = "application/json"
                if action == "post":
                    request_response = requests.post(
                        url,
                        json=payload,
                        headers=headers,
                        verify=verify,
                        # params=payload,
                    )
                else:
                    request_response = requests.put(
                        url,
                        json=payload,
                        headers=headers,
                        verify=verify,
                        # params=payload,
                    )
        else:
            raise ValueError("action needs to be 'get', 'post', 'put' or 'delete'")

        warnings.resetwarnings()
        if request_response.status_code == 200:
            return request_response.text  # if not a json not it raises an error
        elif request_response.status_code > 399 and request_response.status_code < 599:
            raise DatabaseError(request_response)

    def get_database(self, dbid: str, account: str) -> Optional[dict]:
        """
        Returns metadata (id, organization, label, comment) about the requested database
        Parameters
        ----------
        dbid : str
            The id of the database
        account : str
            The account / organization id that the user is acting through

        Raises
        ------
        InterfaceError
            if the client does not connect to a server

        Returns
        -------
        dict or None if not found
        """
        self._check_connection(check_db=False)
        db_ids = []
        all_dbs = []
        for this_db in self.get_databases():
            if this_db["system:resource_name"]["@value"] == dbid:
                db_ids.append(this_db["@id"])
                all_dbs.append(this_db)

        resources_ids = []
        for scope in self._dispatch_json("get", self._api)["system:role"][
            "system:capability"
        ]["system:capability_scope"]:
            if (
                scope["@type"] == "system:Organization"
                and scope["system:organization_name"]["@value"] == account
            ):
                if type(scope["system:resource_includes"]) is list:
                    for resource in scope["system:resource_includes"]:
                        resources_ids.append(resource["@id"])

        target_db = None
        for target in set(db_ids).intersection(set(resources_ids)):
            target_db = target

        for this_db in all_dbs:
            if this_db["@id"] == target_db:
                return this_db

    def get_databases(self) -> List[Dict]:
        """
        Returns a list of database metadata records for all databases the user has access to

        Raises
        ------
        InterfaceError
            if the client does not connect to a server

        Returns
        -------
        list of dicts
        """
        self._check_connection(check_db=False)
        all_dbs = []
        for scope in self._dispatch_json("get", self._api)["system:role"][
            "system:capability"
        ]["system:capability_scope"]:
            if scope["@type"] == "system:Database":
                all_dbs.append(scope)
        return all_dbs

    def list_databases(self) -> List[Dict]:
        """
        Returns a list of database ids for all databases the user has access to

        Raises
        ------
        InterfaceError
            if the client does not connect to a server

        Returns
        -------
        list of dicts
        """
        self._check_connection(check_db=False)
        all_data = self.get_databases()
        all_dbs = []
        for data in all_data:
            all_dbs.append(data["system:resource_name"]["@value"])
        return all_dbs

    def get_metadata(self, dbid: str, account):
        """
        **Deprecated**

        Alias of get_database above - deprecated - included for backwards compatibility

        .. deprecated:: 1.0.0
            use `get_database()` instead
        """
        warnings.warn(
            "get_metadata() is deprecated; use get_database().",
            DeprecationWarning,
        )
        return self.get_database(dbid, account)

    def server(self) -> str:
        """
        Returns the URL of the currently connected server
        """
        return self._server_url

    def api(self) -> str:
        """
        Returns the URL of the currently connected server
        """
        return self._api

    def _db_url_fragment(self):
        if self._db == "_system":
            return self._db
        return f"{self._account}/{self._db}"

    def _db_base(self, action: str):
        return f"{self._api}/{action}/{self._db_url_fragment()}"

    def _branch_url(self, branch_id: str):
        base_url = self._repo_base("branch")
        return f"{base_url}/branch/{branch_id}"

    def _repo_base(self, action: str):
        return self._db_base(action) + f"/{self._repo}"

    def _branch_base(self, action: str):
        base = self._repo_base(action)
        if self._repo == "_meta":
            return base
        if self._branch == "_commits":
            return base + f"/{self._branch}"
        elif self._ref:
            return base + f"/commit/{self._ref}"
        else:
            return base + f"/branch/{self._branch}"
        return base

    def _schema_url(self, sgid="main"):
        if self._db == "_system":
            schema = self._db_base("schema")
        else:
            schema = self._branch_base("schema")
        return schema + f"/{sgid}"

    def _query_url(self):
        if self._db == "_system":
            return self._db_base("woql")
        return self._branch_base("woql")

    def _class_frame_url(self):
        if self._db == "_system":
            return self._db_base("frame")
        return self._branch_base("frame")

    def _csv_url(self, graph_type="instance", graph_id="main"):
        if self._db == "_system":
            base_url = self._db_base("csv")
        else:
            base_url = self._branch_base("csv")
        return f"{base_url}/{graph_type}/{graph_id}"

    def _documents_url(self):
        if self._db == "_system":
            base_url = self._db_base("document")
        else:
            base_url = self._branch_base("document")
        return base_url

    def _triples_url(self, graph_type="instance", graph_id="main"):
        if self._db == "_system":
            base_url = self._db_base("triples")
        else:
            base_url = self._branch_base("triples")
        return f"{base_url}/{graph_type}/{graph_id}"

    def _clone_url(self, new_repo_id: str):
        return f"{self._api}/clone/{self._account}/{new_repo_id}"

    def _cloneable_url(self):
        crl = f"{self._server_url}/{self._account}/{self._db}"
        return crl

    def _pull_url(self):
        return self._branch_base("pull")

    def _fetch_url(self, remote_name: str):
        furl = self._branch_base("fetch")
        return furl + "/" + remote_name + "/_commits"

    def _rebase_url(self):
        return self._branch_base("rebase")

    def _reset_url(self):
        return self._branch_base("reset")

    def _optimize_url(self, path: str):
        return f"{self._api}/optimize/{path}"

    def _squash_url(self):
        return self._branch_base("squash")

    def _push_url(self):
        return self._branch_base("push")

    def _db_url(self):
        return self._db_base("db")

    def _graph_url(self, graph_type: str, gid: str):
        return self._branch_base("graph") + f"/{graph_type}/{gid}"

    """
    Unstable / Experimental Endpoints

    The below API endpoints are not yet officially released

    They are part of the server API (not desktop) and will be finalized and
    officially released when that package is released. They should be considered
    unreliable and unstable until then and use is unsupported and at your own risk
    """

    def get_class_frame(self, class_name):
        self._check_connection()
        opts = {"class": class_name}
        return self.dispatch(
            "get",
            self._class_frame_url(),
            opts,
        )
