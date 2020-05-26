from woqlclient import ConnectionConfig


class TestConnectionConfig:
    start_server_url = "http://localhost:6363/"
    start_dbid = "testDB"
    account = "admin"
    connection_config = ConnectionConfig(
        start_server_url, db=start_dbid, account=account
    )

    db_url = "http://localhost:6363/db/admin/testDB"

    def test_get_sever_url(self):
        assert self.connection_config.server_url == self.start_server_url
        assert self.connection_config.db_url == self.db_url

    def test_change_branch(self):
        self.connection_config.branch = "myBranch"
        assert self.connection_config.db_url == self.db_url
        assert (
            self.connection_config.query_url
            == "http://localhost:6363/woql/admin/testDB/local/branch/myBranch"
        )

    def test_change_server(self):
        new_ref = "gfhfjkflfgorpyuiioo"
        self.connection_config.ref = new_ref
        assert (
            self.connection_config.query_url
            == "http://localhost:6363/woql/admin/testDB/local/commit/" + new_ref
        )
