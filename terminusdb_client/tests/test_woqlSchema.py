import pytest

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    WOQLSchema,
    _check_cycling,
)

# my_schema = WOQLSchema()
cycling_schema = WOQLSchema()


class Abstract(DocumentTemplate):
    """This is abstract class"""

    _schema = WOQLSchema()
    _abstract = []
    name: str


class ChildAbs(Abstract):
    """Child of abstract class, should not be abstract by default"""

    # _abstract = False


class TypeCheck(DocumentTemplate):
    """For checking instance types"""

    _schema = WOQLSchema()
    name: str
    age: int


class CheckCyclingGrandPa(DocumentTemplate):
    """GrandPa For checking cycling"""

    _schema = cycling_schema
    child: "CheckCyclingPaPa"


class CheckCyclingPaPa(CheckCyclingGrandPa):
    """GrandPa For checking cycling"""

    papa: CheckCyclingGrandPa


class CheckCycling(CheckCyclingPaPa):
    """GrandPa For checking cycling"""

    papa: CheckCyclingPaPa
    grand_pa: CheckCyclingGrandPa
    me: "CheckCycling"  # not allow


#
# class Coordinate(DocumentTemplate):
#     """Coordinate of location.
#
#     Coordinate to identify the location of a place on earth, it could be found from Google map.
#
#     Attributes
#     ----------
#     x : float
#         The X coordinate.
#     y : float
#         The Y coordinate.
#     """
#
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
#     _schema = my_schema
#     street: str
#     country: Country
#
#
# class Person(DocumentTemplate):
#     _schema = my_schema
#     name: str
#     age: int
#     friend_of: Set["Person"]
#
#
# class Employee(Person):
#     _schema = my_schema
#     address_of: Address
#     contact_number: str
#     managed_by: "Employee"
#
#
# class Team(EnumTemplate):
#     _schema = my_schema
#     IT = ()
#     Marketing = ()
#


def test_schema_construct(test_schema):
    my_schema = test_schema
    assert set(map(lambda x: x.__name__, my_schema.all_obj())) == {
        "Employee",
        "Person",
        "Address",
        "Team",
        "Country",
        "Coordinate",
        "Role",
    }
    # assert my_schema.all_prop() == {AddressOf, Title, PostCode}
    # assert Employee.properties == {AddressOf, Title}


def test_schema_copy(test_schema):
    my_schema = test_schema
    copy_schema = my_schema.copy()
    assert copy_schema.all_obj() == my_schema.all_obj()
    # assert copy_schema.all_prop() == {AddressOf, Title, PostCode}


def test_abstract_class():
    with pytest.raises(TypeError):
        Abstract()
    assert Abstract._abstract == []
    assert Abstract._to_dict().get("@abstract") == []


def test_abstract_class_child():
    it_ok_to_create = ChildAbs(name="It's ok")
    assert it_ok_to_create.name == "It's ok"
    assert ChildAbs._abstract is None
    assert "@abstract" not in ChildAbs._to_dict()


def test_type_check():
    test_obj = TypeCheck()
    with pytest.raises(TypeError):
        test_obj.name = 123
    with pytest.raises(TypeError):
        test_obj.age = "not a number"


def test_inheritance(test_schema):
    my_schema = test_schema
    Person = my_schema.object.get("Person")
    Employee = my_schema.object.get("Employee")
    for item in Person._annotations:
        if item not in Employee._annotations:
            raise AssertionError(f"{item} not inherted")


def test_cycling():
    # no self embedding if subdocument
    _check_cycling(CheckCycling)
    CheckCycling._subdocument = []
    with pytest.raises(RecursionError):
        _check_cycling(CheckCycling)
    CheckCyclingGrandPa
    # no cycling embedding if subdocument
    _check_cycling(CheckCyclingPaPa)
    CheckCyclingPaPa._subdocument = []
    with pytest.raises(RecursionError):
        _check_cycling(CheckCyclingPaPa)
    with pytest.raises(RecursionError):
        cycling_schema.to_dict()


def test_idgen(test_schema):
    my_schema = test_schema
    Country = my_schema.object.get("Country")
    uk = Country()
    assert uk._id[: len("Country/")] == "Country/"


def test_context(test_schema):
    my_schema = test_schema
    assert my_schema.to_dict()[0].get("@type") == "@context"


def test_import_objects(test_schema):
    my_schema = test_schema
    Person = my_schema.object.get("Person")
    cheuk = Person(
        name="Cheuk",
        age=21,
        friend_of={
            Person(),
        },
    )
    cheuk_dict = cheuk._obj_to_dict()
    del cheuk
    return_objs = my_schema.import_objects([cheuk_dict])
    assert return_objs[0]._obj_to_dict() == cheuk_dict


def test_get_instances(test_schema):
    my_schema = test_schema
    Person = my_schema.object.get("Person")
    _ = Person(
        name="Cheuk",
        age=21,
        friend_of={
            Person(),
        },
    )
    assert len(list(Person.get_instances())) == 2


def test_add_enum_class():
    new_schema = WOQLSchema()
    my_enum = new_schema.add_enum_class("MyEnum", ["item1", "item2"])
    assert "item1" in my_enum.__members__
    assert "item2" in my_enum.__members__
    assert my_enum.__name__ == "MyEnum"
    assert "MyEnum" in new_schema.object


# def test_schema_delete():
#     other_schema.delete_property(Title)
#     assert other_schema.all_obj() == {Employee, Address, Team}
#     assert other_schema.all_prop() == {AddressOf, PostCode, Country}
