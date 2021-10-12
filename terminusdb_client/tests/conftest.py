from typing import List, Optional, Set

import pytest

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    TaggedUnion,
    WOQLSchema,
)


def pytest_addoption(parser):
    parser.addoption("--docker-compose", action="store", default=None)


my_schema = WOQLSchema()


class Coordinate(DocumentTemplate):
    _schema = my_schema
    x: float
    y: float


class Country(DocumentTemplate):
    _schema = my_schema
    name: str
    perimeter: List[Coordinate]


class Address(DocumentTemplate):
    """This is address"""

    _subdocument = []
    _schema = my_schema
    street: str
    postal_code: str
    country: Country


class Person(DocumentTemplate):
    """This is a person

    Attributes
    ----------
    name : str
        Name of the person.
    age : int
        Age of the person.
    """

    _schema = my_schema
    name: str
    age: int
    friend_of: Set["Person"]


class Employee(Person):
    address_of: Address
    contact_number: Optional[str]
    managed_by: "Employee"
    member_of: "Team"
    permisstion: Set["Role"]


class Team(EnumTemplate):
    _schema = my_schema
    IT = "Information Technology"
    Marketing = ()


class Role(EnumTemplate):
    "Test Enum in a set"
    _schema = my_schema
    Admin = ()
    Read = ()
    Write = ()


class Contact(TaggedUnion):
    local_number: int
    international: str


@pytest.fixture(scope="module")
def test_schema():
    return my_schema
