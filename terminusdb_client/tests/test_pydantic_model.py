"""Tests for TerminusModel declaration -> schema document emission.

Golden parity: pydantic twins of the conftest DocumentTemplate classes must
emit byte-identical class documents.
"""

import datetime as dt
from enum import Enum
from typing import Annotated, List, Optional, Set, Union

import pytest

from terminusdb_client.schema.pydantic import (
    Array,
    TerminusModel,
    TerminusUnion,
    Unfold,
)
from terminusdb_client.schema.schema import (
    LexicalKey,
    Schema,
    UuidV7Key,
    ValueHashKey,
)
from terminusdb_client.woql_type import gYear

from .conftest import (
    Address,
    Contact,
    Coordinate,
    Country,
    Employee,
    Person,
)

pydantic_schema = Schema()


class PCoordinate(TerminusModel):
    _schema = pydantic_schema
    x: float
    y: float


class PCountry(TerminusModel):
    _schema = pydantic_schema
    _key = LexicalKey(["name"])
    name: str
    perimeter: List[PCoordinate]


class PAddress(TerminusModel):
    """This is address"""

    _subdocument = []
    _schema = pydantic_schema
    street: str
    postal_code: str
    country: "PCountry"


class PPerson(TerminusModel):
    """This is a person

    Attributes
    ----------
    name : str
        Name of the person.
    age : int
        Age of the person.
    """

    _schema = pydantic_schema
    name: str
    age: int
    friend_of: Set["PPerson"]


class PEmployee(PPerson):
    _schema = pydantic_schema
    address_of: PAddress
    contact_number: Optional[str]
    managed_by: "PEmployee"
    member_of: "PTeam"
    permisstion: Set["PRole"]


class PTeam(str, Enum):
    IT = "Information Technology"
    Marketing = "Marketing"


class PRole(str, Enum):
    "Test Enum in a set"

    Admin = "Admin"
    Read = "Read"
    Write = "Write"


class PContact(TerminusUnion):
    _schema = pydantic_schema
    local_number: int
    international: str


def _expected(docs):
    return {d["@id"]: d for d in docs}


# --- declaration parity vs DocumentTemplate ---------------------------------


def _rename(value, mapping):
    if isinstance(value, str):
        return mapping.get(value, value)
    if isinstance(value, list):
        return [_rename(v, mapping) for v in value]
    if isinstance(value, dict):
        return {k: _rename(v, mapping) for k, v in value.items()}
    return value


def test_class_doc_parity():
    """Each pydantic twin emits the same class doc as its DocumentTemplate
    twin, modulo class names."""
    pairs = [
        (PCoordinate, Coordinate),
        (PCountry, Country),
        (PAddress, Address),
        (PPerson, Person),
        (PEmployee, Employee),
        (PContact, Contact),
    ]
    mapping = {p.__name__: t.__name__ for p, t in pairs}
    mapping.update({"PTeam": "Team", "PRole": "Role"})
    for pcls, tcls in pairs:
        got = _rename(pcls._to_dict(), mapping)
        assert got == tcls._to_dict()


def test_enum_parity():
    assert PTeam.__members__["IT"].value == "Information Technology"
    from terminusdb_client.schema.pydantic import _enum_to_dict

    assert _enum_to_dict(PTeam) == {
        "@type": "Enum",
        "@id": "PTeam",
        "@value": ["Information Technology", "Marketing"],
    }


def test_schema_registration():
    """_schema on a TerminusModel subclass registers like DocumentTemplate."""
    names = set(pydantic_schema.object)
    assert {
        "PCoordinate",
        "PCountry",
        "PAddress",
        "PPerson",
        "PEmployee",
        "PContact",
    } <= names


def test_no_globals_leak():
    """TerminusModel subclasses do not leak into module globals."""
    import terminusdb_client.schema.pydantic as pyd_mod

    assert "PPerson" not in vars(pyd_mod)


# --- annotation -> schema mapping -------------------------------------------


