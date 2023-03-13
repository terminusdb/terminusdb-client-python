# import csv
# import filecmp
import datetime as dt
import os
from random import random

import pytest

from terminusdb_client.errors import DatabaseError, InterfaceError
from terminusdb_client import GraphType, Patch, Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def test_not_ok():
    client = Client('http://localhost:6363')
    not client.ok()


def test_ok(docker_url):
    client = Client(docker_url)
    client.connect()
    assert client.ok()


def test_happy_path(docker_url):
    # create client
    client = Client(docker_url)
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
    first_obj = client.query(WOQLQuery().star(graph="schema"))
    assert first_commit != init_commit
    assert len(client.get_commit_history()) == 1
    client.query(WOQLQuery().add_quad("b", "rdf:type", "sys:Class", "schema"))
    commit_history = client.get_commit_history()
    more_obj = client.query(WOQLQuery().star(graph="schema"))
    assert first_obj != more_obj
    assert client._get_target_commit(1) == first_commit
    assert len(client.get_commit_history()) == 2
    # test reset
    client.reset(commit_history[-1]["commit"], soft=True)
    assert len(client.get_commit_history()) == 2
    assert client._ref == commit_history[-1]["commit"]
    assert client.query(WOQLQuery().star(graph="schema")) == first_obj
    client.reset(commit_history[-1]["commit"])
    assert len(client.get_commit_history()) == 1
    assert client._get_current_commit() == first_commit
    assert client._ref is None
    client.delete_database("test_happy_path", "admin")
    assert client.db is None
    assert "test_happy_path" not in client.list_databases()


