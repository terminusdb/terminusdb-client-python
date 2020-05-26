# connectionConfig.py
from .idParser import IDParser
from copy import copy


class ConnectionConfig:

    def __init__(self, **kwargs):

        """
          client configuration options - connected_mode = true
          tells the client to first connect to the server before invoking other services
        """

        self.server = False
        self.jwt_token = False #jwt token for authenticating to remote servers for push / fetch / clone
        self.jwt_user = False #user id associated with the jwt token
        self.basic_auth = False # basic auth string for authenticating to local server
        #these operate as cursors - where within the connected server context, we currently are
        self.accountid = False
        self.dbid = False

        self.default_branch_id = "master"
        self.default_repo_id = "local"
        #default repository and branch ids
        self.branchid = self.default_branch_id
        self.repoid = self.default_repo_id
        #set if pointing at a commit within a branch
        self.refid = False

        self.connection_error = False

        self.update(**kwargs)

    def copy(self):
        return copy(self)

    def update(self, **kwargs):
        if 'server' in kwargs:
            self.set_server(kwargs['server'])
        if 'account' in kwargs:
            self.set_account(kwargs['account'])
        if 'db' in kwargs:
            self.set_db(kwargs['db'])
        if 'jwt' in kwargs:
            self.set_jwt(kwargs['jwt'], kwargs['jwt_user'])
        #if 'key' in kwargs and 'user' in kwargs:
        #    self.set_key(kwargs['key'], kwargs['user'])
        if 'branch' in kwargs:
            self.set_branch(kwargs['branch'])
        if 'ref' in kwargs:
            self.set_ref(kwargs['ref'])
        if 'repo' in kwargs:
            self.set_repo(kwargs['repo'])

    @property
    def server_url(self):
        return self.server

    @property
    def db(self):
        return self.dbid

    @property
    def branch(self):
        return self.branchid

    @property
    def ref(self):
        return self.refid

    @property
    def account(self):
        return self.accountid

    @property
    def repo(self):
        return self.repoid

    @property
    def key(self):
        return self.basic_auth

    @property
    def jwt(self):
        return self.jwt_token

    @property
    def user(self, ignore_jwt):
        if (not ignore_jwt and self.jwt_user):
            return self.jwt_user
        if self.basic_auth:
            return self.basic_auth.split(":")[0]

    @property
    def db_url_fragment(self):
        if self.db == "terminus":
            return self.db
        return self.account + "/" + self.db

    def db_base(self, action):
        return f"{self.server_url}{action}/{self.db_url_fragment}"

    def repo_base(self, action):
        base = self.db_base(action)
        if self.repo:
            base = base + f"/{self.repo}"
        else:
            base = base + "/" + self.default_repo_id
        return base

    def branch_base(self, action):
        base = self.repo_base(action)
        if self.repo == "_meta":
            return base
        if self.branch == "_commits":
            return base + f"/{self.branch}"
        elif self.ref:
            return base + f"/commit/{self.ref}"
        elif self.branch:
            return base + f"/branch/{self.branch}"
        else:
            base = base + "/branch/" + self.default_branch_id
        return base

    def schema_url(self, sgid):
        if self.db == "terminus":
            schema = self.db_base("schema")
        else:
            schema = this.branch_base("schema")
        if sgid is not None:
            schema = schema + f"/{sgid}"
        return schema

    @property
    def query_url(self):
        if self.db == "terminus":
            return self.db_base("woql")
        return self.branch_base("woql")

    @property
    def class_frame_url(self):
        if self.db == "terminus":
            return self.db_base("frame")
        return self.branch_base("frame")

    def clone_url(self, new_repo_id=None):
        crl = f"{self.serverURL}clone/{self.account}"
        if new_repo_id is not None:
            crl = crl + f"/${new_repo_id}"
        return crl

    def fetch_url(self, repoid=None):
        if repoid is None:
            repoid = self.repo
        return self.db_base("fetch") + f"/{repoid}"

    def rebase_url(self, source_repo= None, source_branch=None):
        purl = self.branch_base("rebase")
        if source_repo is not None:
            purl = purl + f"/{source_repo}"
            if source_branch is not None:
                purl = purl + f"/{source_branch}"
        return purl

    def push_url(self, target_repo=None, target_branch=None):
        purl = self.branch_base("push")
        if target_repo is not None:
            purl = prul + f"/{target_repo}"
            if target_branch is not None:
                purl = purl + f"/{target_branch}"
        return purl

    @property
    def db_url(self):
        return self.db_base("db")

    def graph_url(self, type, gid):
        return self.branch_base("graph") + f"/{type}/{gid}"

    """
      Utility functions for setting and parsing urls and determining
      the current server, database and document
    """

    def clear_cursor(self):
        self.branchid = self.default_branch_id
        self.repoid = self.default_repo_id
        self.accountid = False
        self.dbid = False
        self.refid = False

    def set_cursor(self, account=None, db=None, repo=None, branch=None, ref=None):
        if accoint is not None and not self.set_account(account):
            return False
        if db is not None and not self.set_db(db):
            return False
        if repo is not None and not self.set_repo(repo):
            return False
        if branch is not None and not self.set_branch(branch):
            return False
        if ref is not None and not self.set_ref(ref):
            return False
        return True

    def set_server(self, input_str):
        parser = IDParser()
        surl = parser.parse_server_url(input_str)
        if surl:
            self.server = surl
            return self.server
        self.set_error(f"Invalid Server URL: {inputStr}")

    def set_server_connection(self, surl, key=None, jwt=None):
        if self.set_server(surl):
            if key is not None:
                if not self.set_key(key):
                    return False
            if jwt is not None:
                if not self.set_jwt(jwt):
                    return False
            return True
        return False

    def set_account(self, input_str=None):
        if input_str is None:
            self.accountid = False
            return False
        parser = IDParser()
        aid = parser.parse_dbid(input_str)
        if aid:
            self.accountid = aid
            return self.accountid
        self.set_error(f"Invalid Account ID: {inputStr}")

    def set_db(self, input_str=None):
        if input_str is None:
            self.dbid = Flase
            return False
        parser = IDParser()
        dbid = parser.parse_dbid(input_str)
        if dbid:
            self.dbid = dbid
            return self.dbid
        self.set_error(f"Invalid Database ID: {inputStr}")

    def set_repo(self, input_str=None):
        if input_str is None:
            self.repoid = self.default_repo_id
            return self.repoid
        parser = IDParser()
        repoid = parser.parse_dbid(input_str)
        if repoid:
            self.repoid = repoid
            return self.repoid
        self.set_error(f"Invalid Repo ID: {input_str}")

    def set_branch(self, input_str=None):
        if input_str is None:
            self.branchid = self.default_branch_id
            return self.branchid
        parser = IDParser()
        bid = parser.parse_dbid(input_str)
        if bid:
            self.branchid = bid
            return self.branchid
        self.set_error(f"Invalid Branch ID: {input_str}")

    def set_key(self, input_str=None, uid=None):
        if input_str is None:
            self.basic_auth = False
            return False
        uid = udi if uid is not None else "admin"
        parser = IDParser()
        key = parser.parse_key(input_str)
        if key:
            self.rebase_url = f'{uid}:{key}'
            return self.basic_auth
        self.set_error(f"Invalid API Key: {input_str}")

    def set_ref(self, input_str=None):
        if input_str is not None:
            parser = IDParser()
            bid = parser.parse_dbid(input_str)
            if bid:
                self.refid = bid
                return self.refid
                self.set_error(f"Invalid Branch ID: {input_str}")
        self.refid = False
        return self.refid

    def set_key(self, input_str=None, uid=None):
        if input_str is None:
            self.basic_auth = False
            return False
        if uid is None:
            uid = "admin"
        parser = IDParser()
        key = parser.parse_key(input_str)
        if key:
            self.basic_auth = f"{uid}:{key}"
            return self.basic_auth
        self.set_error(f"Invalid API Key: {input_str}")

    def set_jwt(self, input_str=None, user_id=None):
        if input_str is None:
            self.jwt_token = False
            if user_id is not None:
                self.jwt_user = user_id
            else:
                self.jwt_user = False
        parser = IDParser()
        jwt = parser.parse_jwt(input_str)
        if jwt:
            if user_id is not None:
                self.jwt_user = user_id
                self.jwt_token = jwt
                return self.jwt_token
        self.set_error(f"Invalid JWT: {input_str}")
