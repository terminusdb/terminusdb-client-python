import datetime as dt

import pytest

from terminusdb_client.errors import DatabaseError
from terminusdb_client.client.Client import Client
from terminusdb_client.woqlschema.woql_schema import DocumentTemplate, WOQLSchema

test_user_agent = "terminusdb-client-python-tests"

_SCHEMA_TEST_DBS = [
    "test_docapi",
    "test_docapi2",
    "test_datetime",
    "test_compress_data",
    "test_repeated_load",
    "test_repeated_load_fails",
]


@pytest.fixture(scope="module", autouse=True)
def cleanup_schema_databases(docker_url):
    """Delete stale databases before the module and clean up after."""
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    for db in _SCHEMA_TEST_DBS:
        try:
            client.delete_database(db)
        except Exception:
            pass
    yield
    for db in _SCHEMA_TEST_DBS:
        try:
            client.delete_database(db)
        except Exception:
            pass


# Static prefix for test databases - unique enough to avoid clashes with real databases
TEST_DB_PREFIX = "pyclient_test_xk7q_"


def unique_db_name(prefix):
    """Generate a unique database name with static test prefix to avoid conflicts."""
    return f"{TEST_DB_PREFIX}{prefix}"


@pytest.fixture(scope="module")
def schema_test_db(docker_url, test_schema):
    """Create a shared test database for schema tests that need it."""
    db_name = unique_db_name("test_schema_docapi")
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database(db_name)
    client.insert_document(
        test_schema, commit_msg="I am checking in the schema", graph_type="schema"
    )
    yield db_name, client, test_schema
    # Cleanup
    try:
        client.delete_database(db_name)
    except Exception:
        pass


def test_create_schema(schema_test_db):
    db_name, client, my_schema = schema_test_db
    client.connect(db=db_name)
    result = client.get_all_documents(graph_type="schema")
    for item in result:
        if "@id" in item:
            assert item["@id"] in [
                "Employee",
                "Person",
                "Address",
                "Team",
                "Country",
                "Coordinate",
                "Role",
            ]
        elif "@type" in item:
            assert item["@type"] == "@context"
        else:
            raise AssertionError()


def test_create_schema2(docker_url, test_schema):
    my_schema = test_schema
    db_name = unique_db_name("test_schema2")
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database(db_name)
    try:
        my_schema.commit(client, "I am checking in the schema")
        result = client.get_all_documents(graph_type="schema")
        for item in result:
            if "@id" in item:
                assert item["@id"] in [
                    "Employee",
                    "Person",
                    "Address",
                    "Team",
                    "Country",
                    "Coordinate",
                    "Role",
                ]
            elif "@type" in item:
                assert item["@type"] == "@context"
            else:
                raise AssertionError()
    finally:
        client.delete_database(db_name)


def test_insert_cheuk(schema_test_db):
    db_name, client, my_schema = schema_test_db
    Country = my_schema.object.get("Country")
    Address = my_schema.object.get("Address")
    Employee = my_schema.object.get("Employee")
    Role = my_schema.object.get("Role")
    Team = my_schema.object.get("Team")

    uk = Country()
    uk.name = "United Kingdom"
    uk.perimeter = []

    home = Address()
    home.street = "123 Abc Street"
    home.country = uk
    home.postal_code = "A12 345"

    cheuk = Employee()
    cheuk.permisstion = {Role.Admin, Role.Read}
    cheuk.address_of = home
    cheuk.contact_number = "07777123456"
    cheuk.age = 21
    cheuk.name = "Cheuk"
    cheuk.managed_by = cheuk
    cheuk.friend_of = {cheuk}
    cheuk.member_of = Team.IT

    client.connect(db=db_name)
    with pytest.raises(ValueError) as error:
        client.insert_document(home)
        assert str(error.value) == "Subdocument cannot be added directly"
    assert cheuk._id is None and uk._id is None
    client.insert_document([cheuk], commit_msg="Adding cheuk")
    assert cheuk._backend_id and cheuk._id
    assert uk._backend_id and uk._id
    result = client.get_all_documents()
    for item in result:
        if item.get("@type") == "Country":
            assert item["name"] == "United Kingdom"
        elif item.get("@type") == "Employee":
            assert item["address_of"]["postal_code"] == "A12 345"
            assert item["address_of"]["street"] == "123 Abc Street"
            assert item["name"] == "Cheuk"
            assert item["age"] == 21
            assert item["contact_number"] == "07777123456"
            assert item["managed_by"] == item["@id"]
        else:
            raise AssertionError()


