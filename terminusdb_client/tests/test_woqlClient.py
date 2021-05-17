# import sys
# sys.path.append('woqlclient')
import json
import unittest.mock as mock

import pytest
import requests

from terminusdb_client.__version__ import __version__
from terminusdb_client.errors import DatabaseError, InterfaceError
from terminusdb_client.woqlclient.woqlClient import WOQLClient

from .mockResponse import HEADERS, MOCK_CAPABILITIES
from .woqljson.woqlStarJson import WoqlStar


def mocked_request(response_code=200, *args, **kwargs):
    class MockResponse:
        def __init__(self, text, json_data, status_code):
            self.headers = HEADERS
            self.json_data = json_data
            self.status_code = status_code
            self.text = text

        def json(self):
            return self.json_data

    def wrapper(*args, **kwargs):
        return MockResponse(
            json.dumps(MOCK_CAPABILITIES), {"key1": "value1"}, response_code
        )

    return wrapper


def mock_func_with_1arg(_):
    return True


def mock_func_with_2arg(first, second):
    return True


def mock_func_no_arg():
    return True


@mock.patch("requests.get", side_effect=mocked_request())
def test_connection(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")

    # before connect it connection is empty

    woql_client.connect(key="root", account="admin", user="admin")

    requests.get.assert_called_once_with(
        "http://localhost:6363/api",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        params={},
        verify=False,
    )


@mock.patch("requests.get", side_effect=mocked_request())
def test_connected_flag(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    assert not woql_client._connected
    woql_client.connect(key="root", account="admin", user="admin")
    assert woql_client._connected
    woql_client.close()
    assert not woql_client._connected


@mock.patch("requests.post", side_effect=mocked_request())
@mock.patch("requests.get", side_effect=mocked_request())
def test_create_database(mocked_requests, mocked_requests2):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", key="root", account="admin"
    )
    woql_client.connect()
    assert woql_client.basic_auth() == "admin:root"

    woql_client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/db/admin/myFirstTerminusDB",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
        json={"label": "my first db", "comment": "my first db comment"},
    )


@mock.patch("requests.get", side_effect=mocked_request())
@mock.patch("requests.post", side_effect=mocked_request(response_code=400))
def test_create_db_attempt_when_db_exists(mocked_requests, mocked_requests2):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", key="root", account="admin"
    )
    woql_client.connect()
    assert woql_client.basic_auth() == "admin:root"

    with pytest.raises(DatabaseError):
        woql_client.create_database(
            "myFirstTerminusDB",
            "admin",
            label="my first db",
            description="my first db comment",
            include_schema=False,
        )

    assert woql_client._db is not None
    assert woql_client._context


@mock.patch("requests.post", side_effect=mocked_request())
@mock.patch("requests.get", side_effect=mocked_request())
@mock.patch("terminusdb_client.woqlclient.woqlClient.WOQLClient.create_graph")
def test_create_database_with_schema(
    mocked_requests, mocked_requests2, create_schema_obj
):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", account="admin", key="root"
    )
    woql_client.connect()
    assert woql_client.basic_auth() == "admin:root"

    woql_client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=True,
    )

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/db/admin/myFirstTerminusDB",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
        json={"label": "my first db", "comment": "my first db comment", "schema": True},
    )


@mock.patch("requests.post", side_effect=mocked_request())
@mock.patch("requests.get", side_effect=mocked_request())
def test_create_database_and_change_account(mocked_requests, mocked_requests2):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", account="admin", key="root"
    )
    woql_client.connect()
    woql_client.create_database(
        "myFirstTerminusDB",
        "my_new_account",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/db/my_new_account/myFirstTerminusDB",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
        json={"label": "my first db", "comment": "my first db comment"},
    )

    assert woql_client.basic_auth() == "admin:root"


@mock.patch("requests.get", side_effect=mocked_request())
@mock.patch("requests.post", side_effect=mocked_request())
def test_branch(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
    woql_client.branch("my_new_branch")

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/branch/admin/myDBName/local/branch/my_new_branch",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
        json={"origin": "admin/myDBName/local/branch/main"},
    )


@mock.patch("requests.get", side_effect=mocked_request())
@mock.patch("requests.post", side_effect=mocked_request())
def test_wrong_graph_type(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    with pytest.raises(ValueError):
        woql_client.create_graph("wrong_graph_name", "mygraph", "add a new graph")


@mock.patch("requests.get", side_effect=mocked_request())
def test_get_triples(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    woql_client.get_triples("instance", "mygraph")

    requests.get.assert_called_with(
        "http://localhost:6363/api/triples/admin/myDBName/local/branch/main/instance/mygraph",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
        params={},
    )


@mock.patch("requests.post", side_effect=mocked_request())
@mock.patch("requests.get", side_effect=mocked_request())
def test_query(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    # WoqlStar is the query in json-ld

    woql_client.query(WoqlStar)

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/woql/admin/myDBName/local/branch/main",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
        json={
            "commit_info": {
                "author": "admin",
                "message": f"Commit via python client {__version__}",
            },
            "query": WoqlStar,
        },
    )


@mock.patch("requests.get", side_effect=mocked_request())
def test_query_nodb(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root")
    with pytest.raises(InterfaceError):
        woql_client.query(WoqlStar)


@mock.patch("requests.get", side_effect=mocked_request())
@mock.patch.object(WOQLClient, "_dispatch_json")
def test_query_commit_made(mocked_execute, mocked_requests):
    # mocked_execute.return_value = MOCK_CAPABILITIES
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
    mocked_execute.return_value = {
        "@type": "api:WoqlResponse",
        "api:status": "api:success",
        "api:variable_names": [],
        "bindings": [{}],
        "deletes": 0,
        "inserts": 1,
        "transaction_retry_count": 0,
    }
    result = woql_client.query(WoqlStar)
    assert result == "Commit successfully made."


@mock.patch("requests.post", side_effect=mocked_request())
@mock.patch("requests.get", side_effect=mocked_request())
def test_delete_database(mocked_requests, mocked_requests2):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", key="root", account="admin"
    )
    woql_client.connect()
    assert woql_client.basic_auth() == "admin:root"

    woql_client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    with pytest.raises(UserWarning):
        woql_client.delete_database()


@mock.patch("requests.get", side_effect=mocked_request())
def test_rollback(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root")
    with pytest.raises(NotImplementedError):
        woql_client.rollback()


def test_copy_client():
    woql_client = WOQLClient("http://localhost:6363")
    copy_client = woql_client.copy()
    assert id(woql_client) != copy_client


@mock.patch("requests.get", side_effect=mocked_request())
def test_basic_auth(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    result = woql_client.basic_auth()
    assert result is None
    woql_client.connect(user="admin", account="admin", key="root")
    result = woql_client.basic_auth()
    assert result == "admin:root"
    assert woql_client.account() == "admin"
    assert woql_client.user() == "admin"


@mock.patch("requests.get", side_effect=mocked_request())
def test_remote_auth(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    result = woql_client.remote_auth()
    assert result is None
    woql_client.connect(user="admin", account="admin", key="root")
    result = woql_client.remote_auth()
    assert result is None
    auth_setting = {"type": "jwt", "user": "admin", "key": "<token>"}
    woql_client.remote_auth(auth_setting)
    result = woql_client.remote_auth()
    assert result == auth_setting


@mock.patch("requests.get", side_effect=mocked_request())
def test_set_db(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    with pytest.raises(InterfaceError):
        woql_client.set_db("my_db")
    woql_client.connect()
    woql_client.set_db("my_db")
    assert woql_client._db == "my_db"
    assert woql_client.db() == "my_db"
    assert woql_client.repo() == "local"
