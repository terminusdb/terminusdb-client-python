"""Tests for TerminusModel instance serialisation (to_document/_obj_to_dict)
and reconstruction (from_document/stubs)."""

import datetime as dt
from enum import Enum
from typing import List, Optional, Set

import pytest

from terminusdb_client.schema.pydantic import PydanticSchema, TerminusModel
from terminusdb_client.schema.schema import LexicalKey


class Coord(TerminusModel):
    _subdocument = []
    x: float
    y: float


class Nation(TerminusModel):
    _key = LexicalKey("name")
    name: str
    perimeter: List[Coord]


class Colour(str, Enum):
    red = "red"
    blue = "blue"


class Widget(TerminusModel):
    name: str
    shade: Optional[Colour]
    parts: Set["Widget"]


class CheckDt(TerminusModel):
    when: dt.datetime
    span: dt.timedelta


class Address(TerminusModel):
    _subdocument = []
    street: str
    city: str


class Human(TerminusModel):
    name: str
    home: Optional[Address] = None
    best_friend: Optional["Human"] = None


# --- to_document / _obj_to_dict ---------------------------------------------


def test_basic_serialise():
    w = Widget(name="bolt", shade=Colour.red, parts=set())
    doc, refs = w._obj_to_dict()
    assert doc["@type"] == "Widget"
    assert doc["name"] == "bolt"
    assert doc["shade"] == "red"  # member.value, not "Colour.red"
    assert doc["parts"] == []
    assert "@capture" in doc  # no id yet -> capture minted
    assert refs == {}


def test_capture_and_ref_graph():
    """Un-ided linked objects emit @capture/@ref and land in references."""
    katy = Human(name="katy")
    bob = Human(name="bob", best_friend=katy)
    doc, refs = bob._obj_to_dict()
    assert doc["best_friend"] == {"@ref": katy._capture}
    assert katy._capture in refs
    # bob has no id either
    assert "@capture" in doc


def test_id_link_form():
    """Keyed objects carry no client-side @id — the engine mints it."""
    ireland = Nation(name="Republic of Ireland", perimeter=[])
    doc, _ = ireland._obj_to_dict()
    assert "@id" not in doc
    assert doc["@capture"] == ireland._capture
    assert doc["perimeter"] == []


def test_subdocument_embeds():
    h = Human(name="bob", home=Address(street="s", city="c"))
    doc, _ = h._obj_to_dict()
    assert doc["home"] == {
        "@type": "Address",
        "street": "s",
        "city": "c",
    }


def test_custom_id_and_backend_id():
    w = Widget(name="w", shade=None, parts=set(), _id="custom")
    doc, _ = w._obj_to_dict()
    assert doc["@id"] == "Widget/custom"
    loaded = Widget(name="w", shade=None, parts=set(), _backend_id="Widget/db1")
    doc2, _ = loaded._obj_to_dict()
    assert doc2["@id"] == "Widget/db1"


def test_custom_id_rejected_on_key_scheme():
    with pytest.raises(ValueError, match="Customized id"):
        Nation(name="x", perimeter=[], _id="bad")


def test_datetime_serialise():
    obj = CheckDt(
        when=dt.datetime(2019, 5, 18, 15, 17, 8, 132263),
        span=dt.timedelta(days=64, hours=8, minutes=5, seconds=56.00001),
    )
    doc, _ = obj._obj_to_dict()
    assert doc["when"] == "2019-05-18T15:17:08.132263"
    assert doc["span"].startswith("PT")


def test_to_document_alias():
    w = Widget(name="w", shade=None, parts=set())
    assert w.to_document() == w._obj_to_dict()


# --- stubs / from_document ---------------------------------------------------


def test_stub_from_id_string():
    schema = PydanticSchema()
    schema.add_obj("Human", Human)
    schema.add_obj("Address", Address)
    doc = {"@type": "Human", "@id": "Human/bob", "name": "bob",
           "best_friend": "Human/katy"}
    obj = schema.parse_document(doc)
    assert obj._backend_id == "Human/bob"
    assert obj.name == "bob"
    friend = obj.best_friend
    assert friend._backend_id == "Human/katy"
    with pytest.raises(AttributeError):
        friend.name


def test_stub_from_id_dict():
    schema = PydanticSchema()
    schema.add_obj("Human", Human)
    schema.add_obj("Address", Address)
    doc = {"@type": "Human", "@id": "Human/bob", "name": "bob",
           "best_friend": {"@type": "@id", "@id": "Human/katy"}}
    obj = schema.parse_document(doc)
    assert obj.best_friend._backend_id == "Human/katy"


def test_unfolded_subdocument_parses():
    schema = PydanticSchema()
    schema.add_obj("Human", Human)
    schema.add_obj("Address", Address)
    doc = {"@type": "Human", "@id": "Human/bob", "name": "bob",
           "home": {"@type": "Address", "street": "s", "city": "c"}}
    obj = schema.parse_document(doc)
    assert obj.home.street == "s"
    assert obj.home.city == "c"


def test_unfolded_document_parses_to_model():
    schema = PydanticSchema()
    schema.add_obj("Human", Human)
    schema.add_obj("Address", Address)
    doc = {"@type": "Human", "@id": "Human/bob", "name": "bob",
           "best_friend": {"@type": "Human", "@id": "Human/katy",
                           "name": "katy"}}
    obj = schema.parse_document(doc)
    assert obj.best_friend.name == "katy"
    assert obj.best_friend._backend_id == "Human/katy"


def test_round_trip():
    schema = PydanticSchema()
    schema.add_obj("Nation", Nation)
    schema.add_obj("Coord", Coord)
    n = Nation(name="Ireland", perimeter=[Coord(x=1.0, y=2.0)])
    doc, _ = n._obj_to_dict()
    back = schema.parse_document(doc)
    assert back.name == "Ireland"
    assert back.perimeter[0].x == 1.0
    assert back._backend_id == n._id


def test_scalar_into_set_wraps():
    schema = PydanticSchema()
    schema.add_obj("Widget", Widget)
    schema.add_obj("Colour", Colour)
    doc = {"@type": "Widget", "name": "w", "shade": "red",
           "parts": "Widget/other"}
    obj = schema.parse_document(doc)
    assert isinstance(obj.parts, set)
    assert obj.parts.pop()._backend_id == "Widget/other"
    assert obj.shade is Colour.red


def test_import_objects_list():
    schema = PydanticSchema()
    schema.add_obj("Widget", Widget)
    docs = [{"@type": "Widget", "name": "a", "shade": None, "parts": []},
            {"@type": "Widget", "name": "b", "shade": None, "parts": []}]
    out = schema.import_objects(docs)
    assert [o.name for o in out] == ["a", "b"]


def test_unknown_type_raises():
    schema = PydanticSchema()
    with pytest.raises(ValueError, match="not in current schema"):
        schema.parse_document({"@type": "Nope", "@id": "x"})
