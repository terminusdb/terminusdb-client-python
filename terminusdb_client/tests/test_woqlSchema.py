from typing import List, Set

import pytest

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    WOQLSchema,
)

my_schema = WOQLSchema()


class Abstract(DocumentTemplate):
    """This is abstract class"""

    _schema = WOQLSchema()
    _abstract = []
    name: str


class TypeCheck(DocumentTemplate):
    """For checking instance types"""

    _schema = WOQLSchema()
    name: str
    age: int


class Coordinate(DocumentTemplate):
    """Coordinate of location.

    Coordinate to identify the location of a place on earth, it could be found from Google map.

    Attributes
    ----------
    x : float
        The X coordinate.
    y : float
        The Y coordinate.
    """

    _schema = my_schema
    x: float
    y: float


class Country(DocumentTemplate):
    _schema = my_schema
    name: str
    perimeter: List[Coordinate]


class Address(DocumentTemplate):
    _schema = my_schema
    street: str
    country: Country


class Person(DocumentTemplate):
    _schema = my_schema
    name: str
    age: int
    friend_of: Set["Person"]


class Employee(Person):
    _schema = my_schema
    address_of: Address
    contact_number: str
    managed_by: "Employee"


class Team(EnumTemplate):
    _schema = my_schema
    IT = ()
    Marketing = ()


def test_schema_construct():
    assert my_schema.all_obj() == {Employee, Person, Address, Team, Country, Coordinate}
    # assert my_schema.all_prop() == {AddressOf, Title, PostCode}
    # assert Employee.properties == {AddressOf, Title}


def test_schema_copy():
    copy_schema = my_schema.copy()
    assert copy_schema.all_obj() == {
        Employee,
        Person,
        Address,
        Team,
        Country,
        Coordinate,
    }
    # assert copy_schema.all_prop() == {AddressOf, Title, PostCode}


def test_abstract_class():
    with pytest.raises(TypeError):
        Abstract()


def test_type_check():
    test_obj = TypeCheck()
    with pytest.raises(TypeError):
        test_obj.name = 123
    with pytest.raises(TypeError):
        test_obj.age = "not a number"


# def test_schema_delete():
#     other_schema.delete_property(Title)
#     assert other_schema.all_obj() == {Employee, Address, Team}
#     assert other_schema.all_prop() == {AddressOf, PostCode, Country}
