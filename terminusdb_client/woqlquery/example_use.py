from terminusdb_client.woqlquery.woql_schema import (
    Document,
    Enums,
    Property,
    WOQLObject,
    WOQLSchema,
)

# from woql_schema import WOQLSchema, Document, Property, WOQLObject

my_schema = WOQLSchema()


class Employee(Document):
    # properties = [AddressOf, ContactNum, ManagedBy, Title, TeamMemberOf]
    schema = my_schema


class Address(WOQLObject):
    # properties = [Postcode, StreetName, StreetNum, TownCity]
    schema = my_schema


class Team(Enums):
    """This is Team"""

    value_set = {"IT", "Marketing"}
    schema = my_schema


class AddressOf(Property):
    domain = Employee
    prop_range = Address
    schema = my_schema


# print(my_schema)
my_schema.commit(None)
my_other_schema = my_schema.copy()
# my_other_schema = WOQLSchema()


class Title(Property):
    domain = Employee
    prop_range = "xsd:string"
    schema = my_other_schema


class Intern(Employee):
    schema = my_other_schema


# print("Intern")
# print(Intern.properties)

my_other_schema.commit(None)

# for item in my_other_schema.all_prop():
#     print(item)

# print(Team)
