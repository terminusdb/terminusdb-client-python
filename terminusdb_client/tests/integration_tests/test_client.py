# import csv
# import filecmp
import datetime as dt
import os
from random import random

import pytest

from terminusdb_client.errors import InterfaceError
from terminusdb_client.woqlclient.woqlClient import Patch, WOQLClient
from terminusdb_client.woqlquery.woql_query import WOQLQuery

# from terminusdb_client.woqlquery.woql_query import WOQLQuery


def test_happy_path(docker_url):
    # create client
    client = WOQLClient(docker_url)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    assert client._db_info is not None
    # test db does not exist
    with pytest.raises(InterfaceError) as error:
        client.connect(db="test_happy_path")
        assert error.value == "Connection fail, test_happy_path does not exist."
    # test create db
    client.create_database("test_happy_path")
    init_commit = client._get_current_commit()
    assert client.db == "test_happy_path"
    assert "test_happy_path" in client.list_databases()
    # assert client._context.get("doc") == "foo://"
    assert len(client.get_commit_history()) == 1
    # test adding something
    client.query(WOQLQuery().add_quad("a", "rdf:type", "sys:Class", "schema"))
    first_commit = client._get_current_commit()
    first_obj = client.query(WOQLQuery().star())
    assert first_commit != init_commit
    assert len(client.get_commit_history()) == 1
    client.query(WOQLQuery().add_quad("b", "rdf:type", "sys:Class", "schema"))
    commit_history = client.get_commit_history()
    more_obj = client.query(WOQLQuery().star())
    assert first_obj != more_obj
    assert client._get_target_commit(1) == first_commit
    assert len(client.get_commit_history()) == 2
    # test reset
    client.reset(commit_history[-1]["commit"], soft=True)
    assert len(client.get_commit_history()) == 2
    assert client._ref == commit_history[-1]["commit"]
    assert client.query(WOQLQuery().star()) == first_obj
    client.reset(commit_history[-1]["commit"])
    assert len(client.get_commit_history()) == 1
    assert client._get_current_commit() == first_commit
    assert client._ref is None
    client.delete_database("test_happy_path", "admin")
    assert client.db is None
    assert "test_happy_path" not in client.list_databases()


def test_happy_carzy_path(docker_url):
    # create client
    client = WOQLClient(docker_url)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.create_database("test happy path")
    init_commit = client._get_current_commit()
    assert client.db == "test happy path"
    assert "test happy path" in client.list_databases()
    # assert client._context.get("doc") == "foo://"
    assert len(client.get_commit_history()) == 1
    # test adding something
    client.query(WOQLQuery().add_quad("a", "rdf:type", "sys:Class", "schema"))
    first_commit = client._get_current_commit()
    assert first_commit != init_commit
    assert len(client.get_commit_history()) == 1
    client.query(WOQLQuery().add_quad("b", "rdf:type", "sys:Class", "schema"))
    commit_history = client.get_commit_history()
    assert client._get_target_commit(1) == first_commit
    assert len(client.get_commit_history()) == 2
    # test reset
    client.reset(commit_history[-1]["commit"])
    assert client._get_current_commit() == first_commit
    client.create_branch("New Branch")
    client.rebase("New Branch")
    client.delete_database("test happy path", "admin")
    assert client.db is None
    assert "test happy path" not in client.list_databases()


def test_diff_ops(docker_url, test_schema):
    # create client and db
    client = WOQLClient(docker_url)

    result_patch = Patch(
        json='{"@id": "Person/Jane", "name" : { "@op" : "SwapValue", "@before" : "Jane", "@after": "Janine" }}'
    )
    result = client.diff(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"},
        {"@id": "Person/Jane", "@type": "Person", "name": "Janine"},
    )
    assert result.content == result_patch.content

    Person = test_schema.object.get("Person")
    jane = Person(
        _id="Jane",
        name="Jane",
        age=18,
    )
    janine = Person(
        _id="Jane",
        name="Janine",
        age=18,
    )
    result = client.diff(jane, janine)
    assert result.content == result_patch.content
    assert client.patch(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"}, result_patch
    ) == {"@id": "Person/Jane", "@type": "Person", "name": "Janine"}
    assert client.patch(jane, result_patch) == {
        "@id": "Person/Jane",
        "@type": "Person",
        "name": "Janine",
        "age": 18,
    }
    my_schema = test_schema.copy()
    my_schema.object.pop("Employee")
    assert my_schema.to_dict() != test_schema.to_dict()
    ## Temporary switch off schema diff
    # result = client.diff(test_schema, my_schema)
    # assert result.content == {
    #     "@op": "CopyList",
    #     "@rest": {
    #         "@after": [],
    #         "@before": [
    #             {
    #                 "@id": "Employee",
    #                 "@inherits": ["Person"],
    #                 "@key": {"@type": "Random"},
    #                 "@type": "Class",
    #                 "address_of": "Address",
    #                 "age": "xsd:integer",
    #                 "contact_number": {"@class": "xsd:string", "@type": "Optional"},
    #                 "friend_of": {"@class": "Person", "@type": "Set"},
    #                 "managed_by": "Employee",
    #                 "member_of": "Team",
    #                 "name": "xsd:string",
    #                 "permisstion": {"@class": "Role", "@type": "Set"},
    #             }
    #         ],
    #         "@op": "SwapList",
    #         "@rest": {"@op": "KeepList"},
    #     },
    #     "@to": 4,
    # }
    # assert client.patch(test_schema, result) == my_schema.to_dict()


