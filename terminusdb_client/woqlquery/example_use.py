from .woql_schema import Document, Property, WOQLObject


class Employee(Document):
    properties = [AddressOf, ContactNum, ManagedBy, Title, TeamMemberOf]


class Address(WOQLObject):
    properties = [Postcode, StreetName, StreetNum, TownCity]


class Team(Enums):
    value_list = ["IT", "Marketing"]


class AddressOf(Property):
    domain = []
