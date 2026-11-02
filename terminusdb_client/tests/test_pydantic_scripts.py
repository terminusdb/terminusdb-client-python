"""Tests for pydantic codegen (_create_pydantic_script), Schema.diff and the
tdbpy check/sync/commit wiring."""

import types
from unittest.mock import Mock

import pytest

pytest.importorskip("pydantic", reason="requires terminusdb[pydantic]")

from terminusdb_client.schema.pydantic import (
    PydanticSchema,
    TerminusModel,
    TerminusUnion,
)
from terminusdb_client.schema.schema import LexicalKey
from terminusdb_client.scripts.scripts import _create_pydantic_script

SCHEMA_DOCS = [
    {
        "@type": "@context",
        "@schema": "http://s#",
        "@base": "http://i/",
        "@documentation": {
            "@title": "T",
            "@description": "D",
            "@authors": ["A U Thor"],
        },
    },
    {
        "@type": "Class",
        "@id": "Person",
        "@key": {"@type": "Lexical", "@fields": ["name"]},
        "@documentation": {"@comment": "A person.",
                           "@properties": {"name": "The name."}},
        "name": "xsd:string",
        "age": {"@type": "Optional", "@class": "xsd:integer"},
        "friend_of": {"@type": "Set", "@class": "Person"},
    },
    {
        "@type": "Class",
        "@id": "Employee",
        "@inherits": "Person",
        "managed_by": "Employee",
    },
    {
        "@type": "Class",
        "@id": "Address",
        "@subdocument": [],
        "street": "xsd:string",
    },
    {"@type": "Enum", "@id": "Team", "@value": ["IT", "Information Technology"]},
    {
        "@type": "TaggedUnion",
        "@id": "BinaryTree",
        "leaf": "sys:Unit",
        "node": "Node",
    },
    {
        "@type": "Class",
        "@id": "Node",
        "value": "xsd:integer",
    },
    {
        "@type": "Class",
        "@id": "Shared",
        "@shared": [],
        "@unfoldable": [],
        "name": "xsd:string",
    },
    {
        "@type": "Class",
        "@id": "Holder",
        "maybe": {
            "@type": "Optional",
            "@class": "Shared",
            "@unfold": True,
        },
        "grid": {"@type": "Array", "@class": "xsd:decimal", "@dimensions": 2},
        "three": {"@type": "Set", "@class": "Person", "@cardinality": 3},
    },
    {"@type": "Foreign", "@id": "Ext"},
]


def _exec_script(source):
    mod = types.ModuleType("generated_schema")
    exec(compile(source, "schema.py", "exec"), mod.__dict__)
    return mod


def test_codegen_emits_pydantic_classes():
    source = _create_pydantic_script(list(SCHEMA_DOCS))
    mod = _exec_script(source)
    Person = mod.Person
    assert issubclass(Person, TerminusModel)
    assert Person._key.__class__ is LexicalKey
    assert issubclass(mod.Employee, mod.Person)
    assert issubclass(mod.BinaryTree, TerminusUnion)
    assert issubclass(mod.Team, str) and issubclass(mod.Team, __import__("enum").Enum)
    assert mod.Ext._foreign is True
    assert mod.Shared._shared is True
    assert mod.Shared._unfoldable is True


def test_codegen_reemits_identical_docs():
    source = _create_pydantic_script(list(SCHEMA_DOCS))
    mod = _exec_script(source)
    emitted = {}
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and issubclass(obj, TerminusModel) \
                and name not in ("TerminusModel", "TerminusUnion"):
            emitted[name] = obj._to_dict()
        elif isinstance(obj, type) and issubclass(obj, __import__("enum").Enum) \
                and name != "Enum":
            from terminusdb_client.schema.pydantic import _enum_to_dict

            emitted[name] = _enum_to_dict(obj)
    for doc in SCHEMA_DOCS:
        doc_id = doc.get("@id")
        if doc_id is None:
            continue
        assert doc_id in emitted, f"{doc_id} missing from generated module"
        got = emitted[doc_id]
        for key, value in doc.items():
            if key == "@inherits" and isinstance(value, str):
                value = [value]
            assert got.get(key) == value, f"{doc_id}.{key}: {got.get(key)!r} != {value!r}"


def test_codegen_field_doc():
    source = _create_pydantic_script(list(SCHEMA_DOCS))
    mod = _exec_script(source)
    assert "A person." in mod.Person.__doc__


# --- Schema.diff / tdbpy check -------------------------------------------------


def _normalised(docs):
    return docs


def test_diff_in_sync():
    schema = PydanticSchema()
    for cls_doc in SCHEMA_DOCS:
        if cls_doc.get("@type") == "@context":
            schema.title = cls_doc["@documentation"]["@title"]
            schema.description = cls_doc["@documentation"]["@description"]
            schema.authors = cls_doc["@documentation"]["@authors"]
            schema.schema_ref = cls_doc["@schema"]
            schema.base_ref = cls_doc["@base"]

    class Person(TerminusModel):
        _schema = schema
        _key = LexicalKey("name")
        name: str

    client = Mock()
    local = schema.to_dict()
    client.get_all_documents.return_value = local
    assert schema.diff(client) == []


def test_diff_reports_changes():
    schema = PydanticSchema()

    class Person(TerminusModel):
        _schema = schema
        _key = LexicalKey("name")
        name: str
        age: int

    schema.schema_ref = "http://s#"
    schema.base_ref = "http://i/"
    server_docs = [
        {"@type": "@context", "@schema": "http://s#", "@base": "http://i/"},
        {"@type": "Class", "@id": "Person",
         "@key": {"@type": "Lexical", "@fields": ["name"]},
         "name": "xsd:string"},
        {"@type": "Class", "@id": "Ghost", "x": "xsd:string"},
    ]
    client = Mock()
    client.get_all_documents.return_value = server_docs
    diff = schema.diff(client)
    out = "\n".join(diff)
    assert any("missing" in line.lower() or "-" in line for line in diff)
    # Ghost is on server only, age locally only
    assert "Ghost" in out
    assert "age" in out


def test_diff_ignore_docs():
    schema = PydanticSchema()
    schema.schema_ref = "http://s#"
    schema.base_ref = "http://i/"

    class Person(TerminusModel):
        """Different comment."""
        _schema = schema
        name: str

    client = Mock()
    client.get_all_documents.return_value = [
        {"@type": "@context", "@schema": "http://s#", "@base": "http://i/"},
        {"@type": "Class", "@id": "Person",
         "@documentation": {"@comment": "Old comment", "@properties": {}},
         "name": "xsd:string"},
    ]
    assert schema.diff(client) != []
    assert schema.diff(client, ignore_docs=True) == []
