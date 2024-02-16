# import sys
# sys.path.append('client')
import unittest.mock as mock

import pytest
import random
import requests


from terminusdb_client.client import Client, GraphType
from terminusdb_client.errors import InterfaceError
from terminusdb_client.woqlschema import WOQLSchema

from ..__version__ import __version__
from .conftest import mocked_request_insert_delete, mocked_request_success
from .woqljson.woqlStarJson import WoqlStar


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_connection(mocked_requests):
    client = Client("http://localhost:6363")

    client.connect(key="root", team="admin", user="admin")

    client._session.get.assert_called_once_with(
        "http://localhost:6363/api/info",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_user_agent_set(mocked_requests):
    client = Client("http://localhost:6363", user_agent="test_user_agent")

    client.connect(key="root", team="admin", user="admin")

    client._session.get.assert_called_once_with(
        "http://localhost:6363/api/info",
        auth=("admin", "root"),
        headers={"user-agent": "test_user_agent"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_connected_flag(mocked_requests):
    client = Client("http://localhost:6363")
    assert not client._connected
    client.connect(key="root", team="admin", user="admin")
    assert client._connected
    client.close()
    assert not client._connected


@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_create_database(mocked_requests, mocked_requests2):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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
        json={"label": "my first db", "comment": "my first db comment", "schema": False},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
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


@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
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
        json={"label": "my first db", "comment": "my first db comment", "schema": False},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
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


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
def test_has_database(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    db_name = "testDB" + str(random.randrange(100000))
    client.has_database(db_name)
    client._session.head.assert_called_with(
        f"http://localhost:6363/api/db/admin/{db_name}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@pytest.mark.skip(reason="temporary not avaliable")
@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
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
@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_triples_with_enum(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")

    client.get_triples(GraphType.INSTANCE)

    client._session.get.assert_called_with(
        "http://localhost:6363/api/triples/admin/myDBName/local/branch/main/instance",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_insert_delete)
@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
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
        },
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        stream=False
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_query_nodb(mocked_requests):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    with pytest.raises(InterfaceError):
        client.query(WoqlStar)


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_insert_delete)
def test_query_commit_made(mocked_execute, mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root", db="myDBName")
    result = client.query(WoqlStar)
    assert result == "Commit successfully made."


@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_rollback(mocked_requests):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    with pytest.raises(NotImplementedError):
        client.rollback()


def test_copy_client():
    client = Client("http://localhost:6363")
    copy_client = client.copy()
    assert id(client) != copy_client


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_basic_auth(mocked_requests):
    client = Client("http://localhost:6363")
    client.connect(user="admin", team="admin", key="root")
    assert client._key == "root"
    assert client.team == "admin"
    assert client.user == "admin"


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_remote_auth(mocked_requests):
    client = Client("http://localhost:6363")
    auth_setting = {"type": "jwt", "user": "admin", "key": "<token>"}
    client.connect(
        user="admin", team="admin", key="root", remote_auth=auth_setting
    )
    result = client._remote_auth_dict
    assert result == auth_setting


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_set_db(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    with pytest.raises(InterfaceError):
        client.set_db("myDBName")
    client.connect()
    client.set_db("myDBName")
    assert client.db == "myDBName"
    assert client.repo == "local"


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_full_replace_fail(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(db="myDBName")
    with pytest.raises(ValueError):
        client.insert_document(
            [{"not_context": "no context provided"}], full_replace=True
        )


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_insert_woqlschema_fail(mocked_requests, mocked_requests2):
    client = Client("http://localhost:6363")
    client.connect(db="myDBName")
    with pytest.raises(InterfaceError):
        client.insert_document(WOQLSchema(), graph_type="instance")


@mock.patch.object(requests.Session, 'head', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'delete', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_delete_document(
    mocked_requests, mocked_requests2, mocked_requests3, test_schema
):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
def test_add_user(mocked_requests, mocked_requests2):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()

    user = "Gavin" + str(random.randrange(100000))
    client.add_user(user, "somePassword")

    client._session.post.assert_called_with(
        "http://localhost:6363/api/users",
        auth=("admin", "root"),
        json={"name": user, "password": "somePassword"},
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'delete', side_effect=mocked_request_success)
def test_delete_user(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()

    user = "Gavin" + str(random.randrange(100000))
    client.add_user(user, "somePassword")
    client.delete_user(user)

    client._session.delete.assert_called_with(
        f"http://localhost:6363/api/users/{user}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'delete', side_effect=mocked_request_success)
def test_delete_organization(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()

    org = "RandomOrg" + str(random.randrange(100000))
    client.create_organization(org)
    client.delete_organization(org)

    client._session.delete.assert_called_with(
        f"http://localhost:6363/api/organizations/{org}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'put', side_effect=mocked_request_success)
def test_change_user_password(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
def test_create_organization(mocked_requests, mocked_requests2):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()

    org = "RandomOrg" + str(random.randrange(100000))
    client.create_organization(org)

    client._session.post.assert_called_with(
        f"http://localhost:6363/api/organizations/{org}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_organization_users(mocked_requests):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()
    client.get_organization_users("admin")
    client._session.get.assert_called_with(
        "http://localhost:6363/api/organizations/admin/users",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_organization_user(mocked_requests):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()
    client.get_organization_user("admin", "admin")
    client._session.get.assert_called_with(
        "http://localhost:6363/api/organizations/admin/users/admin",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_organizations(mocked_requests):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()
    client.get_organizations()
    client._session.get.assert_called_with(
        "http://localhost:6363/api/organizations",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
def test_capabilities_change(mocked_requests, mocked_requests2):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()
    capability_change = {
        "operation": "revoke",
        "scope": "UserDatabase/f5a0ef94469b32e1aee321678436c7dfd5a96d9c476672b3282ae89a45b5200e",
        "user": "User/admin",
        "roles": [
            "Role/consumer",
            "Role/admin"
        ]
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
def test_add_role(mocked_requests, mocked_requests2):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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
            "schema_write_access"
        ]
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'post', side_effect=mocked_request_success)
@mock.patch.object(requests.Session, 'put', side_effect=mocked_request_success)
def test_change_role(mocked_requests, mocked_requests2, mocked_requests3):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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
            "schema_write_access"
        ]
    }
    try:
        client.add_role(role)
        del role['action'][2]  # Delete clone as action
        client.change_role(role)
    except InterfaceError:
        pass
    client._session.put.assert_called_with(
        "http://localhost:6363/api/roles",
        auth=("admin", "root"),
        json=role,
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_roles(mocked_requests):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_users(mocked_requests):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
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


@mock.patch.object(requests.Session, 'get', side_effect=mocked_request_success)
def test_get_user(mocked_requests):
    client = Client(
        "http://localhost:6363", user="admin", key="root", team="admin"
    )
    client.connect()
    user = "Gavin" + str(random.randrange(100000))
    client.get_user(user)
    client._session.get.assert_called_with(
        f"http://localhost:6363/api/users/{user}",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
    )
