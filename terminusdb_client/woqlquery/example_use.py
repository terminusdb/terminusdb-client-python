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
    value_set = {"IT", "Marketing"}


class AddressOf(Property):
    domain = [Employee]


my_schema = WOQLSchema([WOQLObject, Property])

my_schema.commit(None)
