import datetime as dt
import unittest.mock as mock
from typing import Set
from unittest.mock import ANY

import pytest
import requests

from terminusdb_client.client import Client
from terminusdb_client.schema.schema import (
    DocumentTemplate,
    Schema,
    _check_cycling,
)

from ..__version__ import __version__
from .conftest import mocked_request_success

# my_schema = Schema()
cycling_schema = Schema()


class Abstract(DocumentTemplate):
    """This is abstract class"""

    _schema = Schema()
    _abstract = []
    name: str


class ChildAbs(Abstract):
    """Child of abstract class, should not be abstract by default"""

    # _abstract = False


class TypeCheck(DocumentTemplate):
    """For checking instance types"""

    _schema = Schema()
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


class CheckEmptySet(DocumentTemplate):

    some_set: Set[str]


class CheckDatetime(DocumentTemplate):

    datetime: dt.datetime
    duration: dt.timedelta


def test_schema_construct(test_schema):
    my_schema = test_schema
    assert {x.__name__ for x in my_schema.all_obj()} == {
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


# def test_idgen(test_schema):
#     my_schema = test_schema
#     Country = my_schema.object.get("Country")
#     uk = Country()
#     assert uk._id[: len("Country/")] == "Country/"


def test_context(test_schema):
    my_schema = test_schema
    assert my_schema.to_dict()[0].get("@type") == "@context"


@pytest.mark.skip(reason="need to be done with backend")
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
    (cheuk_dict, _) = cheuk._obj_to_dict()
    del cheuk
    return_objs = my_schema.import_objects([cheuk_dict])
    assert (return_objs[0]._obj_to_dict())[0] == cheuk_dict


def test_get_instances(test_schema):
    my_schema = test_schema
    Person = my_schema.object.get("Person")
    _ = Person(
        name="Cheuk",
        age=21,
        friend_of={Person()},
    )
    assert len(list(Person.get_instances())) == 2


def test_embedded_object(test_schema):
    my_schema = test_schema
    Person = my_schema.object.get("Person")
    Country = my_schema.object.get("Country")
    Address = my_schema.object.get("Address")
    gavin = Person(
        name="Gavin",
        age=43,
        address=Address(
            street="test",
            country=Country(name="Republic of Ireland"),
        ),
        friend_of={Person(
            name="Katy",
            age=51
        )}
    )
    client = Client("http://127.0.0.1:6366")
    result = client._convert_document(gavin, 'instance')
    # Finds the internal object and splays it out properly
    assert (len(result) == 2)


def test_id_and_capture(test_schema):
    my_schema = test_schema
    Person = my_schema.object.get("Person")
    Country = my_schema.object.get("Country")
    Address = my_schema.object.get("Address")

    ireland = Country()
    ireland.name = "Republic of Ireland"
    ireland.perimeter = []
    with pytest.raises(ValueError) as error:
        ireland._id = "ireland"
        assert (
            str(error.value)
            == "Customized id is not allowed. Country is a subdocument or has set id key scheme."
        )

    home = Address()
    home.street = "123 Abc Street"
    home.country = ireland
    home.postal_code = "A12 345"
    with pytest.raises(ValueError) as error:
        home._id = "home_sweet_home"
        assert (
            str(error.value)
            == "Customized id is not allowed. Address is a subdocument or has set id key scheme."
        )

    cheuk_with_id = Person(
        _id="cheuk",
        name="Cheuk",
        age=21,
    )
    cheuk_with_id.friend_of = {
        cheuk_with_id,
    }
    assert (cheuk_with_id._obj_to_dict())[0] == {
        "@type": "Person",
        "@id": "Person/cheuk",
        "name": "Cheuk",
        "age": 21,
        "friend_of": [{"@id": "Person/cheuk", "@type": "@id"}],
    }
    cheuk_no_id = Person(
        name="Cheuk",
        age=21,
    )
    cheuk_no_id.friend_of = {
        cheuk_no_id,
    }
    assert (cheuk_no_id._obj_to_dict())[0] == {
        "@type": "Person",
        "@capture": cheuk_no_id._capture,
        "name": "Cheuk",
        "age": 21,
        "friend_of": [{"@ref": cheuk_no_id._capture}],
    }


def test_add_enum_class():
    new_schema = Schema()
    my_enum = new_schema.add_enum_class("MyEnum", ["item1", "item2"])
    assert "item1" in my_enum.__members__
    assert "item2" in my_enum.__members__
    assert my_enum.__name__ == "MyEnum"
    assert "MyEnum" in new_schema.object


def test_empty_set():
    test_obj = CheckEmptySet()
    test_obj._obj_to_dict()[0]


def test_datetime():
    datetime_obj = dt.datetime(2019, 5, 18, 15, 17, 8, 132263)
    delta = dt.timedelta(
        days=50,
        seconds=27,
        microseconds=10,
        milliseconds=29000,
        minutes=5,
        hours=8,
        weeks=2,
    )
    test_obj = CheckDatetime(_id="test_obj", datetime=datetime_obj, duration=delta)
    test_dict = test_obj._obj_to_dict()[0]
    assert test_dict["datetime"] == "2019-05-18T15:17:08.132263"
    assert test_dict["duration"] == "PT5558756.00001S"
    datetime_schema = Schema()
    datetime_schema.add_obj("CheckDatetime", CheckDatetime)
    new_obj = datetime_schema.import_objects(test_dict)
    assert new_obj.datetime == datetime_obj
    assert new_obj.duration == delta


@mock.patch("requests.head", side_effect=mocked_request_success)
@mock.patch("requests.get", side_effect=mocked_request_success)
@mock.patch("requests.post", side_effect=mocked_request_success)
@mock.patch("requests.put", side_effect=mocked_request_success)
def test_compress_data(patched, patched2, patched3, patched4):
    datetime_obj = dt.datetime(2019, 5, 18, 15, 17, 8, 132263)
    delta = dt.timedelta(
        days=50,
        seconds=27,
        microseconds=10,
        milliseconds=29000,
        minutes=5,
        hours=8,
        weeks=2,
    )
    test_obj = [CheckDatetime(datetime=datetime_obj, duration=delta) for _ in range(10)]
    client = Client("http://127.0.0.1:6366")
    client.connect(db="test_compress_data")
    client.insert_document(test_obj, compress=0)
    requests.post.assert_called_once_with(
        "http://127.0.0.1:6366/api/document/admin/test_compress_data/local/branch/main",
        auth=("admin", "root"),
        headers={
            "user-agent": f"terminusdb-client-python/{__version__}",
            "Content-Encoding": "gzip",
            "Content-Type": "application/json",
        },
        params={
            "author": "admin",
            "message": f"Commit via python client {__version__}",
            "graph_type": "instance",
            "full_replace": "false",
            "raw_json": "false",
        },
        data=ANY,
    )
    requests.post.reset_mock()
    client.insert_document(test_obj, compress="never")
    requests.post.assert_called_once_with(
        "http://127.0.0.1:6366/api/document/admin/test_compress_data/local/branch/main",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        params={
            "author": "admin",
            "message": f"Commit via python client {__version__}",
            "graph_type": "instance",
            "full_replace": "false",
            "raw_json": "false",
        },
        json=ANY,
    )
    client.replace_document(test_obj, compress=0)
    requests.put.assert_called_once_with(
        "http://127.0.0.1:6366/api/document/admin/test_compress_data/local/branch/main",
        auth=("admin", "root"),
        headers={
            "user-agent": f"terminusdb-client-python/{__version__}",
            "Content-Encoding": "gzip",
            "Content-Type": "application/json",
        },
        params={
            "author": "admin",
            "message": f"Commit via python client {__version__}",
            "graph_type": "instance",
            "create": "false",
            "raw_json": "false",
        },
        data=ANY,
    )
    requests.put.reset_mock()
    client.replace_document(test_obj, compress="never")
    requests.put.assert_called_once_with(
        "http://127.0.0.1:6366/api/document/admin/test_compress_data/local/branch/main",
        auth=("admin", "root"),
        headers={"user-agent": f"terminusdb-client-python/{__version__}"},
        params={
            "author": "admin",
            "message": f"Commit via python client {__version__}",
            "graph_type": "instance",
            "create": "false",
            "raw_json": "false",
        },
        json=ANY,
    )


def test_from_json_schema():
    test_json_schema = {
        "type": "object",
        "properties": {
            "first_name": {"type": "string"},
            "last_name": {"type": "string"},
            "birthday": {"type": "string", "format": "date"},
            "address": {
                "type": "object",
                "properties": {
                    "street_address": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "country": {"type": "string"},
                },
            },
        },
    }

    schema = Schema()
    test_result = schema.from_json_schema("TestJSON", test_json_schema, pipe=True)
    assert test_result == {
        "@id": "TestJSON",
        "@type": "Class",
        "first_name": "xsd:string",
        "last_name": "xsd:string",
        "birthday": "xsd:string",
        "address": {
            "@id": "address",
            "@type": "Class",
            "@subdocument": [],
            "street_address": "xsd:string",
            "city": "xsd:string",
            "state": "xsd:string",
            "country": "xsd:string",
        },
    }


# def test_schema_delete():
#     other_schema.delete_property(Title)
#     assert other_schema.all_obj() == {Employee, Address, Team}
#     assert other_schema.all_prop() == {AddressOf, PostCode, Country}
