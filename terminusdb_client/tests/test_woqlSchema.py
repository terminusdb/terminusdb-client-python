from typing import List, Set

import pytest

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    WOQLSchema,
    _check_cycling,
)

my_schema = WOQLSchema()
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


class Coordinate(DocumentTemplate):
    """Coordinate of location.

    Coordinate to identify the location of a place on earth, it could be found from Google map.

    Attributes
    ----------
    x : float
        The X coordinate.
    y : float
        The Y coordinate.
    """

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


class Person(DocumentTemplate):
    _schema = my_schema
    name: str
    age: int
    friend_of: Set["Person"]


class Employee(Person):
    _schema = my_schema
    address_of: Address
    contact_number: str
    managed_by: "Employee"


class Team(EnumTemplate):
    _schema = my_schema
    IT = ()
    Marketing = ()


def test_schema_construct():
    assert my_schema.all_obj() == {Employee, Person, Address, Team, Country, Coordinate}
    # assert my_schema.all_prop() == {AddressOf, Title, PostCode}
    # assert Employee.properties == {AddressOf, Title}


def test_schema_copy():
    copy_schema = my_schema.copy()
    assert copy_schema.all_obj() == {
        Employee,
        Person,
        Address,
        Team,
        Country,
        Coordinate,
    }
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


def test_inheritance():
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


def test_idgen():
    cheuk = Country()
    assert cheuk._id[: len("Country/")] == "Country/"


def test_context():
    assert my_schema.to_dict()[0].get("@type") == "@context"


# def test_schema_delete():
#     other_schema.delete_property(Title)
#     assert other_schema.all_obj() == {Employee, Address, Team}
#     assert other_schema.all_prop() == {AddressOf, PostCode, Country}
