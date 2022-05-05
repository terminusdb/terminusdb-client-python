from typing import List, Optional, Set

import pytest

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    LexicalKey,
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
    _key = LexicalKey(["name"])
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
    _schema = my_schema
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


class MockResponse:
    def __init__(self, text, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.json_data


def mocked_request_success(*args, **kwargs):
    return MockResponse(
        '[\n  "terminusdb:///data/CheckDatetime/172f8b3ab17c8d1360d05e185694b118c04f32f7c6e65303a6698302a9fb84f6",\n  "terminusdb:///data/CheckDatetime/27a05710219b4f87305a87d06d494651f18113cded461cf251ccd0d409f1d6e9",\n  "terminusdb:///data/CheckDatetime/36599b3442bec7fd852bf844edfbd66a63b30acbc4e14c6d138bf91d31cccd80",\n  "terminusdb:///data/CheckDatetime/571f014ff5c26e634290bd0157cbffefbdf2d8727eb172812643f23027aa0770",\n  "terminusdb:///data/CheckDatetime/8e9580989b682e04761c938f8a9e71254aee176918fee4a8235e938348897cc0",\n  "terminusdb:///data/CheckDatetime/b8b0e7d8eeb06288bc41b34f93f47f13d28c9c5eb705ab3361c47ead6a46b670",\n  "terminusdb:///data/CheckDatetime/d576726340dc7dbc9726205748ceaab0d7e659b07defc8f9daeafb87a4b93da4",\n  "terminusdb:///data/CheckDatetime/01dc05d2d169d2bf42c9e4eb3e3b09815831bff22f4f5c22b317f551b8403bc9",\n  "terminusdb:///data/CheckDatetime/c4b2eea8958c5bc5652c346382d1ede355b6801427e416bdb1e440c0218bd5e1",\n  "terminusdb:///data/CheckDatetime/299f78c3292a05428f896b7d08424ae870203ea0d0b537147bd35239424b0082"\n]\n',
        {"key1": "value1"},
        200,
    )


def mocked_request_insert_delete(*args, **kwargs):
    return MockResponse('{"inserts": 1, "deletes":0}', {"key1": "value1"}, 200)
