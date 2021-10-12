from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlschema.woql_schema import WOQLSchema

# from woql_schema import WOQLSchema, Document, Property, WOQLObject
#
# my_schema = WOQLSchema()
#
#
# class Coordinate(DocumentTemplate):
#     _schema = my_schema
#     x: float
#     y: float
#
#
# class Country(DocumentTemplate):
#     _schema = my_schema
#     name: str
#     perimeter: List[Coordinate]
#
#
# class Address(DocumentTemplate):
#     """This is address"""
#
#     # _key = HashKey(["street", "postal_code"])
#     # _key = LexicalKey(["street", "postal_code"])
#     # _base = "Adddress_"
#     _subdocument = []
#     _schema = my_schema
#     street: str
#     postal_code: str
#     country: Country
#
#
# class Person(DocumentTemplate):
#     """This is a person
#
#     Attributes
#     ----------
#     name : str
#         Name of the person.
#     age : int
#         Age of the person.
#     """
#
#     _schema = my_schema
#     name: str
#     age: int
#     friend_of: Set["Person"]
#
#
# class Employee(Person):
#     address_of: Address
#     contact_number: Optional[str]
#     managed_by: "Employee"
#     member_of: "Team"
#     permisstion: Set["Role"]
#
#
# class Team(EnumTemplate):
#     _schema = my_schema
#     IT = "Information Technology"
#     Marketing = ()
#
#
# class Role(EnumTemplate):
#     "Test Enum in a set"
#     _schema = my_schema
#     Admin = ()
#     Read = ()
#     Write = ()
#
#
# class Contact(TaggedUnion):
#     local_number: int
#     international: str


def test_create_schema(docker_url, test_schema):
    my_schema = test_schema
    client = WOQLClient(docker_url)
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
                "Role",
            ]
        elif "@type" in item:
            assert item["@type"] == "@context"
        else:
            raise AssertionError()


def test_create_schema2(docker_url, test_schema):
    my_schema = test_schema
    client = WOQLClient(docker_url)
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
                "Role",
            ]
        elif "@type" in item:
            assert item["@type"] == "@context"
        else:
            raise AssertionError()


def test_insert_cheuk(docker_url, test_schema):
    my_schema = test_schema
    Country = my_schema.object.get("Country")
    Address = my_schema.object.get("Address")
    Employee = my_schema.object.get("Employee")
    Role = my_schema.object.get("Role")
    Team = my_schema.object.get("Team")

    uk = Country()
    uk.name = "United Kingdom"
    uk.perimeter = []

    home = Address()
    home.street = "123 Abc Street"
    home.country = uk
    home.postal_code = "A12 345"

    cheuk = Employee()
    cheuk.permisstion = {Role.Admin, Role.Read}
    cheuk.address_of = home
    cheuk.contact_number = "07777123456"
    cheuk.age = 21
    cheuk.name = "Cheuk"
    cheuk.managed_by = cheuk
    cheuk.friend_of = {cheuk}
    cheuk.member_of = Team.IT

    client = WOQLClient(docker_url)
    client.connect(db="test_docapi")
    # client.create_database("test_docapi")
    # print(cheuk._obj_to_dict())
    client.insert_document([uk, home, cheuk], commit_msg="Adding cheuk")
    result = client.get_all_documents()
    for item in result:
        if item.get("@type") == "Country":
            assert item["name"] == "United Kingdom"
        elif item.get("@type") == "Employee":
            assert item["address_of"]["postal_code"] == "A12 345"
            assert item["address_of"]["street"] == "123 Abc Street"
            assert item["name"] == "Cheuk"
            assert item["age"] == 21
            assert item["contact_number"] == "07777123456"
            assert item["managed_by"] == item["@id"]
        else:
            raise AssertionError()


def test_getting_and_deleting_cheuk(docker_url):
    assert "cheuk" not in globals()
    assert "cheuk" not in locals()
    client = WOQLClient(docker_url)
    client.connect(db="test_docapi")
    new_schema = WOQLSchema()
    new_schema.from_db(client)
    cheuk = new_schema.import_objects(
        client.get_documents_by_type("Employee", as_list=True)
    )[0]
    result = cheuk._obj_to_dict()
    assert result["address_of"]["postal_code"] == "A12 345"
    assert result["address_of"]["street"] == "123 Abc Street"
    assert result["name"] == "Cheuk"
    assert result["age"] == 21
    assert result["contact_number"] == "07777123456"
    client.delete_document(cheuk)
    assert client.get_documents_by_type("Employee", as_list=True) == []
