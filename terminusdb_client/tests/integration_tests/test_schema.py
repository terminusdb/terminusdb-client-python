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

# from woql_schema import WOQLSchema, Document, Property, WOQLObject

my_schema = WOQLSchema()


class Coordinate(ObjectTemplate):
    _schema = my_schema
    x: float
    y: float


class Country(DocumentTemplate):
    _schema = my_schema
    name: str
    perimeter: List[Coordinate]


class Address(DocumentTemplate):
    """This is address"""

    _key = HashKey(["street", "postal_code", "country"])
    _base = "Adddress_"
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


class Team(EnumTemplate):
    _schema = my_schema
    IT = ()
    Marketing = ()


class Contact(TaggedUnion):
    local_number: int
    international: str


# home = Address()
# home.street = "123 Abc Street"
# home._id = "dnkasnklslkd"
#
# cheuk = Employee()
# cheuk.address_of = home
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
def test_create_schema(docker_url):
    client = WOQLClient(docker_url, insecure=True)
    client.connect()
    client.create_database("test_docapi")
    client.insert_document(
        my_schema, commit_msg="I am checking in the schema", graph_type="schema"
    )
    result = client.get_all_documents(graph_type="schema")
    for item in result:
        if "@id" in item:
            assert item["@id"] in [
                "Employee",
                "Person",
                "Address",
                "Team",
                "Country",
                "Coordinate",
            ]
        elif "@type" in item:
            assert item["@type"] == "@context"
        else:
            assert False


def test_create_schema2(docker_url):
    client = WOQLClient(docker_url, insecure=True)
    client.connect()
    client.create_database("test_docapi2")
    my_schema.commit(client, "I am checking in the schema")
    result = client.get_all_documents(graph_type="schema")
    for item in result:
        if "@id" in item:
            assert item["@id"] in [
                "Employee",
                "Person",
                "Address",
                "Team",
                "Country",
                "Coordinate",
            ]
        elif "@type" in item:
            assert item["@type"] == "@context"
        else:
            assert False


def test_insert_cheuk(docker_url):
    uk = Country()
    uk.name = "United Kingdom"

    home = Address()
    home.street = "123 Abc Street"
    home.country = uk
    home.postal_code = "A12 345"

    cheuk = Employee()
    cheuk.address_of = home
    cheuk.contact_number = "07777123456"
    cheuk.age = 21
    cheuk.name = "Cheuk"
    # cheuk.managed_by = cheuk

    client = WOQLClient(docker_url, insecure=True)
    client.connect(db="test_docapi")
    # client.create_database("test_docapi")
    client.insert_document([uk, home, cheuk], commit_msg="Adding cheuk")


# print(cheuk._obj_to_dict())
# print(Person._to_dict())