def test_scalar_mappings():
    import decimal

    class Scalars(TerminusModel):
        s: str
        i: int
        f: float
        b: bool
        d: dt.date
        t: dt.time
        ts: dt.datetime
        dur: dt.timedelta
        blob: dict
        dec: decimal.Decimal
        y: gYear

    doc = Scalars._to_dict()
    assert doc["s"] == "xsd:string"
    assert doc["i"] == "xsd:integer"
    assert doc["f"] == "xsd:double"
    assert doc["b"] == "xsd:boolean"
    assert doc["d"] == "xsd:date"
    assert doc["t"] == "xsd:time"
    assert doc["ts"] == "xsd:dateTime"
    assert doc["dur"] == "xsd:duration"
    assert doc["blob"] == "sys:JSON"
    assert doc["dec"] == "xsd:decimal"
    assert doc["y"] == "xsd:gYear"


def test_container_mappings():
    class Containers(TerminusModel):
        opt: Optional[int]
        union_none: Union[int, None]
        lst: List[str]
        st: Set[str]
        builtin_lst: "list[str]"
        builtin_opt: "str | None"
    doc = Containers._to_dict()
    assert doc["opt"] == {"@type": "Optional", "@class": "xsd:integer"}
    assert doc["union_none"] == {"@type": "Optional", "@class": "xsd:integer"}
    assert doc["lst"] == {"@type": "List", "@class": "xsd:string"}
    assert doc["st"] == {"@type": "Set", "@class": "xsd:string"}
    assert doc["builtin_lst"] == {"@type": "List", "@class": "xsd:string"}
    assert doc["builtin_opt"] == {"@type": "Optional", "@class": "xsd:string"}


def test_optional_cannot_wrap_collections():
    """The engine rejects Optional over Set/List — collections already
    permit zero elements."""
    class Bad(TerminusModel):
        opt_lst: Optional[List[int]]

    with pytest.raises(TypeError, match="Optional cannot wrap"):
        Bad._to_dict()

    class BadSet(TerminusModel):
        opt_st: Optional[Set[str]]

    with pytest.raises(TypeError, match="Optional cannot wrap"):
        BadSet._to_dict()


def test_unsupported_annotations_raise():
    class Bad(TerminusModel):
        u: Union[int, str]

    with pytest.raises(TypeError, match="TerminusUnion"):
        Bad._to_dict()

    class Bad2(TerminusModel):
        t: tuple

    with pytest.raises(TypeError):
        Bad2._to_dict()

    class Bad3(TerminusModel):
        f: frozenset

    with pytest.raises(TypeError):
        Bad3._to_dict()


def test_field_description_merges_into_documentation():
    from pydantic import Field

    class Documented(TerminusModel):
        """A documented class.

        Attributes
        ----------
        name : str
            Docstring says this.
        """
        name: str = Field(description="Field description wins")
        age: Optional[int] = Field(description="Only the field text")

    doc = Documented._to_dict()
    props = doc["@documentation"]["@properties"]
    assert props["name"] == "Field description wins"
    assert props["age"] == "Only the field text"
    assert doc["@documentation"]["@comment"] == "A documented class."


def test_default_does_not_make_optional():
    class WithDefault(TerminusModel):
        name: str = "x"

    assert WithDefault._to_dict()["name"] == "xsd:string"


# --- class attributes --------------------------------------------------------


def test_class_markers():
    class Marked(TerminusModel):
        _abstract = []
        _base = "marked/"
        _unfoldable = True
        _metadata = {"render_as": {"desc": "markdown"}}
        name: str

    doc = Marked._to_dict()
    assert doc["@abstract"] == []
    assert doc["@base"] == "marked/"
    assert doc["@unfoldable"] == []
    assert doc["@metadata"] == {"render_as": {"desc": "markdown"}}


def test_key_emissions():
    class ValueHashDoc(TerminusModel):
        _key = ValueHashKey()
        name: str

    assert ValueHashDoc._to_dict()["@key"] == {"@type": "ValueHash"}

    class UuidDoc(TerminusModel):
        _key = UuidV7Key()
        name: str

    assert UuidDoc._to_dict()["@key"] == {"@type": "UuidV7"}

    class RandomDoc(TerminusModel):
        name: str

    assert RandomDoc._to_dict()["@key"] == {"@type": "Random"}


