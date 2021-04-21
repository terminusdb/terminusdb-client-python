from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.woql_library import WOQLLib
from terminusdb_client.woqlquery.woql_schema import (
    Document,
    Enums,
    Property,
    WOQLObject,
    WOQLSchema,
)

my_schema = WOQLSchema()


class Employee(Document):
    schema = my_schema


class Address(WOQLObject):
    schema = my_schema


class Team(Enums):
    """This is Team"""

    value_set = {"IT", "Marketing"}
    schema = my_schema


class AddressOf(Property):
    domain = Employee
    prop_range = Address
    schema = my_schema


class Title(Property):
    domain = Employee
    prop_range = "xsd:string"
    schema = my_schema


class PostCode(Property):
    domain = Address
    prop_range = "xsd:string"
    schema = my_schema


def test_schema_construct():
    assert my_schema.all_obj() == {Employee, Address, Team}
    assert my_schema.all_prop() == {AddressOf, Title, PostCode}
    assert Employee.properties == {AddressOf, Title}


def test_schema_copy():
    copy_schema = my_schema.copy()
    assert copy_schema.all_obj() == {Employee, Address, Team}
    assert copy_schema.all_prop() == {AddressOf, Title, PostCode}


def test_happy_schema(docker_url):
    # create client
    client = WOQLClient(docker_url)
    client.connect()
    client.create_database("test_happy_schema")
    my_schema.commit(client)
    objects = set()
    for item in WOQLLib().classes().execute(client).get("bindings"):
        objects.add(item["Class Name"]["@value"])
    assert objects == {"Employee", "Address", "Team"}
    properties = set()
    for item in WOQLLib().property().execute(client).get("bindings"):
        properties.add(item["Property Name"]["@value"])
    assert properties == {"AddressOf", "Title", "PostCode"}
