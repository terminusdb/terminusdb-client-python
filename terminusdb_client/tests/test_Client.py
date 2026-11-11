# import sys
# sys.path.append('client')
import json
import unittest.mock as mock
from datetime import datetime

import pytest
import random
import requests


from terminusdb_client.client import Client, GraphType
from terminusdb_client.client.Client import (
    APITokenAuth,
    JWTAuth,
    Patch,
    WoqlResult,
)
from terminusdb_client.errors import DatabaseError, InterfaceError
from terminusdb_client.woqlschema import WOQLSchema

from ..__version__ import __version__
from .conftest import mocked_request_insert_delete, mocked_request_success
from .woqljson.woqlStarJson import WoqlStar


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_connection(mocked_requests):
    client = Client("http://localhost:6363")

    client.connect(key="root", team="admin", user="admin")

    client._session.get.assert_called_once_with(
        "http://localhost:6363/api/info",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_user_agent_set(mocked_requests):
    client = Client("http://localhost:6363", user_agent="test_user_agent")

    client.connect(key="root", team="admin", user="admin")

    client._session.get.assert_called_once_with(
        "http://localhost:6363/api/info",
        auth=("admin", "root"),
        headers={"user-agent": "test_user_agent"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_connected_flag(mocked_requests):
    client = Client("http://localhost:6363")
    assert not client._connected
    client.connect(key="root", team="admin", user="admin")
    assert client._connected
    client.close()
    assert not client._connected


@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_create_database(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    assert client.user == "admin"

    client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    client._session.post.assert_called_once_with(
        "http://localhost:6363/api/db/admin/myFirstTerminusDB",
        auth=("admin", "root"),
        json={
            "label": "my first db",
            "comment": "my first db comment",
            "schema": False,
        },
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
# @mock.patch("terminusdb_client.woqlclient.woqlClient.WOQLClient.create_graph")
def test_create_database_with_schema(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect()
    client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=True,
    )
    client._session.post.assert_called_once_with(
        "http://localhost:6363/api/db/admin/myFirstTerminusDB",
        auth=("admin", "root"),
        json={"label": "my first db", "comment": "my first db comment", "schema": True},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_create_database_and_change_team(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    client.create_database(
        "myFirstTerminusDB",
        "my_new_team",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    client._session.post.assert_called_once_with(
        "http://localhost:6363/api/db/my_new_team/myFirstTerminusDB",
        auth=("admin", "root"),
        json={
            "label": "my first db",
            "comment": "my first db comment",
            "schema": False,
        },
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_branch(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")
    client.create_branch("my_new_branch")

    client._session.post.assert_called_once_with(
        "http://localhost:6363/api/branch/admin/myDBName/local/branch/my_new_branch",
        auth=("admin", "root"),
        json={"origin": "admin/myDBName/local/branch/main"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_crazy_branch(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="amazing admin", key="root", db="my DB")
    client.create_branch("my new branch")

    client._session.post.assert_called_once_with(
        "http://localhost:6363/api/branch/amazing%20admin/my%20DB/local/branch/my%20new%20branch",
        auth=("admin", "root"),
        json={"origin": "amazing admin/my DB/local/branch/main"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_get_database(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    db_name = "testDB" + str(random.randrange(100000))
    client.create_database(db_name)
    client.get_database(db_name)
    client._session.get.assert_called_with(
        f"http://localhost:6363/api/db/admin/{db_name}?verbose=true",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
def test_has_database(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    db_name = "testDB" + str(random.randrange(100000))
    client.has_database(db_name)
    client._session.head.assert_called_with(
        f"http://localhost:6363/api/db/admin/{db_name}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        allow_redirects=True,
    )


@pytest.mark.skip(reason="temporary not avaliable")
@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_triples(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")

    client.get_triples("instance")

    client._session.get.assert_called_with(
        "http://localhost:6363/api/triples/admin/myDBName/local/branch/main/instance",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@pytest.mark.skip(reason="temporary not avaliable")
@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_triples_with_enum(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")

    client.get_triples(GraphType.INSTANCE)

    client._session.get.assert_called_with(
        "http://localhost:6363/api/triples/admin/myDBName/local/branch/main/instance",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "post", side_effect=mocked_request_insert_delete)
@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_query(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")

    # WoqlStar is the query in json-ld

    client.query(WoqlStar, commit_msg="commit msg")

    client._session.post.assert_called_once_with(
        "http://localhost:6363/api/woql/admin/myDBName/local/branch/main",
        auth=("admin", "root"),
        json={
            "commit_info": {
                "author": "admin",
                "message": "commit msg",
            },
            "query": WoqlStar,
            "streaming": False,
        },
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        stream=False,
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_query_nodb(mocked_requests):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    with pytest.raises(InterfaceError):
        client.query(WoqlStar)


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_insert_delete)
def test_query_commit_made(mocked_execute, mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")
    result = client.query(WoqlStar)
    assert result == "Commit successfully made."


@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_delete_database(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", key="root", team="admin")

    client.create_database(
        "myFirstTerminusDB",
        "admin",
        label="my first db",
        description="my first db comment",
        include_schema=False,
    )

    with pytest.raises(UserWarning):
        client.delete_database()


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_rollback(mocked_requests):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    with pytest.raises(NotImplementedError):
        client.rollback()


def test_copy_client():
    client = Client("http://localhost:6363")
    copy_client = client.copy()
    assert id(client) != copy_client


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_basic_auth(mocked_requests):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    assert client._key == "root"
    assert client.team == "admin"
    assert client.user == "admin"


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_remote_auth(mocked_requests):
    client = Client("http://localhost:6363")
    auth_setting = {"type": "jwt", "user": "admin", "key": "<token>"}
    client.connect(user="admin", team="admin", key="root", remote_auth=auth_setting)
    result = client._remote_auth_dict
    assert result == auth_setting


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_set_db(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    with pytest.raises(InterfaceError):
        client.set_db("myDBName")
    client.connect()
    client.set_db("myDBName")
    assert client.db == "myDBName"
    assert client.repo == "local"


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_full_replace_fail(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(db="myDBName")
    with pytest.raises(ValueError):
        client.insert_document(
            [{"not_context": "no context provided"}], full_replace=True
        )


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_insert_woqlschema_fail(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(db="myDBName")
    with pytest.raises(InterfaceError):
        client.insert_document(WOQLSchema(), graph_type="instance")


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "delete", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_delete_document(
    mocked_requests, mocked_requests2, mocked_requests3, test_schema
):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect(db="myDBName")

    client.delete_document(["id1", "id2"])

    client._session.delete.assert_called_with(
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

    client.delete_document("id1")

    client._session.delete.assert_called_with(
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
    client.delete_document(home)

    client._session.delete.assert_called_with(
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

    client.delete_document(home._obj_to_dict())

    client._session.delete.assert_called_with(
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


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_add_user(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()

    user = "Gavin" + str(random.randrange(100000))
    client.add_user(user, "somePassword")

    client._session.post.assert_called_with(
        "http://localhost:6363/api/users",
        auth=("admin", "root"),
        json={"name": user, "password": "somePassword"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "delete", side_effect=mocked_request_success)
def test_delete_user(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()

    user = "Gavin" + str(random.randrange(100000))
    client.add_user(user, "somePassword")
    client.delete_user(user)

    client._session.delete.assert_called_with(
        f"http://localhost:6363/api/users/{user}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "delete", side_effect=mocked_request_success)
def test_delete_organization(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()

    org = "RandomOrg" + str(random.randrange(100000))
    client.create_organization(org)
    client.delete_organization(org)

    client._session.delete.assert_called_with(
        f"http://localhost:6363/api/organizations/{org}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "put", side_effect=mocked_request_success)
def test_change_user_password(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()

    user = "Gavin" + str(random.randrange(100000))
    client.add_user(user, "somePassword")
    client.change_user_password(user, "newPassword")

    client._session.put.assert_called_with(
        "http://localhost:6363/api/users",
        auth=("admin", "root"),
        json={"name": user, "password": "newPassword"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_create_organization(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()

    org = "RandomOrg" + str(random.randrange(100000))
    client.create_organization(org)

    client._session.post.assert_called_with(
        f"http://localhost:6363/api/organizations/{org}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_organization_users(mocked_requests):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    client.get_organization_users("admin")
    client._session.get.assert_called_with(
        "http://localhost:6363/api/organizations/admin/users",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_organization_user(mocked_requests):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    client.get_organization_user("admin", "admin")
    client._session.get.assert_called_with(
        "http://localhost:6363/api/organizations/admin/users/admin",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_organizations(mocked_requests):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    client.get_organizations()
    client._session.get.assert_called_with(
        "http://localhost:6363/api/organizations",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_capabilities_change(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    capability_change = {
        "operation": "revoke",
        "scope": "UserDatabase/f5a0ef94469b32e1aee321678436c7dfd5a96d9c476672b3282ae89a45b5200e",
        "user": "User/admin",
        "roles": ["Role/consumer", "Role/admin"],
    }
    try:
        client.change_capabilities(capability_change)
    except InterfaceError:
        pass
    client._session.post.assert_called_with(
        "http://localhost:6363/api/capabilities",
        auth=("admin", "root"),
        json=capability_change,
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
def test_add_role(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    role = {
        "name": "Grand Pubah",
        "action": [
            "branch",
            "class_frame",
            "clone",
            "commit_read_access",
            "commit_write_access",
            "create_database",
            "delete_database",
            "fetch",
            "instance_read_access",
            "instance_write_access",
            "manage_capabilities",
            "meta_read_access",
            "meta_write_access",
            "push",
            "rebase",
            "schema_read_access",
            "schema_write_access",
        ],
    }
    try:
        client.add_role(role)
    except InterfaceError:
        pass
    client._session.post.assert_called_with(
        "http://localhost:6363/api/roles",
        auth=("admin", "root"),
        json=role,
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "post", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "put", side_effect=mocked_request_success)
def test_change_role(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    role = {
        "name": "Grand Pubahz",
        "action": [
            "branch",
            "class_frame",
            "clone",
            "commit_read_access",
            "commit_write_access",
            "create_database",
            "delete_database",
            "fetch",
            "instance_read_access",
            "instance_write_access",
            "manage_capabilities",
            "meta_read_access",
            "meta_write_access",
            "push",
            "rebase",
            "schema_read_access",
            "schema_write_access",
        ],
    }
    try:
        client.add_role(role)
        del role["action"][2]  # Delete clone as action
        client.change_role(role)
    except InterfaceError:
        pass
    client._session.put.assert_called_with(
        "http://localhost:6363/api/roles",
        auth=("admin", "root"),
        json=role,
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_roles(mocked_requests):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    try:
        client.get_available_roles()
    except InterfaceError:
        pass
    client._session.get.assert_called_with(
        "http://localhost:6363/api/roles",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_users(mocked_requests):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    try:
        client.get_users()
    except InterfaceError:
        pass
    client._session.get.assert_called_with(
        "http://localhost:6363/api/users",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_user(mocked_requests):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect()
    user = "Gavin" + str(random.randrange(100000))
    client.get_user(user)
    client._session.get.assert_called_with(
        f"http://localhost:6363/api/users/{user}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_document_history(mocked_get, mocked_head):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect(db="myDBName")

    client.get_document_history("Person/Jane", start=0, count=10)

    # Get the last call to get (should be our get_document_history call)
    last_call = client._session.get.call_args_list[-1]
    assert last_call[0][0] == "http://localhost:6363/api/history/admin/myDBName"
    assert last_call[1]["params"] == {"id": "Person/Jane", "start": 0, "count": 10}
    assert last_call[1]["headers"] == {
        "user-agent": f"terminusdb-client-python/{__version__}"
    }
    assert last_call[1]["auth"] == ("admin", "root")


@mock.patch.object(requests.Session, "head", side_effect=mocked_request_success)
@mock.patch.object(requests.Session, "get", side_effect=mocked_request_success)
def test_get_document_history_with_created_updated(mocked_get, mocked_head):
    client = Client("http://localhost:6363", user="admin", key="root", team="admin")
    client.connect(db="myDBName")

    client.get_document_history("Person/Jane", created=True, updated=True)

    # Get the last call to get (should be our get_document_history call)
    last_call = client._session.get.call_args_list[-1]
    assert last_call[0][0] == "http://localhost:6363/api/history/admin/myDBName"
    assert last_call[1]["params"] == {
        "id": "Person/Jane",
        "start": 0,
        "count": 10,
        "created": True,
        "updated": True,
    }
    assert last_call[1]["headers"] == {
        "user-agent": f"terminusdb-client-python/{__version__}"
    }
    assert last_call[1]["auth"] == ("admin", "root")


def test_convert_document_expands_unprefixed_id():
    client = Client("http://localhost:6363")
    docs = client._convert_document(
        [{"@id": "abc123", "@type": "Coordinate", "x": 0.7}], GraphType.INSTANCE
    )
    assert docs[0]["@id"] == "Coordinate/abc123"


def test_convert_document_keeps_prefixed_and_schema_ids():
    client = Client("http://localhost:6363")
    docs = client._convert_document(
        [{"@id": "Coordinate/abc123", "@type": "Coordinate"}], GraphType.INSTANCE
    )
    assert docs[0]["@id"] == "Coordinate/abc123"
    docs = client._convert_document(
        [{"@id": "Coordinate", "@type": "Class"}], "schema"
    )
    assert docs[0]["@id"] == "Coordinate"


def _resp(payload, status=200, text=None, lines=None):
    r = mock.MagicMock()
    r.status_code = status
    r.headers = {
        "content-type": "application/json",
        "Terminusdb-Data-Version": "v0",
    }
    r.text = text if text is not None else json.dumps(payload)
    r.json.return_value = payload
    r.iter_lines.return_value = iter(lines or [])
    return r


def _mock(payload, status=200, text=None):
    return lambda *a, **k: _resp(payload, status, text=text)


def _route(routes):
    def f(url, *a, **k):
        for pat, payload in routes:
            if pat in url:
                return _resp(payload)
        return _resp({})

    return f


INFO_RESPONSE = {
    "@type": "api:InfoResponse",
    "api:info": {
        "authority": "admin",
        "terminusdb": {"version": "11.0.0"},
    },
    "api:status": "api:success",
}


def _connect(client, **kwargs):
    kwargs.setdefault("user", "admin")
    kwargs.setdefault("key", "root")
    kwargs.setdefault("team", "admin")
    with mock.patch.object(
        requests.Session, "get", side_effect=_mock(INFO_RESPONSE)
    ):
        client.connect(**kwargs)
    return client


def _client():
    client = _connect(Client("http://localhost:6363"), repo="local")
    client.branch = "main"
    client.db = "db"
    return client


class TestAuthClasses:
    def test_jwt_auth_sets_bearer_header(self):
        req = mock.Mock()
        req.headers = {}
        JWTAuth("tok")(req)
        assert req.headers["Authorization"] == "Bearer tok"

    def test_api_token_auth_sets_token_header(self):
        req = mock.Mock()
        req.headers = {}
        APITokenAuth("tok")(req)
        assert req.headers["Authorization"] == "Token tok"


class TestWoqlResult:
    def _lines(self, *docs):
        return iter(json.dumps(d) for d in docs)

    def test_iterates_bindings_and_captures_postscript(self):
        result = WoqlResult(
            self._lines(
                {"@type": "PrefaceRecord", "names": ["v:x"]},
                {"@type": "Binding", "v:x": 1},
                {"@type": "Binding", "v:x": 2},
                {"@type": "PostscriptRecord", "done": True},
            )
        )
        assert result.variable_names() == ["v:x"]
        rows = list(result)
        assert len(rows) == 2
        assert rows[0]["v:x"] == 1
        assert result.postscript == {"@type": "PostscriptRecord", "done": True}

    def test_rejects_non_preface_first_line(self):
        with pytest.raises(DatabaseError) as exc:
            WoqlResult(self._lines({"@type": "SomethingElse"}))
        assert exc.value.error_obj["@type"] == "SomethingElse"

    def test_rejects_document_without_type(self):
        result = WoqlResult(
            self._lines(
                {"@type": "PrefaceRecord", "names": []},
                {"not": "a typed document"},
            )
        )
        with pytest.raises(DatabaseError):
            next(result)


class TestPatch:
    def test_update_extracts_after_values(self):
        patch = Patch(
            json.dumps(
                {
                    "name": {"@op": "SwapValue", "@before": "a", "@after": "b"},
                    "nested": {"deep": {"@op": "SwapValue", "@after": 5}},
                }
            )
        )
        assert patch.update == {"name": "b", "nested": {"deep": 5}}

    def test_before_extracts_before_values(self):
        patch = Patch(
            json.dumps(
                {
                    "name": {"@op": "SwapValue", "@before": "a", "@after": "b"},
                    "other": "plain",
                    "nested": {"deep": {"@before": 1}},
                }
            )
        )
        assert patch.before == {"name": "a", "other": "plain", "nested": {"deep": 1}}

    def test_to_json_and_copy_round_trip(self):
        patch = Patch(json.dumps({"a": {"@before": 1}}))
        clone = patch.copy()
        assert json.loads(clone.to_json()) == json.loads(patch.to_json())

    def test_properties_reject_set_and_delete(self):
        patch = Patch(json.dumps({"a": 1}))
        for prop in ("update", "before"):
            with pytest.raises(Exception):
                setattr(patch, prop, None)
            with pytest.raises(Exception):
                delattr(patch, prop)


class TestClientProperties:
    def test_team_quotes_and_unquotes(self):
        client = Client("http://localhost:6363")
        client.team = "my team"
        assert client.team == "my team"
        assert client._team == "my%20team"

    def test_db_branch_repo_ref_accessors(self):
        client = Client("http://localhost:6363")
        client.db = "mydb"
        client.branch = "dev"
        client.repo = "origin"
        client.ref = "abc123"
        assert client.db == "mydb"
        assert client.branch == "dev"
        assert client.repo == "origin"
        assert client.ref == "abc123"

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    def test_ok_reports_connection_state(self, _m):
        client = Client("http://localhost:6363")
        assert client.ok() is False
        _connect(client)
        assert client.ok() is True


class TestClientMethods:
    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock([{"timestamp": 1, "identifier": "abc"}]),
    )
    def test_log_and_histories(self, _m):
        client = _client()
        commits = client.log()
        assert commits[0]["identifier"] == "abc"
        assert commits[0]["commit"] == "abc"
        assert isinstance(commits[0]["timestamp"], datetime)
        assert client.log(team="t", db="d", start=1, count=5)[0]["identifier"] == "abc"
        assert isinstance(client.get_commit_history(), (dict, list))
        assert isinstance(
            client.get_document_history("doc/x", start=1, count=3, created=True),
            (dict, list),
        )
        assert isinstance(
            client.get_document_history("doc/x", updated=True), (dict, list)
        )

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_route(
            [
                ("prefix/", {"api:prefix_uri": "http://ex/"}),
                ("prefix", {"ex": "http://ex/"}),
            ]
        ),
    )
    @mock.patch.object(requests.Session, "post", side_effect=_mock({"inserts": 0}))
    @mock.patch.object(requests.Session, "put", side_effect=_mock({"inserts": 0}))
    @mock.patch.object(requests.Session, "delete", side_effect=_mock({"inserts": 0}))
    def test_prefix_crud(self, _d, _u, _p, _g):
        client = _client()
        assert client._get_prefixes() == {"ex": "http://ex/"}
        assert client.get_prefix("ex") == "http://ex/"
        client.add_prefix("ex", "http://x/")
        client.update_prefix("ex", "http://y/")
        client.upsert_prefix("ex", "http://z/")
        client.delete_prefix("ex")

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock([], text="[]"),
    )
    @mock.patch.object(requests.Session, "put", side_effect=_mock({"inserts": 0}))
    @mock.patch.object(requests.Session, "post", side_effect=_mock({"inserts": 0}))
    def test_triples_methods(self, _p, _u, _g):
        client = _client()
        client.get_triples(GraphType.INSTANCE)
        client.update_triples(GraphType.INSTANCE, "<a> <b> <c>", "msg")
        client.insert_triples(GraphType.INSTANCE, "<a> <b> <c>", "msg")

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock({"@id": "doc/x"}, text='{"@id": "doc/x"}'),
    )
    @mock.patch.object(
        requests.Session,
        "post",
        side_effect=_mock({"@id": "doc/x"}, text='{"@id": "doc/x"}'),
    )
    def test_document_reads(self, _p, _g):
        client = _client()
        assert client.query_document({"@type": "Person"}, as_list=True) == [
            {"@id": "doc/x"}
        ]
        assert client.get_document("doc/x") == {"@id": "doc/x"}
        assert client.get_documents_by_type("Person", as_list=True) == [
            {"@id": "doc/x"}
        ]
        assert client.get_all_documents(as_list=True, doc_type="Person") == [
            {"@id": "doc/x"}
        ]
        assert client.get_class_frame("Person") is not None
        assert client.get_existing_classes() == {"doc/x": {"@id": "doc/x"}}

    @mock.patch.object(requests.Session, "get", side_effect=_mock({"@id": "doc/x"}))
    def test_has_doc_true(self, _g):
        client = _client()
        assert client.has_doc("doc/x") is True

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock({"api:error": {"@type": "api:DocumentNotFound"}}, status=404),
    )
    def test_has_doc_not_found(self, _g):
        client = _client()
        assert client.has_doc("doc/missing") is False

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock({"api:error": {"@type": "api:Other"}}, status=500),
    )
    def test_has_doc_reraises_other_errors(self, _g):
        client = _client()
        with pytest.raises(DatabaseError):
            client.has_doc("doc/x")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(requests.Session, "post", side_effect=_mock({"inserts": 1}))
    @mock.patch.object(requests.Session, "put", side_effect=_mock({"inserts": 1}))
    @mock.patch.object(requests.Session, "delete", side_effect=_mock({"deletes": 1}))
    def test_document_writes(self, _d, _u, _p, _g):
        client = _client()
        client.insert_document({"@id": "doc/x", "name": "n"})
        client.insert_document([{"@id": "doc/a"}, {"@id": "doc/b"}])
        client.insert_document(
            [{"@type": "@context", "@base": "x/"}, {"@id": "doc/x"}],
            full_replace=True,
        )
        client.replace_document({"@id": "doc/x"})
        client.update_document({"@id": "doc/x", "name": "m"})
        client.delete_document("doc/x")
        client.delete_document(["doc/x", "doc/y"])
        client.delete_document({"@id": "doc/z"})

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"inserts": 0, "deletes": 0})
    )
    def test_query_variants(self, _p, _g):
        client = _client()
        client.query({"@type": "Triple"})
        client.query({"@type": "Triple"}, commit_msg="cm")
        result, version = client.query({"@type": "Triple"}, get_data_version=True)
        assert version == "v0"

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_vcs_operations(self, _p, _g):
        client = _client()
        client.pull()
        client.pull(remote="other", remote_branch="dev", message="m")
        client.fetch("origin")
        client.push()
        client.push(remote="other", remote_branch="dev", message="m", author="a")
        client.rebase(branch="dev")
        client.rebase(commit="abc123")
        client.rebase(rebase_source="admin/db/local/branch/src")
        client.squash(message="m", author="a")
        client.squash(reset=True)
        client.apply("v1", "v2", branch="dev", message="m", author="a")
        client.clonedb("newdb", "admin")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_reset_and_optimize(self, _p, _g):
        client = _client()
        client.reset("commit123")
        client.reset("commit123", soft=True)
        client.optimize("admin/db")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_diff_and_versions(self, _p, _g):
        client = _client()
        client.diff({"a": 1}, {"a": 2})
        client.diff_version("v1", "v2")
        client.diff_object({"a": 1}, {"a": 2})

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_patch_method(self, _p, _g):
        client = _client()
        patch = Patch(json.dumps({"name": {"@op": "SwapValue", "@after": "b"}}))
        result = client.patch({"name": "a"}, patch)
        assert result is not None

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_route(
            [
                ("databas", [{"name": "admin/db"}]),
                ("organiz", {"name": "admin"}),
                ("api/", [{"name": "admin/db"}]),
            ]
        ),
    )
    def test_organizations_and_databases(self, _g):
        client = _client()
        assert client.get_organization("admin") == {"name": "admin"}
        assert client.get_organization_user_databases("admin", "admin") == [
            {"name": "admin/db"}
        ]
        assert client.get_databases() == [{"name": "admin/db"}]
        assert client.list_databases() == ["admin/db"]

    def test_check_connection_raises_when_disconnected(self):
        client = Client("http://localhost:6363")
        with pytest.raises(InterfaceError):
            client.get_databases()


class TestClientWave2:
    def test_auth_variants(self):
        client = _client()
        assert client._auth() == ("admin", "root")

        jwt_client = _connect(
            Client("http://localhost:6363"), jwt_token="jwt", use_token=True
        )
        assert isinstance(jwt_client._auth(), JWTAuth)

        token_client = _connect(
            Client("http://localhost:6363"), api_token="tok"
        )
        assert isinstance(token_client._auth(), APITokenAuth)

        with mock.patch.dict(
            "os.environ", {"TERMINUSDB_ACCESS_TOKEN": "envtok"}
        ):
            env_client = _connect(
                Client("http://localhost:6363"), key=None, user=None
            )
            assert isinstance(env_client._auth(), APITokenAuth)

        client.close()
        with pytest.raises(RuntimeError):
            client._auth()

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    def test_query_streaming(self, _g):
        client = _client()
        lines = [
            json.dumps({"@type": "PrefaceRecord", "names": ["v:x"]}),
            json.dumps({"@type": "Binding", "v:x": 1}),
        ]
        with mock.patch.object(
            requests.Session,
            "post",
            side_effect=lambda *a, **k: _resp({}, lines=lines),
        ):
            result = client.query({"@type": "Triple"}, streaming=True)
            assert list(result) == [{"@type": "Binding", "v:x": 1}]

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"inserts": 0, "deletes": 0})
    )
    def test_query_woql_object_and_last_version(self, _p, _g):
        from terminusdb_client.woqlquery.woql_query import WOQLQuery

        client = _client()
        client.query(WOQLQuery().star())
        client.query({"@type": "Triple"}, last_data_version="v1")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(requests.Session, "delete", side_effect=_mock({}))
    def test_delete_database(self, _d, _g):
        client = _client()
        with pytest.raises(UserWarning):
            client.delete_database()

        client = _client()
        with pytest.warns(UserWarning):
            client.delete_database("otherdb")
        assert client.db is None

        client = _client()
        client.delete_database("db", "admin", force=True)
        assert client.db is None

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(requests.Session, "post", side_effect=_mock({}))
    @mock.patch.object(requests.Session, "delete", side_effect=_mock({}))
    def test_branch_management(self, _d, _p, _g):
        client = _client()
        client.create_branch("dev")
        client.create_branch("empty", empty=True)
        client.ref = "commit1"
        client.create_branch("fromref")
        client.delete_branch("dev")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(requests.Session, "post", side_effect=_mock({}))
    def test_patch_resource(self, _p, _g):
        client = _client()
        patch = Patch(json.dumps({"name": {"@op": "SwapValue", "@after": "b"}}))
        client.patch_resource(patch, branch="dev", message="m", author="a")

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock({"@id": "doc/x"}, text='{"@id": "doc/x"}'),
    )
    @mock.patch.object(
        requests.Session,
        "post",
        side_effect=_mock({"@id": "doc/x"}, text='{"@id": "doc/x"}'),
    )
    def test_document_version_paths(self, _p, _g):
        client = _client()
        docs, v = client.query_document({"@type": "T"}, get_data_version=True)
        assert v == "v0"
        docs, v = client.query_document(
            {"@type": "T"}, get_data_version=True, as_list=True, skip=1, count=2
        )
        doc, v = client.get_document("doc/x", get_data_version=True)
        assert v == "v0"
        docs, v = client.get_documents_by_type("T", get_data_version=True)
        assert v == "v0"
        docs, v = client.get_all_documents(
            get_data_version=True, as_list=True
        )
        assert v == "v0"
        it = client.query_document({"@type": "T"})
        assert list(it) == [{"@id": "doc/x"}]
        client.get_documents_by_type("T", prefixed=True, unfold=True)

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(requests.Session, "delete", side_effect=_mock({}))
    def test_iterable_delete(self, _d, _g):
        client = _client()
        client.delete_document(iter(["doc/x", "doc/y"]))

    def test_reset_and_rebase_guards(self):
        client = _client()
        assert client.reset(None) is None
        with pytest.raises(RuntimeError):
            client.rebase()
        with pytest.raises(RuntimeError):
            client.rebase(branch="a", commit="b")

    def test_prefix_url_system_db(self):
        client = _client()
        client.db = "_system"
        url = client._prefix_url("ex")
        assert "prefix/_system/ex" in url
        assert client._prefix_url() is not None

    @mock.patch.object(requests.Session, "get", side_effect=_mock({"api:info": {}}))
    @mock.patch.object(requests.Session, "head", side_effect=_mock({}))
    def test_connect_with_db(self, _h, _g):
        client = Client("http://localhost:6363")
        client.connect(user="admin", key="root", team="admin", db="db")
        assert client.db == "db"
        client.close()
        assert client._connected is False


class TestClientWave3:
    def test_url_builders(self):
        client = _client()
        assert "capabilities" in client._capabilities_url()
        assert "organizations" in client._organization_url()
        assert "users" in client._users_url()
        assert "roles" in client._roles_url()

        client.db = "_system"
        assert client._db_url_fragment() == "_system"
        assert "woql" in client._query_url()
        assert "schema" in client._class_frame_url()
        assert "document" in client._documents_url()

        client = _client()
        client.repo = "_meta"
        assert "_meta" in client._branch_base("document")
        client.repo = "local"
        client.branch = "_commits"
        assert "_commits" in client._branch_base("document")
        client.branch = "main"
        client.ref = "abc"
        assert "commit/abc" in client._branch_base("document")
        client.ref = None
        assert "branch/other" in client._branch_base("document", branch="other")

    @mock.patch.object(
        requests.Session,
        "get",
        side_effect=_mock(
            [{"timestamp": 1, "identifier": "abc"}],
            text='[{"timestamp": 1, "identifier": "abc"}]',
        ),
    )
    def test_branches_and_commit_helpers(self, _g):
        client = _client()
        assert client._get_current_commit() == "abc"
        assert client._get_target_commit(1) == "abc"
        branches = client.get_all_branches()
        assert isinstance(branches, list)
        branches, version = client.get_all_branches(get_data_version=True)
        assert version == "v0"

    def test_conv_to_dict_branches(self):
        client = _client()

        with_to_dict = mock.Mock()
        with_to_dict.to_dict.return_value = {"a": 1}
        del with_to_dict._isinstance
        assert client._conv_to_dict(with_to_dict) == {"a": 1}

        with__to_dict = mock.Mock(spec=[])
        with__to_dict._to_dict = mock.Mock(return_value={"b": 2})
        with__to_dict._isinstance = False
        assert client._conv_to_dict(with__to_dict) == {"b": 2}

        with pytest.raises(ValueError):
            client._conv_to_dict(object())

    def test_insert_document_edges(self):
        client = _client()
        with mock.patch.object(
            requests.Session, "post", side_effect=_mock({"inserts": 1})
        ):
            with pytest.warns(UserWarning):
                client.insert_document(
                    [{"@type": "@context", "@base": "x/"}, {"@id": "doc/x"}]
                )
            assert client.insert_document([]) is None

        class SchemaObj:
            pass

        obj = SchemaObj()
        obj.to_dict = lambda: {"@type": "Class"}
        with pytest.raises(InterfaceError):
            client.insert_document(obj)

    @mock.patch.object(requests.Session, "get", side_effect=_mock({"api:info": {}}))
    @mock.patch.object(
        requests.Session,
        "head",
        side_effect=_mock({"api:error": {"@type": "x"}}, status=404),
    )
    def test_connect_db_missing(self, _h, _g):
        client = Client("http://localhost:6363")
        with pytest.raises(InterfaceError):
            client.connect(user="admin", key="root", team="admin", db="missing")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_remote_auth_and_push(self, _p, _g):
        client = _client()
        client.push(remote_auth={"type": "basic", "user": "u", "key": "k"})
        client = _connect(
            Client("http://localhost:6363"),
            remote_auth={"type": "basic", "user": "u", "key": "k"},
        )
        client.repo = "local"
        client.branch = "main"
        client.db = "db"
        client.push()
        client.fetch("origin")

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_reset_use_path_and_soft(self, _p, _g):
        client = _client()
        client.reset("admin/db/local/commit/abc", use_path=True)
        client.reset("abc", soft=True, use_path=True)

    @mock.patch.object(requests.Session, "get", side_effect=_mock({}))
    @mock.patch.object(
        requests.Session, "post", side_effect=_mock({"api:status": "api:success"})
    )
    def test_diff_document_id(self, _p, _g):
        client = _client()
        client.diff("v1", "v2", document_id="doc/x")
        with pytest.raises(ValueError):
            client.diff({"a": 1}, {"a": 2}, document_id="doc/x")
