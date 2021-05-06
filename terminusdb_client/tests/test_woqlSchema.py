from typing import Set

from terminusdb_client.woqlquery.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    ObjectTemplate,
    WOQLSchema,
)

my_schema = WOQLSchema()

# class MyObject(ObjectTemplate):
#     _schema = my_schema
#
# class MyDocument(DocumentTemplate):
#     _schema = my_schema


class Address(ObjectTemplate):
    _schema = my_schema
    street: str
    # country : Country


class Person(DocumentTemplate):
    _schema = my_schema
    name: str
    age: int
    friend_of: Set["Person"]


class Employee(Person):
    address_of: Address
    contact_number: str
    managed_by: "Employee"


class Team(EnumTemplate):
    """This is Team"""

    _schema = my_schema
    IT = ()
    Marketing = ()


# other_schema = my_schema.copy()

# class Country(Property):
#     domain = Address
#     prop_range = "xsd:string"
#     schema = other_schema


def test_schema_construct():
    assert my_schema.all_obj() == {Employee, Person, Address, Team}
    # assert my_schema.all_prop() == {AddressOf, Title, PostCode}
    # assert Employee.properties == {AddressOf, Title}


def test_schema_copy():
    copy_schema = my_schema.copy()
    assert copy_schema.all_obj() == {Employee, Person, Address, Team}
    # assert copy_schema.all_prop() == {AddressOf, Title, PostCode}


# def test_schema_delete():
#     other_schema.delete_property(Title)
#     assert other_schema.all_obj() == {Employee, Address, Team}
#     assert other_schema.all_prop() == {AddressOf, PostCode, Country}