@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_diff_ops_no_auth(test_schema, terminusx_token):
    # create client and db
    client = WOQLClient("https://cloud-dev.dcm.ist/TerminusDBTest/")
    client.connect(use_token=True, team="TerminusDBTest")

    result_patch = Patch(
        json='{"@id": "Person/Jane", "name" : { "@op" : "SwapValue", "@before" : "Jane", "@after": "Janine" }}'
    )
    result = client.diff(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"},
        {"@id": "Person/Jane", "@type": "Person", "name": "Janine"},
    )
    assert result.content == result_patch.content

    Person = test_schema.object.get("Person")
    jane = Person(
        _id="Jane",
        name="Jane",
        age=18,
    )
    janine = Person(
        _id="Jane",
        name="Janine",
        age=18,
    )
    result = client.diff(jane, janine)
    assert result.content == result_patch.content
    assert client.patch(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"}, result_patch
    ) == {"@id": "Person/Jane", "@type": "Person", "name": "Janine"}
    assert client.patch(jane, result_patch) == {
        "@id": "Person/Jane",
        "@type": "Person",
        "name": "Janine",
        "age": 18,
    }
    my_schema = test_schema.copy()
    my_schema.object.pop("Employee")
    assert my_schema.to_dict() != test_schema.to_dict()
    ## Temporary switch off schema diff
    # result = client.diff(test_schema, my_schema)
    # assert client.patch(test_schema, result) == my_schema.to_dict()


def test_jwt(docker_url_jwt):
    # create client
    url = docker_url_jwt[0]
    token = docker_url_jwt[1]
    client = WOQLClient(url)
    assert not client._connected
    # test connect
    client.connect(use_token=True, jwt_token=token)
    assert client._connected
    # test create db
    client.create_database("test_happy_path")
    assert client.db == "test_happy_path"
    assert "test_happy_path" in client.list_databases()
    client.delete_database("test_happy_path", "admin")
    assert client.db is None
    assert "test_happy_path" not in client.list_databases()


@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_terminusx(terminusx_token):
    testdb = (
        "test_happy_" + str(dt.datetime.now()).replace(" ", "") + "_" + str(random())
    )
    endpoint = "https://cloud-dev.dcm.ist/TerminusDBTest/"
    client = WOQLClient(endpoint)
    client.connect(use_token=True, team="TerminusDBTest")
    assert client._connected
    # test create db
    client.create_database(testdb)
    assert client.db == testdb
    assert testdb in client.list_databases()
    client.delete_database(testdb, "TerminusDBTest")
    assert client.db is None
    assert testdb not in client.list_databases()


@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_terminusx_crazy_path(terminusx_token):
    testdb = "test happy_" + str(dt.datetime.now()).replace(" ", "")
    endpoint = "https://cloud-dev.dcm.ist/TerminusDBTest/"
    client = WOQLClient(endpoint)
    client.connect(use_token=True, team="TerminusDBTest")
    assert client._connected
    # test create db
    client.create_database(testdb)
    assert client.db == testdb
    assert testdb in client.list_databases()
    client.create_branch("New Branch")
    client.rebase("New Branch")
    client.delete_database(testdb, "TerminusDBTest")
    assert client.db is None
    assert testdb not in client.list_databases()


#
# def _generate_csv(option):
#     if option == 1:
#         file_path = "employee_file.csv"
#         with open(file_path, mode="w") as employee_file:
#             employee_writer = csv.writer(
#                 employee_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
#             )
#             employee_writer.writerow(["John Smith", "Accounting", "November"])
#             employee_writer.writerow(["Erica Meyers", "IT", "March"])
#         return file_path
#     else:
#         file_path = "employee_file.csv"
#         with open(file_path, mode="w") as employee_file:
#             employee_writer = csv.writer(
#                 employee_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
#             )
#             employee_writer.writerow(["Cow Duck", "Marketing", "April"])
#         return file_path
#
#
# def _file_clean_up(filename):
#     if os.path.exists(filename):
#         os.remove(filename)
#
#
# def test_csv_handeling(docker_url):
#     client = WOQLClient(docker_url)
#     assert not client._connected
#     # test connect
#     client.connect()
#     assert client._connected
#     # test create db
#     client.create_database("test_csv")
#     client._get_current_commit()
#     assert client._db == "test_csv"
#     assert "test_csv" in client.list_databases()
#     csv_file_path = _generate_csv(1)  # create testing csv
#     try:
#         client.insert_csv(csv_file_path)
#         client.get_csv(csv_file_path, csv_output_name="new_" + csv_file_path)
#         assert filecmp.cmp(csv_file_path, "new_" + csv_file_path)
#         csv_file_path = _generate_csv(2)
#         client.update_csv(csv_file_path)
#         client.get_csv(csv_file_path, csv_output_name="update_" + csv_file_path)
#         assert not filecmp.cmp("new_" + csv_file_path, "update_" + csv_file_path)
#     finally:
#         _file_clean_up(csv_file_path)
#         _file_clean_up("new_" + csv_file_path)
#         _file_clean_up("update_" + csv_file_path)
#

# def test_create_graph(docker_url):
#     client = WOQLClient(docker_url)
#     assert not client._connected
#     # test connect
#     client.connect()
#     assert client._connected
#     # test create db
#     client.create_database("test_graph")
#     client.create_graph("instance", "test-one-more-graph", "create test graph")
#     client.delete_graph("instance", "test-one-more-graph", "delete test graph")
