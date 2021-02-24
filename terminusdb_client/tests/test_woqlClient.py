# import sys
# sys.path.append('woqlclient')
import unittest.mock as mock

import pytest
import requests
from terminusdb_client.woqlclient.woqlClient import WOQLClient

from .mockResponse import MOCK_CAPABILITIES, mocked_requests
from .woqljson.woqlStarJson import WoqlStar


def mock_func_with_1arg(_):
    return True


def mock_func_with_2arg(first, second):
    return True


def mock_func_no_arg():
    return True


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connection(mocked_requests):

    woql_client = WOQLClient("http://localhost:6363")

    # before connect it connection is empty

    woql_client.connect(key="root", account="admin", user="admin")

    requests.get.assert_called_once_with(
        "http://localhost:6363/api",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
    )


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connected_flag(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    assert not woql_client._connected
    woql_client.connect(key="root", account="admin", user="admin")
    assert woql_client._connected
    woql_client.close()
    assert not woql_client._connected


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
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
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        verify=False,
        json={"label": "my first db", "comment": "my first db comment"},
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
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
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        verify=False,
        json={"label": "my first db", "comment": "my first db comment", "schema": True},
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
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
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        verify=False,
        json={"label": "my first db", "comment": "my first db comment"},
    )

    assert woql_client.basic_auth() == "admin:root"


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_branch(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
    woql_client.branch("my_new_branch")

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/branch/admin/myDBName/local/branch/my_new_branch",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        verify=False,
        json={"origin": "admin/myDBName/local/branch/main"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_wrong_graph_type(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    with pytest.raises(ValueError):
        woql_client.create_graph("wrong_graph_name", "mygraph", "add a new graph")


@mock.patch("requests.get", side_effect=mocked_requests)
def test_get_triples(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    woql_client.get_triples("instance", "mygraph")

    requests.get.assert_called_with(
        "http://localhost:6363/api/triples/admin/myDBName/local/branch/main/instance/mygraph",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_query(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    # WoqlStar is the query in json-ld

    woql_client.query(WoqlStar)

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/woql/admin/myDBName/local/branch/main",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        verify=False,
        json={"query": WoqlStar},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch.object(WOQLClient, "dispatch")
def test_query_commit_count(mocked_execute, mocked_requests):
    mocked_execute.return_value = MOCK_CAPABILITIES
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
    assert woql_client._commit_made == 0
    mocked_execute.return_value = {
        "@type": "api:WoqlResponse",
        "api:status": "api:success",
        "api:variable_names": [],
        "bindings": [{}],
        "deletes": 0,
        "inserts": 1,
        "transaction_retry_count": 0,
    }
    woql_client.query(WoqlStar)
    assert woql_client._commit_made == 1
    woql_client.commit(WoqlStar)
    assert woql_client._commit_made == 0
