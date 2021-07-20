from typing import List, Optional, Set

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    ObjectTemplate,
    TaggedUnion,
    ValueHashKey,
)


class Coordinate(ObjectTemplate):
    x: float
    y: float


class Country(DocumentTemplate):
    _key = ValueHashKey()
    name: str
    perimeter: List[Coordinate]


class Address(DocumentTemplate):
    """This is address"""

    _key = HashKey(["street", "postal_code"])
    _subdocument = []
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

    name: str
    age: int
    friend_of: Set["Person"]


class Employee(Person):
    address_of: Address
    contact_number: Optional[str]
    managed_by: "Employee"


class Team(EnumTemplate):
    IT = ()
    Marketing = ()


class Contact(TaggedUnion):
    local_number: int
    international: str
