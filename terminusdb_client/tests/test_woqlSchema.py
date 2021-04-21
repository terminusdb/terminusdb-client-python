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
