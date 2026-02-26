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

_CLIENT_TEST_DBS = ["test_diff_ops"]
_CLIENT_TEST_ORGS = ["testOrg235091"]


@pytest.fixture(scope="module", autouse=True)
def cleanup_client_resources(docker_url):
    """Delete stale databases and organizations before the module and clean up after."""
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()

    def _cleanup():
        for db in _CLIENT_TEST_DBS:
            try:
                client.delete_database(db)
            except Exception:
                pass
        for org in _CLIENT_TEST_ORGS:
            # Ensure admin has access so we can list and delete databases
            try:
                client.change_capabilities(
                    {
                        "operation": "grant",
                        "scope": f"Organization/{org}",
                        "user": "User/admin",
                        "roles": ["Role/admin"],
                    }
                )
            except Exception:
                pass
            try:
                dbs = client.get_organization_user_databases(org=org, username="admin")
                for db in dbs:
                    try:
                        client.delete_database(db["name"], team=org)
                    except Exception:
                        pass
            except Exception:
                pass
            # Revoke capabilities before deleting org
            try:
                client.change_capabilities(
                    {
                        "operation": "revoke",
                        "scope": f"Organization/{org}",
                        "user": "User/admin",
                        "roles": ["Role/admin"],
                    }
                )
            except Exception:
                pass
            try:
                client.delete_organization(org)
            except Exception:
                pass

    _cleanup()
    yield
    _cleanup()


def test_not_ok():
    client = Client("http://localhost:6363")
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
    assert org["name"] == "testOrg"
    client.delete_organization("testOrg")
    with pytest.raises(DatabaseError):
        # The org shouldn't exist anymore
        client.get_organization("testOrg")


