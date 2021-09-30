####
# This is the script for storing the schema of your TerminusDB
# database for your project.
# Use 'terminusdb commit' to commit changes to the database and
# use 'terminusdb sync' to change this file according to
# the exsisting database schema
####
"""
Title: This is an Example
Description: Example to show how schema works
Authors: TerminusDB, Cheuk
"""
from typing import List, Optional, Set

from terminusdb_client.woqlschema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    TaggedUnion,
)


class Country(DocumentTemplate):
    """This is Country.

    Country is a class object in the schema. It's class attributes will be the properties of the object. Therefore, a Country object will have a name which is string and a list of alias names that is called 'also_know_as'
    """

    _key = HashKey(["name"])  # Specifies a specific key generation method to use
    name: str
    also_know_as: List[str]  # Can be a list


class Address(DocumentTemplate):
    """This is address"""

    _subdocument = (
        []
    )  # Subdocument means that it will not be reference when added as a property of another object
    street: str
    postal_code: str
    country: Country  # Type can be a Class that is defined


class Person(DocumentTemplate):
    """This is a person

    Can store the explanation to the attributes in the docstring. Docstrings needs to be in numpydoc format.

    Attributes
    ----------
    name : str
        Name of the person.
    age : int
        Age of the person.
    """

    name: str
    age: int
    friend_of: Set["Person"]  # Using quotation for future reference


class Employee(Person):
    """Employee will inherits the attributes from Person"""

    address_of: Address
    contact_number: Optional[str]  # if Optional is used, it can be None
    managed_by: "Employee"


class Coordinate(DocumentTemplate):
    _abstract = []  # Abstract means that it cannot have any instances
    x: float
    y: float


class Location(Address, Coordinate):
    """Location is inherits from Address and Coordinate

    Class can have multiple inheritance. It will inherits both the attibutes from Address and Coordinate.
    """

    name: str


class Team(EnumTemplate):
    """This is an example for Enum, if a value is not provided, the name of the Enum (e.g. Marketing) will be used as the value."""

    IT = "Information Technology"
    Marketing = ()


class Contact(TaggedUnion):
    """TaggedUnion allow options for types"""

    local_number: int
    international: str
