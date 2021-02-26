import secrets
import string

import pytest

from terminusdb_client.woqlclient.connectionConfig import ConnectionConfig


@pytest.mark.skip(reason="deprecated")
class TestConnectionConfig:
    start_server_url = "http://localhost:6363/"
    start_dbid = "testDB"
    local_user = "admin"
    # Set of random string values that can as replacements for dummy id valuess
    # i.e accountid,branchid,refid etc
    id_value = "".join(
        secrets.choice(string.ascii_uppercase + string.ascii_lowercase)
        for _ in range(16)
    )
    # to be review !!!!!
    connection_config = ConnectionConfig(
        start_server_url,
        db=start_dbid,
        user=local_user,
        key="mykey",
        account=local_user,
    )

    db_url = "http://localhost:6363/api/db/admin/testDB"

    def test_get_sever_url(self):
        assert self.connection_config.server == self.start_server_url
        assert self.connection_config.db_url() == self.db_url

    def test_change_branch(self):
        self.connection_config.branch = "myBranch"
        assert self.connection_config.db_url() == self.db_url
        assert (
            self.connection_config.query_url()
            == "http://localhost:6363/api/woql/admin/testDB/local/branch/myBranch"
        )

    def test_change_server(self):
        new_ref = "gfhfjkflfgorpyuiioo"
        self.connection_config.ref = new_ref
        assert (
            self.connection_config.query_url()
            == "http://localhost:6363/api/woql/admin/testDB/local/commit/" + new_ref
        )

    def test_check_basic_auth(self):
        assert self.connection_config.basic_auth == "admin:mykey"

    def test_set_remote_auth(self):
        auth_dict = {type: "jwt", "key": "eyJhbGciOiJIUzI1NiIsInR5c"}
        self.connection_config.set_remote_auth(auth_dict)
        assert self.connection_config.remote_auth == auth_dict
        auth_dict = {
            type: "basic",
            "user": self.local_user,
            "key": "admin_testDB_Password",
        }
        self.connection_config.update(remote_auth=auth_dict)
        assert self.connection_config.remote_auth == auth_dict

    def test_update(self):
        self.connection_config.update(db=self.id_value)
        self.connection_config.update(account=self.id_value)
        self.connection_config.update(repo=self.id_value)
        self.connection_config.update(branch=self.id_value)
        self.connection_config.update(ref=self.id_value)
        self.connection_config.update(repo=self.id_value)
        assert self.connection_config.db == self.id_value
        assert self.connection_config.account == self.id_value
        assert self.connection_config.repo == self.id_value
        assert self.connection_config.branch == self.id_value
        assert self.connection_config.ref == self.id_value
        assert self.connection_config.repo == self.id_value

    def test_clear_cursor(self):
        self.connection_config.update(branch=self.id_value)
        self.connection_config.update(repo=self.id_value)
        self.connection_config.update(account=self.id_value)
        self.connection_config.update(db=self.id_value)
        self.connection_config.update(ref=self.id_value)
        self.connection_config.clear_cursor()
        assert self.connection_config.branch != self.id_value
        assert self.connection_config.repo != self.id_value
        assert self.connection_config.account is False
        assert self.connection_config.db is False
        assert self.connection_config.ref is False

    def test_user(self):
        assert self.connection_config.user() == self.local_user
        auth_dict = {type: "jwt", "key": "eyJhbGciOiJIUzI1NiIsInR5c"}
        self.connection_config.update(remote=auth_dict)
        assert self.connection_config.user() == self.local_user

    def test_set_basic_auth(self):
        assert self.connection_config.set_basic_auth() is None
        self.connection_config.set_basic_auth(api_key="admin_testDB_Password")
        basic_auth = self.connection_config.basic_auth
        assert basic_auth == "admin:admin_testDB_Password"

    def test_db_url_fragmen(self):
        self.connection_config.update(db=self.id_value)
        self.connection_config.update(account=self.id_value)
        db_url_fragment = self.connection_config.db_url_fragment()
        assert db_url_fragment == f"{self.id_value}/{self.id_value}"

    def test_db_base(self):
        self.connection_config.update(db=self.id_value)
        self.connection_config.update(account=self.id_value)
        db_base = self.connection_config.db_base("push")
        assert (
            db_base == f"http://localhost:6363/api/push/{self.id_value}/{self.id_value}"
        )

    def test_repo_base(self):
        self.connection_config.update(db=self.id_value)
        self.connection_config.update(account=self.id_value)
        self.connection_config.db_base("pull")
        default_base = self.connection_config.repo_base("pull")
        assert (
            default_base
            == f"http://localhost:6363/api/pull/{self.id_value}/{self.id_value}/local"
        )

        self.connection_config.update(repo=self.id_value)
        updated_base = self.connection_config.db_base("pull")
        assert (
            updated_base
            == f"http://localhost:6363/api/pull/{self.id_value}/{self.id_value}"
        )

    def test_account(self):
        self.connection_config.account = self.id_value
        assert self.connection_config.account == self.id_value

    def test_db(self):
        self.connection_config.db = self.id_value
        assert self.connection_config.db == self.id_value

    def test_repo(self):
        self.connection_config.repo = self.id_value
        assert self.connection_config.repo == self.id_value

    def branch(self):
        self.connection_config.branch = self.id_value
        assert self.connection_config.branch == self.id_value

    def ref(self):
        self.connection_config.ref = self.id_value
        assert self.connection_config.ref == self.id_value