def test_happy_crazy_path(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
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


def test_add_get_remove_org(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.create_organization("testOrg")
    org = client.get_organization("testOrg")
    assert org['name'] == 'testOrg'
    client.delete_organization("testOrg")
    with pytest.raises(DatabaseError):
        # The org shouldn't exist anymore
        client.get_organization("testOrg")


def test_diff_object(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    # test create db
    client.connect()
    diff = client.diff_object({'test': 'wew'}, {'test': 'wow'})
    assert diff == {'test': {'@before': 'wew', '@after': 'wow', '@op': 'SwapValue'}}


def test_class_frame(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    db_name = "philosophers" + str(random())
    client.create_database(db_name)
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class",
              "@id": "Philosopher",
              "name": "xsd:string"
              }
    # Add schema and Socrates
    client.insert_document(schema, graph_type=GraphType.SCHEMA)
    assert client.get_class_frame("Philosopher") == {'@type': 'Class', 'name': 'xsd:string'}


def test_woql_substr(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    db_name = "philosophers" + str(random())
    client.create_database(db_name)
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class",
              "@id": "Philosopher",
              "name": "xsd:string"
              }
    # Add schema and Socrates
    client.insert_document(schema, graph_type="schema")
    client.insert_document({"name": "Socrates"})
    result = client.query(
        WOQLQuery().triple('v:Philosopher', '@schema:name', 'v:Name')
        .substr('v:Name', 3, 'v:Substring', 0, 'v:After'))
    assert result['bindings'][0]['Substring']['@value'] == 'Soc'


def test_diff_apply_version(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    db_name = "philosophers" + str(random())
    client.create_database(db_name)
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class",
              "@id": "Philosopher",
              "name": "xsd:string"
              }
    # Add schema and Socrates
    client.insert_document(schema, graph_type="schema")
    client.insert_document({"name": "Socrates"})

    # Create new branch and switch to it
    client.create_branch("changes")
    client.branch = "changes"

    # Add more philosophers
    client.insert_document({"name": "Plato"})
    client.insert_document({"name": "Aristotle"})

    diff = client.diff_version("main", "changes")
    assert len(diff) == 2
    assert diff[0]['@insert']['name'] == 'Plato'
    assert diff[1]['@insert']['name'] == 'Aristotle'

    # Apply the differences to main with apply
    client.apply("main", "changes", branch='main')

    # Diff again
    diff_again = client.diff_version("main", "changes")
    assert len(diff_again) == 0


def test_log(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    # test create db
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    log = client.log(team="admin", db=db_name)
    assert log[0]['@type'] == 'InitialCommit'


def test_get_triples(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class",
              "@id": "Philosopher",
              "name": "xsd:string"
              }
    # Add schema and Socrates
    client.insert_document(schema, graph_type="schema")
    schema_triples = client.get_triples(graph_type='schema')
    assert "<schema#Philosopher>\n  a sys:Class ;\n  <schema#name> xsd:string ." in schema_triples


def test_update_triples(docker_url):
    ttl = """
@base <terminusdb:///schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix woql: <http://terminusdb.com/schema/woql#> .
@prefix json: <http://terminusdb.com/schema/json#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix xdd: <http://terminusdb.com/schema/xdd#> .
@prefix vio: <http://terminusdb.com/schema/vio#> .
@prefix sys: <http://terminusdb.com/schema/sys#> .
@prefix api: <http://terminusdb.com/schema/api#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix doc: <data/> .

<schema#Philosopher>
  a sys:Class ;
  <schema#name> xsd:string .

<terminusdb://context>
  a sys:Context ;
  sys:base "terminusdb:///data/"^^xsd:string ;
  sys:schema "terminusdb:///schema#"^^xsd:string .
"""
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)
    client.update_triples(graph_type='schema', content=ttl, commit_msg="Update triples")
    client.insert_document({"name": "Socrates"})
    assert len(list(client.get_all_documents())) == 1


def test_insert_triples(docker_url):
    ttl = """
@base <terminusdb:///schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix woql: <http://terminusdb.com/schema/woql#> .
@prefix json: <http://terminusdb.com/schema/json#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix xdd: <http://terminusdb.com/schema/xdd#> .
@prefix vio: <http://terminusdb.com/schema/vio#> .
@prefix sys: <http://terminusdb.com/schema/sys#> .
@prefix api: <http://terminusdb.com/schema/api#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix doc: <data/> .

<schema#Philosopher>
  a sys:Class ;
  <schema#name> xsd:string .

<terminusdb://context>
  a sys:Context ;
  sys:base "terminusdb:///data/"^^xsd:string ;
  sys:schema "terminusdb:///schema#"^^xsd:string .
"""
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)
    client.insert_triples(graph_type='schema', content=ttl, commit_msg="Insert triples")
    client.insert_document({"name": "Socrates"})
    assert len(list(client.get_all_documents())) == 1


def test_get_database(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    db = client.get_database(db_name)
    assert db['name'] == db_name
    db_with_team = client.get_database(db_name, team='admin')
    assert db_with_team['name'] == db_name
    with pytest.raises(DatabaseError):
        client.get_database("DOES_NOT_EXISTDB")


def test_has_doc(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)
    assert not client.has_doc("THIS_DOCUMENT_DOES_NOT_EXIST")
    client.insert_document({"test": "test"}, raw_json=True)
    doc_id = list(client.get_all_documents())[0]["@id"]
    assert client.has_doc(doc_id)


def test_get_organization_user_databases(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    db_name2 = "testDB" + str(random())
    org_name = "testOrg235091"
    # Add DB in admin org to make sure they don't appear in other team
    client.create_database(db_name + "admin", team="admin")
    client.create_organization(org_name)
    client.create_database(db_name, team=org_name)
    client.create_database(db_name2, team=org_name)
    capability_change = {
        "operation": "grant",
        "scope": f"Organization/{org_name}",
        "user": "User/admin",
        "roles": [
            "Role/admin"
        ]
    }
    client.change_capabilities(capability_change)
    databases = client.get_organization_user_databases(org=org_name, username="admin")
    assert len(databases) == 2
    assert databases[0]['name'] == db_name
    assert databases[1]['name'] == db_name2


def test_has_database(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    assert client.has_database(db_name)
    assert not client.has_database("DOES_NOT_EXISTDB")


def test_optimize(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)
    for x in range(0, 10):
        client.insert_document({"name": f"Philosopher{x}"}, raw_json=True)
    client.optimize(f"admin/{db_name}")


def test_add_get_remove_user(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.add_user("test", "randomPassword")
    user = client.get_user("test")
    assert user['name'] == 'test'
    client.delete_user("test")
    with pytest.raises(DatabaseError):
        user = client.get_user("test")


def test_patch(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database("patch")
    schema = [{"@id" : "Person",
               "@type" : "Class",
               "name" : "xsd:string"}]
    instance = [{"@type" : "Person",
                 "@id" : "Person/Jane",
                 "name" : "Jane"}]
    client.insert_document(schema, graph_type="schema")
    client.insert_document(instance)

    patch = Patch(
        json='{"@id": "Person/Jane", "name" : { "@op" : "SwapValue", "@before" : "Jane", "@after": "Janine" }}'
    )

    client.patch(patch)
    doc = client.get_document('Person/Jane')
    assert doc == {"@type" : "Person",
                   "@id" : "Person/Jane",
                   "name" : "Janine"}
    client.delete_database("patch", "admin")


def test_diff_ops(docker_url, test_schema):
    # create client and db
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database("test_diff_ops")
    public_diff = Client(
        "https://cloud.terminusdb.com/jsondiff", user_agent=test_user_agent
    )
    public_patch = Client(
        "https://cloud.terminusdb.com/jsonpatch", user_agent=test_user_agent
    )
    result_patch = Patch(
        json='{"@id": "Person/Jane", "name" : { "@op" : "SwapValue", "@before" : "Jane", "@after": "Janine" }}'
    )
    result = client.diff(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"},
        {"@id": "Person/Jane", "@type": "Person", "name": "Janine"},
    )
    public_result = public_diff.diff(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"},
        {"@id": "Person/Jane", "@type": "Person", "name": "Janine"},
    )
    assert result.content == result_patch.content
    assert public_result.content == result_patch.content

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
    public_result = public_diff.diff(jane, janine)
    # test commit_id and data_version with after obj
    test_schema.commit(client)
    jane_id = client.insert_document(jane)[0]
    data_version = client.get_document(jane_id, get_data_version=True)[-1]
    current_commit = client._get_current_commit()
    commit_id_result = client.diff(current_commit, janine, document_id=jane_id)
    data_version_result = client.diff(data_version, janine, document_id=jane_id)
    # test commit_id and data_version both before and after
    client.update_document(janine)
    new_data_version = client.get_document(jane_id, get_data_version=True)[-1]
    new_commit = client._get_current_commit()
    commit_id_result2 = client.diff(current_commit, new_commit, document_id=jane_id)
    data_version_result2 = client.diff(
        data_version, new_data_version, document_id=jane_id
    )
    # test all diff commit_id and data_version
    commit_id_result_all = client.diff(current_commit, new_commit)
    data_version_result_all = client.diff(data_version, new_data_version)
    assert result.content == result_patch.content
    assert public_result.content == result_patch.content
    assert commit_id_result.content == result_patch.content
    assert commit_id_result2.content == result_patch.content
    assert data_version_result.content == result_patch.content
    assert data_version_result2.content == result_patch.content
    assert commit_id_result_all.content == [result_patch.content]
    assert data_version_result_all.content == [result_patch.content]
    assert client.patch(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"}, result_patch
    ) == {"@id": "Person/Jane", "@type": "Person", "name": "Janine"}
    assert public_patch.patch(
        {"@id": "Person/Jane", "@type": "Person", "name": "Jane"}, result_patch
    ) == {"@id": "Person/Jane", "@type": "Person", "name": "Janine"}
    assert client.patch(jane, result_patch) == {
        "@id": "Person/Jane",
        "@type": "Person",
        "name": "Janine",
        "age": 18,
    }
    assert public_patch.patch(jane, result_patch) == {
        "@id": "Person/Jane",
        "@type": "Person",
        "name": "Janine",
        "age": 18,
    }
    my_schema = test_schema.copy()
    my_schema.object.pop("Employee")
    assert my_schema.to_dict() != test_schema.to_dict()


@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_diff_ops_no_auth(test_schema, terminusx_token):
    # create client and db
    client = Client(
        "https://cloud-dev.terminusdb.com/TerminusDBTest//", user_agent=test_user_agent
    )
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
        age="18",
    )
    janine = Person(
        _id="Jane",
        name="Janine",
        age="18",
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
    client = Client(url, user_agent=test_user_agent)
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
    ).replace(":", "_").replace(".", "")
    endpoint = "https://cloud-dev.terminusdb.com/TerminusDBTest/"
    client = Client(endpoint, user_agent=test_user_agent)
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
    testdb = (
        "test_crazy" + str(dt.datetime.now()).replace(" ", "") + "_" + str(random())
    ).replace(":", "_").replace(".", "")
    endpoint = "https://cloud-dev.terminusdb.com/TerminusDBTest/"
    client = Client(endpoint, user_agent=test_user_agent)
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
