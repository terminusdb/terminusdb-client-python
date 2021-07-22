from typing import List, Optional, Set

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    TaggedUnion,
    WOQLSchema,
)

# from woql_schema import WOQLSchema, Document, Property, WOQLObject

my_schema = WOQLSchema()
dani_schema = WOQLSchema()


# class MyObject(DocumentTemplate):
#     _schema = my_schema
#
#
# class MyDocument(DocumentTemplate):
#     _schema = my_schema


class Coordinate(DocumentTemplate):
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


class Location(Address, Coordinate):
    pass


class Person(DocumentTemplate):
    """This is a person
    I hate human

    This is extended summary and there will be more things here.
    This is the next line.

    Attributes
    ----------
    x : float
        The X coordinate.
    y : float
        The Y coordinate.
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
    IT = "Information Technology"
    Marketing = "Amazing Marketing"
    # IT = ()
    # Marketing = ()


class Address(DocumentTemplate):
    """This is address"""

    _key = HashKey(["street", "region", "postal_code"])
    _base = "Adddress_"
    _subdocument = []
    _schema = my_schema
    street: str
    postal_code: str


class Contact(TaggedUnion):
    local_number: int
    international: str


home = Address()
home.street = "123 Abc Street"
home._id = "dnkasnklslkd"

cheuk = Employee()
cheuk.address_of = home
cheuk.contact_number = "13123238473897"
# cheuk.commit(client)
# client.commit_objects(cheuk, gavin, matthijs)
# print(Location.__mro__.index(DocumentTemplate))
# print(Address.__mro__)
# print(Employee.__mro__)
# print(Contact.__mro__)
# print(Team.__mro__)
# print(Location._to_dict())
# print(Team._to_dict())
print(my_schema.to_dict())


class AgricultureDiversity(DocumentTemplate):
    """IV.4.2 Agriculture Diversity []"""

    _schema = dani_schema


class Polity(DocumentTemplate):
    _schema = dani_schema
    agriculture_diversity: AgricultureDiversity


#
# print(dani_schema.to_dict())
# print(dir(Person))
# print(Person.to_dict())

# print(my_schema.all_obj())
# print(Team.__members__)
# print(my_schema.to_dict())
# my_schema.commit()
# print(dir(Address))
# print(Contact._to_dict())
# pp.pprint(my_schema.to_dict())

# client = WOQLClient("https://127.0.0.1:6363/", insecure=True)
# client.connect(db="test_docapi")
# #client.create_database("test_docapi")
# #print(client._auth())
# # stuff = my_schema.to_dict()
# # pp.pprint(stuff)
# # client.insert_document(my_schema.to_dict(),
# #                        commit_msg="I am checking in the schema",
# #                        graph_type="schema")
# results = client.get_all_documents(graph_type="schema")
# print(list(results))


# print(cheuk._obj_to_dict())
# print(Person._to_dict())