def test_subdocument_key_rule():
    class Sub(TerminusModel):
        _subdocument = []
        name: str

    assert Sub._to_dict()["@key"] == {"@type": "Random"}

    class SubVH(TerminusModel):
        _subdocument = []
        _key = ValueHashKey()
        name: str

    assert SubVH._to_dict()["@key"] == {"@type": "ValueHash"}

    with pytest.raises(ValueError, match="subdocument"):

        class BadSub(TerminusModel):
            _subdocument = []
            _key = LexicalKey("name")
            name: str


def test_shared_mutual_exclusion():
    class Shared(TerminusModel):
        _shared = True
        name: str

    assert Shared._to_dict()["@shared"] == []

    with pytest.raises(ValueError, match="subdocument"):

        class BadShared(TerminusModel):
            _shared = True
            _subdocument = []
            name: str


def test_foreign_class():
    class ForeignPerson(TerminusModel):
        _foreign = True

    assert ForeignPerson._to_dict() == {
        "@type": "Foreign",
        "@id": "ForeignPerson",
    }

    with pytest.raises(ValueError, match="Foreign"):

        class BadForeign(TerminusModel):
            _foreign = True
            name: str


# --- unfold markers ----------------------------------------------------------


def test_unfold_property_marker():
    class Sub(TerminusModel):
        _subdocument = []
        name: str

    class Host(TerminusModel):
        req: Annotated[Sub, Unfold]
        opt: Annotated[Optional[Sub], Unfold]
        plain: Optional[Sub]

    doc = Host._to_dict()
    assert doc["req"] == {"@class": "Sub", "@unfold": True}
    assert doc["opt"] == {
        "@type": "Optional",
        "@class": "Sub",
        "@unfold": True,
    }
    assert doc["plain"] == {"@type": "Optional", "@class": "Sub"}


# --- array + cardinality -----------------------------------------------------


def test_array_marker():
    class Grid(TerminusModel):
        flat: Annotated[list[float], Array]
        grid2d: Annotated[list[list[float]], Array]

    doc = Grid._to_dict()
    assert doc["flat"] == {"@type": "Array", "@class": "xsd:double"}
    assert doc["grid2d"] == {
        "@type": "Array",
        "@class": "xsd:double",
        "@dimensions": 2,
    }


def test_set_cardinality():
    from pydantic import Field

    class Capped(TerminusModel):
        friends: Set[str] = Field(min_length=3, max_length=3)
        tags: Set[str] = Field(min_length=1)
        opts: Set[str] = Field(max_length=2, default_factory=set)
        plain: Set[str]

    doc = Capped._to_dict()
    assert doc["friends"] == {
        "@type": "Set",
        "@class": "xsd:string",
        "@cardinality": 3,
    }
    assert doc["tags"] == {
        "@type": "Set",
        "@class": "xsd:string",
        "@min_cardinality": 1,
    }
    assert doc["opts"] == {
        "@type": "Set",
        "@class": "xsd:string",
        "@max_cardinality": 2,
    }
    assert doc["plain"] == {"@type": "Set", "@class": "xsd:string"}


# --- tagged unions ------------------------------------------------------------


def test_union_sys_unit():
    class Node(TerminusModel):
        value: int

    class BinaryTree(TerminusUnion):
        leaf: None
        node: Node

    doc = BinaryTree._to_dict()
    assert doc["@type"] == "TaggedUnion"
    assert doc["leaf"] == "sys:Unit"
    assert doc["node"] == "Node"


def test_forward_refs():
    doc = PEmployee._to_dict()
    assert doc["managed_by"] == "PEmployee"
    assert doc["member_of"] == "PTeam"
    assert doc["permisstion"] == {"@type": "Set", "@class": "PRole"}
    assert doc["friend_of"] == {"@type": "Set", "@class": "PPerson"}