def test_getting_and_deleting_cheuk(schema_test_db):
    db_name, client, test_schema = schema_test_db
    assert "cheuk" not in globals()
    assert "cheuk" not in locals()
    client.connect(db=db_name)

    # Set up: Create test data first
    Country = test_schema.object.get("Country")
    Address = test_schema.object.get("Address")
    Employee = test_schema.object.get("Employee")
    Role = test_schema.object.get("Role")
    Team = test_schema.object.get("Team")

    uk = Country()
    uk.name = "UK Test 1"
    uk.perimeter = []

    home = Address()
    home.street = "123 Abc Street"
    home.country = uk
    home.postal_code = "A12 345"

    cheuk_setup = Employee()
    cheuk_setup.permisstion = {Role.Admin, Role.Read}
    cheuk_setup.address_of = home
    cheuk_setup.contact_number = "07777123456"
    cheuk_setup.age = 21
    cheuk_setup.name = "Cheuk Test 1"
    cheuk_setup._id = "cheuk_test_1"
    cheuk_setup.managed_by = cheuk_setup
    cheuk_setup.friend_of = {cheuk_setup}
    cheuk_setup.member_of = Team.IT

    client.insert_document(
        [cheuk_setup], commit_msg="Setup for test_getting_and_deleting_cheuk"
    )

    # Test: Load and verify
    new_schema = WOQLSchema()
    new_schema.from_db(client)
    cheuk = new_schema.import_objects(client.get_document("Employee/cheuk_test_1"))
    result = cheuk._obj_to_dict()[0]
    assert result["address_of"]["postal_code"] == "A12 345"
    assert result["address_of"]["street"] == "123 Abc Street"
    assert result["name"] == "Cheuk Test 1"
    assert result["age"] == 21
    assert result["contact_number"] == "07777123456"
    assert result.get("@id")
    # Delete the document - this is the main test
    client.delete_document(cheuk)


def test_insert_cheuk_again(schema_test_db):
    db_name, client, test_schema = schema_test_db
    client.connect(db=db_name)

    # Set up: Create Country first
    Country = test_schema.object.get("Country")
    uk_setup = Country()
    uk_setup.name = "UK Test 2"
    uk_setup.perimeter = []
    client.insert_document(
        [uk_setup], commit_msg="Setup country for test_insert_cheuk_again"
    )

    # Test: Load country and create employee
    new_schema = WOQLSchema()
    new_schema.from_db(client)
    uk = new_schema.import_objects(client.get_document("Country/UK%20Test%202"))

    Address = new_schema.object.get("Address")
    Employee = new_schema.object.get("Employee")
    Role = new_schema.object.get("Role")
    Team = new_schema.object.get("Team")
    Coordinate = new_schema.object.get("Coordinate")

    home = Address()
    home.street = "123 Abc Street"
    home.country = uk
    home.postal_code = "A12 345"

    location = Coordinate(x=0.7, y=51.3)
    uk.perimeter = [location]
    with pytest.raises(ValueError) as error:
        uk.name = "United Kingdom of Great Britain and Northern Ireland"
        assert (
            str(error.value)
            == "name has been used to generate the id, hence cannot be changed."
        )

    cheuk = Employee()
    cheuk.permisstion = {Role.admin, Role.read}
    cheuk.address_of = home
    cheuk.contact_number = "07777123456"
    cheuk.age = 21
    cheuk.name = "Cheuk Test 2"
    cheuk.managed_by = cheuk
    cheuk.friend_of = {cheuk}
    cheuk.member_of = Team.information_technology
    cheuk._id = "cheuk_test_2"

    client.update_document([location, uk, cheuk], commit_msg="Adding cheuk again")
    assert location._backend_id and location._id
    location.x = -0.7
    result = client.replace_document([location], commit_msg="Fixing location")
    assert len(result) == 1
    result = client.get_all_documents()

    # Verify specific documents we created
    found_country = False
    found_employee = False
    found_coordinate = False

    for item in result:
        if item.get("@type") == "Country" and item.get("name") == "UK Test 2":
            assert item["perimeter"]
            found_country = True
        elif (
            item.get("@type") == "Employee"
            and item.get("@id") == "Employee/cheuk_test_2"
        ):
            assert item["address_of"]["postal_code"] == "A12 345"
            assert item["address_of"]["street"] == "123 Abc Street"
            assert item["name"] == "Cheuk Test 2"
            assert item["age"] == 21
            assert item["contact_number"] == "07777123456"
            assert item["managed_by"] == item["@id"]
            found_employee = True
        elif item.get("@type") == "Coordinate" and item.get("x") == -0.7:
            assert item["y"] == 51.3
            found_coordinate = True

    assert found_country, "UK Test 2 country not found"
    assert found_employee, "cheuk_test_2 employee not found"
    assert found_coordinate, "Coordinate not found"