def test_diff_object(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    # test create db
    client.connect()
    diff = client.diff_object({"test": "wew"}, {"test": "wow"})
    assert diff == {"test": {"@before": "wew", "@after": "wow", "@op": "SwapValue"}}


def test_class_frame(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    db_name = "philosophers" + str(random())
    client.create_database(db_name)
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class", "@id": "Philosopher", "name": "xsd:string"}
    # Add schema and Socrates
    client.insert_document(schema, graph_type=GraphType.SCHEMA)
    assert client.get_class_frame("Philosopher") == {
        "@type": "Class",
        "name": "xsd:string",
    }


def test_woql_substr(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    db_name = "philosophers" + str(random())
    client.create_database(db_name)
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class", "@id": "Philosopher", "name": "xsd:string"}
    # Add schema and Socrates
    client.insert_document(schema, graph_type="schema")
    client.insert_document({"name": "Socrates"})
    result = client.query(
        WOQLQuery()
        .triple("v:Philosopher", "@schema:name", "v:Name")
        .substr("v:Name", 3, "v:Substring", 0, "v:After")
    )
    assert result["bindings"][0]["Substring"]["@value"] == "Soc"


def test_diff_apply_version(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    db_name = "philosophers" + str(random())
    client.create_database(db_name)
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class", "@id": "Philosopher", "name": "xsd:string"}
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
    assert diff[0]["@insert"]["name"] == "Plato"
    assert diff[1]["@insert"]["name"] == "Aristotle"

    # Apply the differences to main with apply
    client.apply("main", "changes", branch="main")

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
    assert log[0]["@type"] == "InitialCommit"


def test_get_document_history(docker_url):
    # Create client
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()

    # Create test database
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)

    # Add a schema
    schema = {
        "@type": "Class",
        "@id": "Person",
        "name": "xsd:string",
        "age": "xsd:integer",
    }
    client.insert_document(schema, graph_type=GraphType.SCHEMA)

    # Insert a document
    person = {"@type": "Person", "@id": "Person/Jane", "name": "Jane", "age": 30}
    client.insert_document(person, commit_msg="Created Person/Jane")

    # Update the document to create history
    person["name"] = "Jane Doe"
    person["age"] = 31
    client.update_document(person, commit_msg="Updated Person/Jane name and age")

    # Update again
    person["age"] = 32
    client.update_document(person, commit_msg="Updated Person/Jane age")

    # Get document history
    history = client.get_document_history("Person/Jane")

    # Assertions
    assert isinstance(history, list)
    assert len(history) >= 3  # At least insert and two updates
    assert all("timestamp" in entry for entry in history)
    assert all(isinstance(entry["timestamp"], dt.datetime) for entry in history)
    assert all("author" in entry for entry in history)
    assert all("message" in entry for entry in history)
    assert all("identifier" in entry for entry in history)

    # Verify messages are in the history (order may vary)
    messages = [entry["message"] for entry in history]
    assert "Created Person/Jane" in messages
    assert "Updated Person/Jane name and age" in messages
    assert "Updated Person/Jane age" in messages

    # Test with pagination
    paginated_history = client.get_document_history("Person/Jane", start=0, count=2)
    assert len(paginated_history) == 2

    # Test with team/db override
    history_override = client.get_document_history(
        "Person/Jane", team="admin", db=db_name
    )
    assert len(history_override) == len(history)

    # Cleanup
    client.delete_database(db_name, "admin")


def test_get_triples(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    client.connect(db=db_name)
    # Add a philosopher schema
    schema = {"@type": "Class", "@id": "Philosopher", "name": "xsd:string"}
    # Add schema and Socrates
    client.insert_document(schema, graph_type="schema")
    schema_triples = client.get_triples(graph_type="schema")
    assert (
        "<schema#Philosopher>\n  a sys:Class ;\n  <schema#name> xsd:string ."
        in schema_triples
    )


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
    client.update_triples(graph_type="schema", content=ttl, commit_msg="Update triples")
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
    client.insert_triples(graph_type="schema", content=ttl, commit_msg="Insert triples")
    client.insert_document({"name": "Socrates"})
    assert len(list(client.get_all_documents())) == 1


def test_get_database(docker_url):
    client = Client(docker_url, user_agent=test_user_agent, team="admin")
    client.connect()
    db_name = "testDB" + str(random())
    client.create_database(db_name, team="admin")
    db = client.get_database(db_name)
    assert db["name"] == db_name
    db_with_team = client.get_database(db_name, team="admin")
    assert db_with_team["name"] == db_name
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

    # BEFORE grant: verify our specific databases are NOT accessible to admin user
    databases_before = client.get_organization_user_databases(
        org=org_name, username="admin"
    )
    db_names_before = {db["name"] for db in databases_before}
    assert (
        db_name not in db_names_before
    ), f"{db_name} should not be accessible before capability grant"
    assert (
        db_name2 not in db_names_before
    ), f"{db_name2} should not be accessible before capability grant"

    # Grant capabilities to admin user for the organization
    capability_change = {
        "operation": "grant",
        "scope": f"Organization/{org_name}",
        "user": "User/admin",
        "roles": ["Role/admin"],
    }
    client.change_capabilities(capability_change)

    # AFTER grant: verify our specific databases ARE accessible to admin user
    databases_after = client.get_organization_user_databases(
        org=org_name, username="admin"
    )
    db_names_after = {db["name"] for db in databases_after}
    # Check both our databases are now accessible (order not guaranteed)
    assert (
        db_name in db_names_after
    ), f"{db_name} should be accessible after capability grant"
    assert (
        db_name2 in db_names_after
    ), f"{db_name2} should be accessible after capability grant"
    # Verify admin team database does NOT appear in organization results
    assert (
        db_name + "admin" not in db_names_after
    ), f"{db_name}admin should not appear in {org_name} results"


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
    assert user["name"] == "test"
    client.delete_user("test")
    with pytest.raises(DatabaseError):
        user = client.get_user("test")


def test_patch(docker_url):
    # create client
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(user="admin", team="admin")
    client.create_database("patch")
    schema = [{"@id": "Person", "@type": "Class", "name": "xsd:string"}]
    instance = [{"@type": "Person", "@id": "Person/Jane", "name": "Jane"}]
    client.insert_document(schema, graph_type="schema")
    client.insert_document(instance)

    patch = Patch(
        json='{"@id": "Person/Jane", "name" : { "@op" : "SwapValue", "@before" : "Jane", "@after": "Janine" }}'
    )

    client.patch_resource(patch)
    doc = client.get_document("Person/Jane")
    assert doc == {"@type": "Person", "@id": "Person/Jane", "name": "Janine"}
    client.delete_database("patch", "admin")


def test_diff_ops(docker_url, test_schema):
    # create client and db
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(user="admin", team="admin")
    client.create_database("test_diff_ops")
    # NOTE: Public API endpoints (jsondiff/jsonpatch) no longer exist
    # Testing authenticated diff/patch only
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
    assert commit_id_result.content == result_patch.content
    assert commit_id_result2.content == result_patch.content
    assert data_version_result.content == result_patch.content
    assert data_version_result2.content == result_patch.content
    assert commit_id_result_all.content == [result_patch.content]
    assert data_version_result_all.content == [result_patch.content]
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


@pytest.mark.skip(reason="Cloud infrastructure no longer operational")
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


@pytest.mark.skipif(
    os.environ.get("TERMINUSDB_TEST_JWT") is None,
    reason="JWT testing not enabled. Set TERMINUSDB_TEST_JWT=1 to enable JWT tests.",
)
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


@pytest.mark.skip(reason="Cloud infrastructure no longer operational")
@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_terminusx(terminusx_token):
    testdb = (
        ("test_happy_" + str(dt.datetime.now()).replace(" ", "") + "_" + str(random()))
        .replace(":", "_")
        .replace(".", "")
    )
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


@pytest.mark.skip(reason="Cloud infrastructure no longer operational")
@pytest.mark.skipif(
    os.environ.get("TERMINUSX_TOKEN") is None, reason="TerminusX token does not exist"
)
def test_terminusx_crazy_path(terminusx_token):
    testdb = (
        ("test_crazy" + str(dt.datetime.now()).replace(" ", "") + "_" + str(random()))
        .replace(":", "_")
        .replace(".", "")
    )
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
