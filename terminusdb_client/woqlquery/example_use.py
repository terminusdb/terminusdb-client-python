from terminusdb_client.woqlquery.woql_schema import (
    Document,
    Enums,
    Property,
    WOQLObject,
    WOQLSchema,
)

# from woql_schema import WOQLSchema, Document, Property, WOQLObject


class Employee(Document):
    # properties = [AddressOf, ContactNum, ManagedBy, Title, TeamMemberOf]
    pass


class Address(WOQLObject):
    # properties = [Postcode, StreetName, StreetNum, TownCity]
    pass


class Team(Enums):
    """This is Team"""

    value_set = {"IT", "Marketing"}


class AddressOf(Property):
    domain = [Employee]
    prop_range = [Address]


print(Team.__name__)

my_schema = WOQLSchema()

my_schema.commit(None)


class Title(Property):
    domain = [Employee]
    prop_range = ["xsd:string"]


my_other_schema = WOQLSchema()

my_other_schema.commit(None)
