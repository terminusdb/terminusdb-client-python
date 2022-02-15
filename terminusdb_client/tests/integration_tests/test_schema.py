import datetime as dt

import pytest

from terminusdb_client.errors import DatabaseError
from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlschema.woql_schema import DocumentTemplate, WOQLSchema


def test_create_schema(docker_url, test_schema):
    my_schema = test_schema
    client = WOQLClient(docker_url)
    client.connect()
    client.create_database("test_docapi")
    client.insert_document(
        my_schema, commit_msg="I am checking in the schema", graph_type="schema"
    )
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
    client = WOQLClient(docker_url)
    client.connect()
    client.create_database("test_docapi2")
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


def test_insert_cheuk(docker_url, test_schema):
    my_schema = test_schema
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

    client = WOQLClient(docker_url)
    client.connect(db="test_docapi")
    # client.create_database("test_docapi")
    # print(cheuk._obj_to_dict())
    with pytest.raises(ValueError) as error:
        client.insert_document(home)
        assert str(error.value) == "Subdocument cannot be added directly"
    with pytest.raises(ValueError) as error:
        client.insert_document([cheuk])
        assert (
            str(error.value)
            == f"{uk._capture} is referenced but not captured. Seems you forgot to submit one or more object(s)."
        )
    with pytest.raises(ValueError) as error:
        client.insert_document(cheuk)
        assert (
            str(error.value)
            == "There are uncaptured references. Seems you forgot to submit one or more object(s)."
        )
    assert cheuk._id is None and uk._id is None
    client.insert_document([uk, cheuk], commit_msg="Adding cheuk")
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


def test_getting_and_deleting_cheuk(docker_url):
    assert "cheuk" not in globals()
    assert "cheuk" not in locals()
    client = WOQLClient(docker_url)
    client.connect(db="test_docapi")
    new_schema = WOQLSchema()
    new_schema.from_db(client)
    cheuk = new_schema.import_objects(
        client.get_documents_by_type("Employee", as_list=True)
    )[0]
    result = cheuk._obj_to_dict()
    assert result["address_of"]["postal_code"] == "A12 345"
    assert result["address_of"]["street"] == "123 Abc Street"
    assert result["name"] == "Cheuk"
    assert result["age"] == 21
    assert result["contact_number"] == "07777123456"
    assert result.get("@id")
    client.delete_document(cheuk)
    assert client.get_documents_by_type("Employee", as_list=True) == []


def test_insert_cheuk_again(docker_url, test_schema):
    client = WOQLClient(docker_url)
    client.connect(db="test_docapi")
    new_schema = WOQLSchema()
    new_schema.from_db(client)
    uk = new_schema.import_objects(client.get_document("Country/United%20Kingdom"))

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
            == "name has been used to generated id hance cannot be changed."
        )

    cheuk = Employee()
    cheuk.permisstion = {Role.admin, Role.read}
    cheuk.address_of = home
    cheuk.contact_number = "07777123456"
    cheuk.age = 21
    cheuk.name = "Cheuk"
    cheuk.managed_by = cheuk
    cheuk.friend_of = {cheuk}
    cheuk.member_of = Team.information_technology
    cheuk._id = "Cheuk is back"

    with pytest.raises(ValueError) as error:
        client.update_document([uk])
        assert (
            str(error.value)
            == f"{location._capture} is referenced but not captured. Seems you forgot to submit one or more object(s)."
        )
    with pytest.raises(ValueError) as error:
        client.insert_document(uk)
        assert (
            str(error.value)
            == "There are uncaptured references. Seems you forgot to submit one or more object(s)."
        )

    client.update_document([location, uk, cheuk], commit_msg="Adding cheuk again")
    assert location._backend_id and location._id
    location.x = -0.7
    result = client.replace_document([location], commit_msg="Fixing location")
    assert len(result) == 1
    result = client.get_all_documents()
    for item in result:
        if item.get("@type") == "Country":
            assert item["name"] == "United Kingdom"
            assert item["perimeter"]
        elif item.get("@type") == "Employee":
            assert item["@id"] == "Employee/Cheuk%20is%20back"
            assert item["address_of"]["postal_code"] == "A12 345"
            assert item["address_of"]["street"] == "123 Abc Street"
            assert item["name"] == "Cheuk"
            assert item["age"] == 21
            assert item["contact_number"] == "07777123456"
            assert item["managed_by"] == item["@id"]
        elif item.get("@type") == "Coordinate":
            assert item["x"] == -0.7
            assert item["y"] == 51.3
        else:
            raise AssertionError()


def test_get_data_version(docker_url):
    client = WOQLClient(docker_url)
    client.connect(db="test_docapi")
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
        {"@type": "Employee", "@id": "Employee/Cheuk%20is%20back"},
        get_data_version=True,
        as_list=True,
    )
    assert version
    new_schema = WOQLSchema().from_db(client)
    cheuk = new_schema.import_objects(result[0])
    cheuk.name = "Cheuk Ting Ho"
    client.replace_document(cheuk, last_data_version=version)
    result, version2 = client.get_document(
        "Employee/Cheuk%20is%20back", get_data_version=True
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
    client = WOQLClient(docker_url)
    client.connect()
    client.create_database("test_datetime")
    client.insert_document(CheckDatetime, graph_type="schema")
    client.insert_document(test_obj)