def test_get_data_version(schema_test_db):
    db_name, client, test_schema = schema_test_db
    client.connect(db=db_name)

    # Set up: Create test employee for data version tests
    Country = test_schema.object.get("Country")
    Address = test_schema.object.get("Address")
    Employee = test_schema.object.get("Employee")
    Role = test_schema.object.get("Role")
    Team = test_schema.object.get("Team")
    Coordinate = test_schema.object.get("Coordinate")

    uk = Country()
    uk.name = "UK Test 3"
    uk.perimeter = []

    home = Address()
    home.street = "123 Abc Street"
    home.country = uk
    home.postal_code = "A12 345"

    location = Coordinate(x=0.7, y=51.3)
    uk.perimeter = [location]

    cheuk = Employee()
    cheuk.permisstion = {Role.Admin, Role.Read}
    cheuk.address_of = home
    cheuk.contact_number = "07777123456"
    cheuk.age = 21
    cheuk.name = "Cheuk Test 3"
    cheuk.managed_by = cheuk
    cheuk.friend_of = {cheuk}
    cheuk.member_of = Team.IT
    cheuk._id = "cheuk_test_3"

    client.insert_document(
        [location, uk, cheuk], commit_msg="Setup for test_get_data_version"
    )
    result, version = client.get_all_branches(get_data_version=True)
    assert version
    result, version = client.get_all_documents(
        graph_type="schema", get_data_version=True
    )
    assert version
    result, version = client.get_all_documents(
        graph_type="schema", get_data_version=True, as_list=True
    )
    assert version
    result, version = client.get_documents_by_type(
        "Class", graph_type="schema", get_data_version=True
    )
    assert version
    result, version = client.get_documents_by_type(
        "Class", graph_type="schema", get_data_version=True, as_list=True
    )
    assert version
    result, version = client.get_document(
        "Team", graph_type="schema", get_data_version=True
    )
    assert version
    result, version = client.query_document(
        {"@type": "Employee", "@id": "Employee/cheuk_test_3"},
        get_data_version=True,
        as_list=True,
    )
    assert version
    new_schema = WOQLSchema().from_db(client)
    cheuk = new_schema.import_objects(result[0])
    cheuk.name = "Cheuk Ting Ho"
    client.replace_document(cheuk, last_data_version=version)
    result, version2 = client.get_document(
        "Employee/cheuk_test_3", get_data_version=True
    )
    assert version != version2
    with pytest.raises(DatabaseError) as error:
        client.update_document(cheuk, last_data_version=version)
        assert (
            "Requested data version in header does not match actual data version."
            in str(error.value)
        )
    client.update_document(cheuk, last_data_version=version2)

    _, version = client.get_all_documents(get_data_version=True)
    Country = new_schema.object.get("Country")
    ireland = Country()
    ireland.name = "The Republic of Ireland"
    ireland.perimeter = []
    client.insert_document(ireland, last_data_version=version)
    with pytest.raises(DatabaseError) as error:
        client.delete_document(ireland, last_data_version=version)
        assert (
            "Requested data version in header does not match actual data version."
            in str(error.value)
        )
    _, version2 = client.get_all_documents(get_data_version=True)
    client.delete_document(ireland, last_data_version=version2)


class CheckDatetime(DocumentTemplate):

    datetime: dt.datetime
    duration: dt.timedelta


def test_datetime_backend(docker_url):
    datetime_obj = dt.datetime(2019, 5, 18, 15, 17, 8, 132263)
    delta = dt.timedelta(
        days=50,
        seconds=27,
        microseconds=10,
        milliseconds=29000,
        minutes=5,
        hours=8,
        weeks=2,
    )
    test_obj = CheckDatetime(datetime=datetime_obj, duration=delta)
    db_name = unique_db_name("test_datetime")
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database(db_name)
    try:
        client.insert_document(CheckDatetime, graph_type="schema")
        client.insert_document(test_obj)
    finally:
        client.delete_database(db_name)


def test_compress_data(docker_url):
    datetime_obj = dt.datetime(2019, 5, 18, 15, 17, 8, 132263)
    delta = dt.timedelta(
        days=50,
        seconds=27,
        microseconds=10,
        milliseconds=29000,
        minutes=5,
        hours=8,
        weeks=2,
    )
    test_obj = [CheckDatetime(datetime=datetime_obj, duration=delta) for _ in range(10)]
    db_name = unique_db_name("test_compress")
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database(db_name)
    try:
        client.insert_document(CheckDatetime, graph_type="schema")
        client.insert_document(test_obj, compress=0)
        test_obj2 = client.get_all_documents(as_list=True)
        assert len(test_obj2) == 10
    finally:
        client.delete_database(db_name)


def test_repeated_object_load(docker_url, test_schema):
    schema = test_schema
    db_name = unique_db_name("test_repeated_load")
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database(db_name)
    try:
        client.insert_document(
            schema, commit_msg="I am checking in the schema", graph_type="schema"
        )
        [country_id] = client.insert_document(
            {"@type": "Country", "name": "Romania", "perimeter": []}
        )
        obj = client.get_document(country_id)
        schema.import_objects(obj)
        obj2 = client.get_document(country_id)
        schema.import_objects(obj2)
    finally:
        client.delete_database(db_name)


def test_key_change_raises_exception(docker_url, test_schema):
    schema = test_schema
    db_name = unique_db_name("test_key_change")
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    client.create_database(db_name)
    try:
        client.insert_document(
            schema, commit_msg="I am checking in the schema", graph_type="schema"
        )
        [country_id] = client.insert_document(
            {"@type": "Country", "name": "Romania", "perimeter": []}
        )
        obj = client.get_document(country_id)
        local_obj = schema.import_objects(obj)
        with pytest.raises(
            ValueError,
            match=r"name has been used to generate the id, hence cannot be changed.",
        ):
            local_obj.name = "France"
    finally:
        client.delete_database(db_name)
