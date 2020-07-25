import random
import string
import pytest
from terminusdb_client.woqlclient.connectionConfig import ConnectionConfig


class TestConnectionConfig:
    start_server_url = "http://localhost:6363/"
    start_dbid = "testDB"
    local_user = "admin"
    # to be review !!!!!
    connection_config = ConnectionConfig(
        start_server_url,
        db=start_dbid,
        user=local_user,
        key="mykey",
        account=local_user,
    )

    db_url = "http://localhost:6363/db/admin/testDB"

    def test_get_sever_url(self):
        assert self.connection_config.server == self.start_server_url
        assert self.connection_config.db_url() == self.db_url

    def test_change_branch(self):
        self.connection_config.branch = "myBranch"
        assert self.connection_config.db_url() == self.db_url
        assert (
            self.connection_config.query_url()
            == "http://localhost:6363/woql/admin/testDB/local/branch/myBranch"
        )

    def test_change_server(self):
        new_ref = "gfhfjkflfgorpyuiioo"
        self.connection_config.ref = new_ref
        assert (
            self.connection_config.query_url()
            == "http://localhost:6363/woql/admin/testDB/local/commit/" + new_ref
        )

    def test_check_basic_auth(self):
        assert self.connection_config.basic_auth == "admin:mykey"

    def test_set_remote_auth(self):
        auth_dict = {type: "jwt", "key": "eyJhbGciOiJIUzI1NiIsInR5c"}
        self.connection_config.set_remote_auth(auth_dict)
        assert self.connection_config.remote_auth == auth_dict
        auth_dict = {type: "basic", "user": self.local_user,
                     "key": "admin_testDB_Password"}
        self.connection_config.update(remote_auth=auth_dict)
        assert self.connection_config.remote_auth == auth_dict

    def test_update(self):
        id_value = ''.join(random.choice(
            string.ascii_uppercase + string.ascii_lowercase
        ) for _ in range(16))
        self.connection_config.update(db=id_value)
        self.connection_config.update(account=id_value)
        self.connection_config.update(repo=id_value)
        self.connection_config.update(branch=id_value)
        self.connection_config.update(ref=id_value)
        self.connection_config.update(repo=id_value)
        assert self.connection_config.db == id_value
        assert self.connection_config.account == id_value
        assert self.connection_config.repo == id_value
        assert self.connection_config.branch == id_value
        assert self.connection_config.ref == id_value
        assert self.connection_config.repo == id_value

    def test_clear_cursor(self):
        id_value = ''.join(random.choice(
            string.ascii_uppercase + string.ascii_lowercase
        ) for _ in range(16))
        self.connection_config.update(branch=id_value)
        self.connection_config.update(repo=id_value)
        self.connection_config.update(account=id_value)
        self.connection_config.update(db=id_value)
        self.connection_config.update(ref=id_value)
        self.connection_config.clear_cursor()
        assert self.connection_config.branch != id_value
        assert self.connection_config.repo != id_value
        assert self.connection_config.account is False
        assert self.connection_config.db is False
        assert self.connection_config.ref is False
