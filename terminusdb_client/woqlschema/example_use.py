from typing import List, Optional, Set

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    WOQLSchema,
)

# from woql_schema import WOQLSchema, Document, Property, WOQLObject

my_schema = WOQLSchema()


class MyDocument(DocumentTemplate):
    _schema = my_schema


class Coordinate(MyObject):
    x: float
    y: float


class Country(MyDocument):
    name: str
    perimeter: List[Coordinate]


class Address(MyObject):
    street: str
    country: Country


class Person(MyDocument):
    """This is a person
    attribute
    =========
    name: this is the name of that Person
    age: age of that person, integer
    friend_of: who is this person friend's with"""

    name: str
    age: int
    friend_of: Set["Person"]


class Employee(Person):
    address_of: Address
    contact_number: Optional[str]
    managed_by: "Employee"


class Team(EnumTemplate):
    _schema = my_schema
    IT = ()
    Marketing = ()


# cheuk = Employee()
# cheuk.contact_number = "13123238473897"
# cheuk.commit(client)
# client.commit_objects(cheuk, gavin, matthijs)

# print(dir(Person))
# print(Person.to_dict())

# print(my_schema.all_obj())
# print(Team.__members__)
# print(my_schema.to_dict())
# my_schema.commit()

print(Team.to_dict())
