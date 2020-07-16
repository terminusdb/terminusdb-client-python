# import sys
# sys.path.append('woqlclient')
import unittest.mock as mock

import pytest
import requests
from terminusdb_client.woqlclient.woqlClient import WOQLClient

from ..__version__ import __version__
from .mockResponse import mocked_requests
from .woqljson.woqlStarJson import WoqlStar


def mock_func_with_1arg(_):
    return True


def mock_func_with_2arg(first, second):
    return True


def mock_func_no_arg():
    return True


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connection(mocked_requests, monkeypatch):

    woql_client = WOQLClient("http://localhost:6363")

    # before connect it connection is empty
    assert woql_client.conCapabilities.connection == {}

    woql_client.connect(key="root", account="admin", user="admin")

    requests.get.assert_called_once_with(
        "http://localhost:6363/", headers={"Authorization": "Basic YWRtaW46cm9vdA=="}
    )


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
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        json={
            "label": "my first db",
            "comment": "my first db comment",
            "prefixes": {
                "scm": "terminusdb://admin/myFirstTerminusDB/schema#",
                "doc": "terminusdb://admin/myFirstTerminusDB/data/",
            },
        },
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("terminusdb_client.woqlclient.woqlClient.WOQLClient.create_graph")
def test_create_database_with_schema(
    mocked_requests, mocked_requests2, create_schema_obj
):
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
    )

    WOQLClient.create_graph.assert_called_once_with(
        "schema", "main", f"Python client {__version__} message: Creating schema graph"
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_create_database_and_change_account(mocked_requests, mocked_requests2):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", key="root", account="admin"
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
        "http://localhost:6363/db/my_new_account/myFirstTerminusDB",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        json={
            "label": "my first db",
            "comment": "my first db comment",
            "prefixes": {
                "scm": "terminusdb://my_new_account/myFirstTerminusDB/schema#",
                "doc": "terminusdb://my_new_account/myFirstTerminusDB/data/",
            },
        },
    )

    assert woql_client.basic_auth() == "admin:root"


@mock.patch("requests.delete", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_delete_database(mocked_requests, mocked_requests2, monkeypatch):
    woql_client = WOQLClient("http://localhost:6363")

    woql_client.connect(user="admin", account="admin", key="root")

    monkeypatch.setattr(
        woql_client.conCapabilities, "capabilities_permit", mock_func_with_1arg
    )

    monkeypatch.setattr(woql_client.conCapabilities, "remove_db", mock_func_with_2arg)

    woql_client.delete_database("myFirstTerminusDB")

    requests.delete.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_branch(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
    woql_client.branch("my_new_branch")

    requests.post.assert_called_once_with(
        "http://localhost:6363/branch/admin/myDBName/local/branch/my_new_branch",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        json={"origin": "admin/myDBName/local/branch/master"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_create_graph(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    woql_client.create_graph("instance", "mygraph", "add a new graph")

    requests.post.assert_called_once_with(
        "http://localhost:6363/graph/admin/myDBName/local/branch/master/instance/mygraph",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        json={
            "commit_info": {
                "author": "admin Server Admin User",
                "message": "add a new graph",
            }
        },
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_wrong_graph_type(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    with pytest.raises(ValueError):
        woql_client.create_graph("wrong_graph_name", "mygraph", "add a new graph")


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.delete", side_effect=mocked_requests)
def test_delete_graph(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    woql_client.delete_graph("instance", "mygraph", "add a new graph")

    requests.delete.assert_called_once_with(
        "http://localhost:6363/graph/admin/myDBName/local/branch/master/instance/mygraph?author=admin+Server+Admin+User&message=add+a+new+graph",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
def test_get_triples(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    woql_client.get_triples("instance", "mygraph")

    requests.get.assert_called_with(
        "http://localhost:6363/triples/admin/myDBName/local/branch/master/instance/mygraph",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_query(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", account="admin", key="root", db="myDBName")

    # WoqlStar is the query in json-ld

    woql_client.query(WoqlStar)

    requests.post.assert_called_once_with(
        "http://localhost:6363/woql/admin/myDBName/local/branch/master",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        json={"query": WoqlStar},
    )
