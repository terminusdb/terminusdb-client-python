# import sys
# sys.path.append('woqlclient')
import json
import unittest.mock as mock

import pytest
import requests
from terminusdb_client.woqlclient.woqlClient import WOQLClient

from .mockResponse import mocked_requests
from .woqljson.woqlStarJson import WoqlStar

# def test_realCall():
# resp=WOQLClient.directDeleteDatabase("http://localhost:6363/test0009","root")
# print('test_realCall',resp)


def mock_func_with_1arg(_):
    return True


def mock_func_with_2arg(first, second):
    return True


def mock_func_no_arg():
    return True


def test_connection_error():
    # this test is weird
    WOQLClient("http://localhost:6363")
    print("___MOCKED______", mocked_requests("http://...").status_code)


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connection(mocked_requests, monkeypatch):

    __woql_client__ = WOQLClient("http://localhost:6363")

    # before connect it connection is empty
    assert __woql_client__.conCapabilities.connection == {}

    # response = __woql_client__.connect(key="mykey", account="admin", user="admin")

    requests.get.assert_called_once_with(
        "http://localhost:6363/", headers={"Authorization": "Basic OmFkbWluOm15a2V5"}
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_create_database(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient(
        "http://localhost:6363", user="admin", key="mykey", account="admin"
    )
    __woql_client__.connect()
    assert __woql_client__.basic_auth() == "admin:mykey"

    __woql_client__.create_database("myFirstTerminusDB", "my first db")

    requests.post.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={
            "Authorization": "Basic OmFkbWluOm15a2V5",
            "content-type": "application/json",
        },
        json={
            "label": "my first db",
            "comment": "my first db",
            "prefixes": {
                "scm": "terminus://admin/myFirstTerminusDB/schema#",
                "doc": "terminus://admin/myFirstTerminusDB/data/",
            },
        },
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_create_database_and_change_account(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient(
        "http://localhost:6363", user="admin", key="mykey", account="admin"
    )
    __woql_client__.connect()
    __woql_client__.create_database(
        "myFirstTerminusDB", "my first db", accountid="my_new_account"
    )

    requests.post.assert_called_once_with(
        "http://localhost:6363/db/my_new_account/myFirstTerminusDB",
        headers={
            "Authorization": "Basic OmFkbWluOm15a2V5",
            "content-type": "application/json",
        },
        json={
            "label": "my first db",
            "comment": "my first db",
            "prefixes": {
                "scm": "terminus://my_new_account/myFirstTerminusDB/schema#",
                "doc": "terminus://my_new_account/myFirstTerminusDB/data/",
            },
        },
    )

    __woql_client__.basic_auth() == "admin:mykey"

    __woql_client__.create_database("myFirstTerminusDB", "my first db")


@mock.patch("requests.delete", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_delete_database(mocked_requests, mocked_requests2, monkeypatch):
    __woql_client__ = WOQLClient("http://localhost:6363")

    __woql_client__.connect(user="admin", account="admin", key="mykey")

    monkeypatch.setattr(
        __woql_client__.conCapabilities, "capabilities_permit", mock_func_with_1arg
    )

    monkeypatch.setattr(
        __woql_client__.conCapabilities, "remove_db", mock_func_with_2arg
    )

    __woql_client__.delete_database("myFirstTerminusDB")

    requests.delete.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={"Authorization": "Basic OmFkbWluOm15a2V5"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_branch(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient("http://localhost:6363")
    __woql_client__.connect(user="admin", account="admin", key="mykey", db="myDBName")
    __woql_client__.branch("my_new_branch")

    requests.post.assert_called_once_with(
        "http://localhost:6363/branch/admin/myDBName/local/branch/my_new_branch",
        headers={
            "Authorization": "Basic OmFkbWluOm15a2V5",
            "content-type": "application/json",
        },
        json={"origin": "admin/myDBName/local/branch/master"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_create_graph(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient("http://localhost:6363")
    __woql_client__.connect(user="admin", account="admin", key="mykey", db="myDBName")

    __woql_client__.create_graph("instance", "mygraph", "add a new graph")

    requests.post.assert_called_once_with(
        "http://localhost:6363/graph/admin/myDBName/local/branch/master/instance/mygraph",
        headers={
            "Authorization": "Basic OmFkbWluOm15a2V5",
            "content-type": "application/json",
        },
        json={"commit_info": {"author": "admin", "message": "add a new graph"}},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.post", side_effect=mocked_requests)
def test_wrong_graph_type(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient("http://localhost:6363")
    __woql_client__.connect(user="admin", account="admin", key="mykey", db="myDBName")

    with pytest.raises(ValueError):
        __woql_client__.create_graph("wrong_graph_name", "mygraph", "add a new graph")


@mock.patch("requests.get", side_effect=mocked_requests)
@mock.patch("requests.delete", side_effect=mocked_requests)
def test_delete_graph(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient("http://localhost:6363")
    __woql_client__.connect(user="admin", account="admin", key="mykey", db="myDBName")

    __woql_client__.delete_graph("instance", "mygraph", "add a new graph")

    requests.delete.assert_called_once_with(
        "http://localhost:6363/graph/admin/myDBName/local/branch/master/instance/mygraph?author=admin&message=add+a+new+graph",
        headers={"Authorization": "Basic OmFkbWluOm15a2V5"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
def test_get_triples(mocked_requests):
    __woql_client__ = WOQLClient("http://localhost:6363")
    __woql_client__.connect(user="admin", account="admin", key="mykey", db="myDBName")

    __woql_client__.get_triples("instance", "mygraph")

    requests.get.assert_called_with(
        "http://localhost:6363/triples/admin/myDBName/local/branch/master/instance/mygraph",
        headers={"Authorization": "Basic OmFkbWluOm15a2V5"},
    )


@mock.patch("requests.post", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_query(mocked_requests, mocked_requests2):
    __woql_client__ = WOQLClient("http://localhost:6363")
    __woql_client__.connect(user="admin", account="admin", key="mykey", db="myDBName")

    # WoqlStar is the query in json-ld

    __woql_client__.query(WoqlStar)

    requests.post.assert_called_once_with(
        "http://localhost:6363/woql/admin/myDBName/local/branch/master",
        headers={
            "Authorization": "Basic OmFkbWluOm15a2V5",
            "content-type": "application/json",
        },
        json={
            "commit_info": {"author": "admin", "message": "Automatically Added Commit"},
            "query": json.dumps(WoqlStar),
        },
    )
