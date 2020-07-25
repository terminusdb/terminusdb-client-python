import random
import string
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
        """
        Use hypothesis here to test the values.
        """
        pass
