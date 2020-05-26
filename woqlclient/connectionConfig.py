# connectionConfig.py
from .idParser import IDParser
from copy import copy


class ConnectionConfig:

    def __init__(self, server_url,**kwargs):

        """
          client configuration options - connected_mode = true
          tells the client to first connect to the server before invoking other services
        """

        self.__server = False
        self.__jwt_token = False #jwt token for authenticating to remote servers for push / fetch / clone
        self.__jwt_user = False #user id associated with the jwt token
        self.__basic_auth = False # basic auth string for authenticating to local server
        #these operate as cursors - where within the connected server context, we currently are
        self.__accountid = False
        self.__dbid = False

        self.__default_branch_id = "master"
        self.__default_repo_id = "local"
        #default repository and branch ids
        self.__branchid = self.__default_branch_id
        self.__repoid = self.__default_repo_id 
        #set if pointing at a commit within a branch
        self.__refid = False

        #self.connection_error = False

        #set the serverUrl
        parser = IDParser()
        surl = parser.parse_server_url(server_url)
        if surl:
            self.__server = surl
        else:
            raise ValueError(f"Invalid Server URL: {server_url}")

        self.update(**kwargs)

    def copy(self):
        return copy(self)

    def update(self, **kwargs):
        #if 'server' in kwargs:
            #self.server_url = kwargs['server']
        if 'account' in kwargs:
            self.account= kwargs['account']
        if 'db' in kwargs:
            self.db = kwargs['db']
        
        if 'jwt' in kwargs:
            self.set_jwt(kwargs['jwt'], kwargs['jwt_user'])
        #if 'key' in kwargs and 'user' in kwargs:
        #    self.set_key(kwargs['key'], kwargs['user'])
        if 'branch' in kwargs:
            self.branch = kwargs['branch']
        if 'ref' in kwargs:
            self.ref = kwargs['ref']
        if 'repo' in kwargs:
            self.repo = kwargs['repo']

    @property
    def server_url(self):
        return self.__server

    @property
    def db(self):
        return self.__dbid

    @property
    def branch(self):
        return self.__branchid

    @property
    def ref(self):
        return self.__refid

    @property
    def account(self):
        return self.__accountid

    @property
    def repo(self):
        return self.__repoid

    @property
    def key(self):
        return self.__basic_auth

    @property
    def jwt(self):
        return self.__jwt_token

    @property
    def user(self, ignore_jwt):
        if (not ignore_jwt and self.__jwt_user):
            return self.__jwt_user
        if self.__basic_auth:
            return self.__basic_auth.split(":")[0]

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
            base = base + "/" + self.__default_repo_id 
        return base

    def branch_base(self, action):
        base = self.repo_base(action)
        print(self.ref);
        if self.repo == "_meta":
            return base
        if self.branch == "_commits":
            return base + f"/{self.branch}"
        elif self.ref:
            return base + f"/commit/{self.ref}"
        elif self.branch:
            return base + f"/branch/{self.branch}"
        else:
            base = base + "/branch/" + self.__default_branch_id
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

    def graph_url(self, graph_type, gid):
        return self.branch_base("graph") + f"/{graph_type}/{gid}"

    """
      Utility functions for setting and parsing urls and determining
      the current server, database and document
    """

    def clear_cursor(self):
        self.__branchid = self.__default_branch_id
        self.__repoid = self.__default_repo_id 
        self.__accountid = False
        self.__dbid = False
        self.__refid = False


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

    @account.setter
    def account(self, input_str):
        if input_str is None:
            self.__accountid = False
            return None
        parser = IDParser()
        aid = parser.parse_dbid(input_str)
        if aid:
            self.__accountid = aid
            return self.__accountid
        self.set_error(f"Invalid Account ID: {inputStr}")

    @db.setter
    def db(self, input_str):
        if input_str is None:
            self.__dbid = False
            return None
        parser = IDParser()
        dbid = parser.parse_dbid(input_str)
        if dbid:
            self.__dbid = dbid
        else:
            raise ValueError(f"Invalid Database ID: {inputStr}")

    @repo.setter
    def repo(self, input_str):
        if input_str is None:
            self.__repoid = self.__default_repo_id 
            return None
        parser = IDParser()
        repoid = parser.parse_dbid(input_str)
        if repoid:
            self.__repoid = repoid
        else:
            raise ValueError(f"Invalid Repo ID: {input_str}")   
    
    @branch.setter
    def branch(self, input_str):
        if input_str is None:
            self.__branchid = self.__default_branch_id
            return None
        parser = IDParser()
        bid = parser.parse_dbid(input_str)
        if bid:
            self.__branchid = bid
        else:
            raise ValueError(f"Invalid Branch ID: {input_str}")

            
    #None value is a possible value, in this case we set redid to false 
    @ref.setter
    def ref(self, input_str):
        if input_str is not None:
            parser = IDParser()
            bid = parser.parse_dbid(input_str)
            if bid:
                self.__refid = bid
            else:
                raise ValueError(f"Invalid ref ID: {input_str}")
        else:        
            self.__refid = False

    def set_key(self, api_key=None, uid=None):
        if api_key is None:
            self.__basic_auth = False
            return False
        if uid is None:
            uid = "admin"
        if key:
            self.__basic_auth = f"{uid}:{key}"
            return self.__basic_auth
        self.set_error(f"Invalid API Key: {api_key}")

    def set_jwt(self, jwt_str=None, user_id=None):
        if jwt_str is None:
            self.__jwt_token = False
            if user_id is not None:
                self.__jwt_user = user_id
            else:
                self.__jwt_user = False
        if jwt:
            if user_id is not None:
                self.__jwt_user = user_id
                self.__jwt_token = jwt
                return self.__jwt_token
        self.set_error(f"Invalid JWT: {input_str}")
