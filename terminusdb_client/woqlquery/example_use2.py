from typing import List, Optional, Set

from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    ObjectTemplate,
    TaggedUnion,
    WOQLSchema,
)

import pprint as pp
# from woql_schema import WOQLSchema, Document, Property, WOQLObject

my_schema = WOQLSchema()


class MyObject(ObjectTemplate):
    _schema = my_schema


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


class Address(MyDocument):
    """This is address"""

    _key = HashKey(["street", "region", "postal_code"])
    _base = "Adddress_"
    street: str
    region: "Region"
    postal_code: str


class Contact(TaggedUnion):
    local_number: int
    international: str


home = Address()
home.street = "123 Abc Street"
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
# print(dir(Address))
# print(Contact._to_dict())
# pp.pprint(my_schema.to_dict())

client = WOQLClient("https://127.0.0.1:6363/", insecure=True)
client.connect(db="test_docapi")
#client.create_database("test_docapi")
#print(client._auth())
stuff = my_schema.to_dict()
pp.pprint(stuff)
client.insert_document(my_schema.to_dict(),
                       commit_msg="I am checking in the schema",
                       graph_type="schema")

