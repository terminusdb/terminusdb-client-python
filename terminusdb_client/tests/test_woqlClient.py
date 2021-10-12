# import sys
# sys.path.append('woqlclient')
import json
import unittest.mock as mock

import pytest
import requests

from terminusdb_client.errors import InterfaceError
from terminusdb_client.woqlclient import WOQLClient
from terminusdb_client.woqlschema import WOQLSchema

from ..__version__ import __version__
from .woqljson.woqlStarJson import WoqlStar


class MockResponse:
    def __init__(self, text, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.json_data


def mocked_requests_get(*args, **kwargs):

    if "http://localhost:6363/" in args[0]:
        return MockResponse(
            json.dumps(
                [
                    {
                        "@id": "UserDatabase_48965a1628f9748db159df4ebacf3eca",
                        "@type": "UserDatabase",
                        "comment": "",
                        "creation_date": "2021-08-10T12:30:44.565Z",
                        "label": "myDBName",
                        "name": "myDBName",
                        "state": "finalized",
                    }
                ]
            ),
            {"key1": "value1"},
            200,
        )

    return MockResponse(None, {}, 404)


def mocked_requests_get2(*args, **kwargs):

    if "http://localhost:6363/" in args[0]:
        return MockResponse(
            json.dumps(
                [
                    {
                        "@id": "UserDatabase_48965a1628f9748db159df4ebacf3eca",
                        "@type": "UserDatabase",
                        "comment": "",
                        "creation_date": "2021-08-10T12:30:44.565Z",
                        "label": "my DB",
                        "name": "my DB",
                        "state": "finalized",
                    }
                ]
            ),
            {"key1": "value1"},
            200,
        )

    return MockResponse(None, {}, 404)


def mocked_requests_post(*args, **kwargs):
    # class MockResponse:
    #     def __init__(self, text, json_data, status_code):
    #         self.json_data = json_data
    #         self.status_code = status_code
    #         self.text = text
    #
    #     def json(self):
    #         return self.json_data

    if "http://localhost:6363/" in args[0]:
        mock_result = {
            "@type": "api:WoqlResponse",
            "api:status": "api:success",
            "api:variable_names": [],
            "bindings": [{}],
            "deletes": 0,
            "inserts": 1,
            "transaction_retry_count": 0,
        }
        return MockResponse(json.dumps(mock_result), {"key1": "value1"}, 200)

    return MockResponse(None, {}, 404)


def mock_func_with_1arg(_):
    return True


def mock_func_with_2arg(first, second):
    return True


def mock_func_no_arg():
    return True


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_connection(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")

    # before connect it connection is empty

    woql_client.connect(key="root", team="admin", user="admin")

    requests.get.assert_called_once_with(
        "http://localhost:6363/api/",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_connected_flag(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    assert not woql_client._connected
    woql_client.connect(key="root", team="admin", user="admin")
    assert woql_client._connected
    woql_client.close()
    assert not woql_client._connected


@mock.patch("requests.post", side_effect=mocked_requests_get)
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_create_database(mocked_requests, mocked_requests2):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    woql_client.connect()
    assert woql_client.user == "admin"

    woql_client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/db/admin/myFirstTerminusDB",
        auth=("admin", "root"),
        json={"label": "my first db", "comment": "my first db comment"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.post", side_effect=mocked_requests_get)
@mock.patch("requests.get", side_effect=mocked_requests_get)
# @mock.patch("terminusdb_client.woqlclient.woqlClient.WOQLClient.create_graph")
def test_create_database_with_schema(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect()
    woql_client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=True,
    )
    requests.post.assert_called_once_with(
        "http://localhost:6363/api/db/admin/myFirstTerminusDB",
        auth=("admin", "root"),
        json={"label": "my first db", "comment": "my first db comment", "schema": True},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.post", side_effect=mocked_requests_get)
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_create_database_and_change_team(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root")
    woql_client.create_database(
        "myFirstTerminusDB",
        "my_new_team",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/db/my_new_team/myFirstTerminusDB",
        auth=("admin", "root"),
        json={"label": "my first db", "comment": "my first db comment"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.get", side_effect=mocked_requests_get)
@mock.patch("requests.post", side_effect=mocked_requests_get)
def test_branch(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root", db="myDBName")
    woql_client.create_branch("my_new_branch")

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/branch/admin/myDBName/local/branch/my_new_branch",
        auth=("admin", "root"),
        json={"origin": "admin/myDBName/local/branch/main"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.get", side_effect=mocked_requests_get2)
@mock.patch("requests.post", side_effect=mocked_requests_get)
def test_crazy_branch(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="amazing admin", key="root", db="my DB")
    woql_client.create_branch("my new branch")

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/branch/amazing%20admin/my%20DB/local/branch/my%20new%20branch",
        auth=("admin", "root"),
        json={"origin": "amazing admin/my DB/local/branch/main"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


# @mock.patch("requests.get", side_effect=mocked_requests_get)
# @mock.patch("requests.post", side_effect=mocked_requests_get)
# def test_wrong_graph_type(mocked_requests, mocked_requests2):
#     woql_client = WOQLClient("http://localhost:6363")
#     woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
#
#     with pytest.raises(ValueError):
#         woql_client.create_graph("wrong_graph_name", "mygraph", "add a new graph")


@pytest.mark.skip(reason="temporary not avaliable")
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_get_triples(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root", db="myDBName")

    woql_client.get_triples("instance")

    requests.get.assert_called_with(
        "http://localhost:6363/api/triples/admin/myDBName/local/branch/main/instance",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.post", side_effect=mocked_requests_post)
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_query(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root", db="myDBName")

    # WoqlStar is the query in json-ld

    woql_client.query(WoqlStar, commit_msg="commit msg")

    requests.post.assert_called_once_with(
        "http://localhost:6363/api/woql/admin/myDBName/local/branch/main",
        auth=("admin", "root"),
        json={
            "commit_info": {
                "author": "admin",
                "message": "commit msg",
            },
            "query": WoqlStar,
        },
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_query_nodb(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root")
    with pytest.raises(InterfaceError):
        woql_client.query(WoqlStar)


@mock.patch("requests.get", side_effect=mocked_requests_get)
@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_query_commit_made(mocked_execute, mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root", db="myDBName")
    result = woql_client.query(WoqlStar)
    assert result == "Commit successfully made."


@mock.patch("requests.post", side_effect=mocked_requests_get)
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_delete_database(mocked_requests, mocked_requests2):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", key="root", team="admin")

    woql_client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    with pytest.raises(UserWarning):
        woql_client.delete_database()


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_rollback(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root")
    with pytest.raises(NotImplementedError):
        woql_client.rollback()


def test_copy_client():
    woql_client = WOQLClient("http://localhost:6363")
    copy_client = woql_client.copy()
    assert id(woql_client) != copy_client


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_basic_auth(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(user="admin", team="admin", key="root")
    assert woql_client._key == "root"
    assert woql_client.team == "admin"
    assert woql_client.user == "admin"


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_remote_auth(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    auth_setting = {"type": "jwt", "user": "admin", "key": "<token>"}
    woql_client.connect(
        user="admin", team="admin", key="root", remote_auth=auth_setting
    )
    result = woql_client._remote_auth
    assert result == auth_setting


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_set_db(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    with pytest.raises(InterfaceError):
        woql_client.set_db("myDBName")
    woql_client.connect()
    woql_client.set_db("myDBName")
    assert woql_client.db == "myDBName"
    assert woql_client.repo == "local"


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_full_replace_fail(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(db="myDBName")
    with pytest.raises(ValueError):
        woql_client.insert_document(
            [{"not_context": "no context provided"}], full_replace=True
        )


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_insert_woqlschema_fail(mocked_requests):
    woql_client = WOQLClient("http://localhost:6363")
    woql_client.connect(db="myDBName")
    with pytest.raises(InterfaceError):
        woql_client.insert_document(WOQLSchema(), graph_type="instance")


@mock.patch("requests.delete", side_effect=mocked_requests_get)
@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_delete_document(mocked_requests, mocked_requests2, test_schema):
    woql_client = WOQLClient(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    woql_client.connect(db="myDBName")

    woql_client.delete_document(["id1", "id2"])

    requests.delete.assert_called_with(
        "http://localhost:6363/api/document/admin/myDBName/local/branch/main",
        auth=("admin", "root"),
        json=["id1", "id2"],
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        params={
            "author": "admin",
            "graph_type": "instance",
            "message": f"Commit via python client {__version__}",
        },
    )

    woql_client.delete_document("id1")

    requests.delete.assert_called_with(
        "http://localhost:6363/api/document/admin/myDBName/local/branch/main",
        auth=("admin", "root"),
        json=["id1"],
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        params={
            "author": "admin",
            "graph_type": "instance",
            "message": f"Commit via python client {__version__}",
        },
    )
    my_schema = test_schema
    Coordinate = my_schema.object.get("Coordinate")
    home = Coordinate(_id="Coordinate/home", x=123.431, y=342.435)

    woql_client.delete_document(home)

    requests.delete.assert_called_with(
        "http://localhost:6363/api/document/admin/myDBName/local/branch/main",
        auth=("admin", "root"),
        json=["Coordinate/home"],
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        params={
            "author": "admin",
            "graph_type": "instance",
            "message": f"Commit via python client {__version__}",
        },
    )

    woql_client.delete_document(home._obj_to_dict())

    requests.delete.assert_called_with(
        "http://localhost:6363/api/document/admin/myDBName/local/branch/main",
        auth=("admin", "root"),
        json=["Coordinate/home"],
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        params={
            "author": "admin",
            "graph_type": "instance",
            "message": f"Commit via python client {__version__}",
        },
    )
