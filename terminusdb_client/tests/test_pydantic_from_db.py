"""Tests for PydanticSchema.from_db — rebuilding models from schema docs."""

from unittest.mock import Mock
from typing import Optional

from terminusdb_client.schema.pydantic import (
    PydanticSchema,
    TerminusModel,
    TerminusUnion,
)
from terminusdb_client.schema.schema import LexicalKey, RandomKey, ValueHashKey

SCHEMA_DOCS = [
    {"@type": "@context", "@schema": "http://s#", "@base": "http://i/"},
    {
        "@type": "Class",
        "@id": "Person",
        "@key": {"@type": "Lexical", "@fields": ["name"]},
        "@documentation": {
            "@comment": "A person.",
            "@properties": {"name": "The name."},
        },
        "name": "xsd:string",
        "age": {"@type": "Optional", "@class": "xsd:integer"},
        "friend_of": {"@type": "Set", "@class": "Person"},
    },
    {
        "@type": "Class",
        "@id": "Employee",
        "@inherits": "Person",
        "@key": {"@type": "Lexical", "@fields": ["name"]},
        "managed_by": "Employee",
    },
    {
        "@type": "Class",
        "@id": "Address",
        "@subdocument": [],
        "@key": {"@type": "Random"},
        "street": "xsd:string",
    },
    {"@type": "Enum", "@id": "Team", "@value": ["IT", "Information Technology"]},
    {
        "@type": "TaggedUnion",
        "@id": "Contact",
        "local_number": "xsd:integer",
        "international": "xsd:string",
    },
    {
        "@type": "Class",
        "@id": "Unfoldable",
        "@unfoldable": [],
        "name": "xsd:string",
    },
    {
        "@type": "Class",
        "@id": "SharedDoc",
        "@shared": [],
        "@key": {"@type": "ValueHash"},
        "name": "xsd:string",
    },
    {"@type": "Foreign", "@id": "ExternalThing"},
    {
        "@type": "Class",
        "@id": "Meta",
        "@metadata": {"order_by": ["name"]},
        "name": "xsd:string",
    },
    {
        "@type": "Class",
        "@id": "Holder",
        "maybe": {
            "@type": "Optional",
            "@class": "Unfoldable",
            "@unfold": True,
        },
        "always": {"@class": "Unfoldable", "@unfold": True},
        "grid": {"@type": "Array", "@class": "xsd:decimal", "@dimensions": 2},
        "three": {
            "@type": "Set",
            "@class": "Person",
            "@cardinality": 3,
        },
        "unit_field": "sys:Unit",
    },
]


def _client(docs=SCHEMA_DOCS):
    client = Mock()
    client.get_all_documents.return_value = docs
    return client


def test_from_db_builds_models():
    schema = PydanticSchema().from_db(_client())
    for name in ["Person", "Employee", "Address", "Contact", "Holder"]:
        assert name in schema.object
    Person = schema.object["Person"]
    assert issubclass(Person, TerminusModel)
    assert Person._key.__class__ is LexicalKey
    assert Person._key._keys == ["name"]
    Employee = schema.object["Employee"]
    assert issubclass(Employee, Person)
    Address = schema.object["Address"]
    assert hasattr(Address, "_subdocument")
    Team = schema.object["Team"]
    assert list(Team.__members__) == ["it", "information_technology"]
    assert issubclass(schema.object["Contact"], TerminusUnion)


def test_from_db_annotations_resolve():
    schema = PydanticSchema().from_db(_client())
    Person = schema.object["Person"]
    from typing import Set as TSet

    assert Person.model_fields["friend_of"].annotation == TSet[Person]
    assert Person.model_fields["age"].annotation == Optional[int]
    Employee = schema.object["Employee"]
    assert Employee.model_fields["managed_by"].annotation is Employee


def test_from_db_reemits_identical_docs():
    schema = PydanticSchema().from_db(_client())
    emitted = {d["@id"]: d for d in schema.to_dict() if "@id" in d}
    for doc in SCHEMA_DOCS:
        doc_id = doc.get("@id")
        if doc_id is None:
            continue
        got = emitted[doc_id]
        for key, value in doc.items():
            if key == "@inherits" and isinstance(value, str):
                value = [value]
            assert got.get(key) == value, f"{doc_id}.{key}: {got.get(key)!r} != {value!r}"


def test_from_db_docstring():
    schema = PydanticSchema().from_db(_client())
    assert "A person." in schema.object["Person"].__doc__


def test_from_db_markers():
    schema = PydanticSchema().from_db(_client())
    assert schema.object["Unfoldable"]._unfoldable is True
    assert schema.object["SharedDoc"]._shared is True
    assert schema.object["SharedDoc"]._key.__class__ is ValueHashKey
    assert schema.object["ExternalThing"]._foreign is True
    assert schema.object["Meta"]._metadata == {"order_by": ["name"]}


def test_from_db_field_markers():
    schema = PydanticSchema().from_db(_client())
    Holder = schema.object["Holder"]
    doc = Holder._to_dict()
    assert doc["maybe"] == {
        "@type": "Optional",
        "@class": "Unfoldable",
        "@unfold": True,
    }
    assert doc["always"] == {"@class": "Unfoldable", "@unfold": True}
    assert doc["grid"] == {
        "@type": "Array",
        "@class": "xsd:decimal",
        "@dimensions": 2,
    }
    assert doc["three"] == {"@type": "Set", "@class": "Person", "@cardinality": 3}
    assert doc["unit_field"] == "sys:Unit"


def test_from_db_select():
    schema = PydanticSchema().from_db(_client(), select=["Address"])
    assert "Address" in schema.object
    assert "Person" not in schema.object


def test_from_db_context():
    schema = PydanticSchema().from_db(_client())
    assert schema.context["@schema"] == "http://s#"
    assert schema.context["@base"] == "http://i/"


def test_from_db_random_key_default():
    schema = PydanticSchema().from_db(_client())
    # Person has Lexical; Address Random (explicit), Holder no @key
    assert schema.object["Address"]._key.__class__ is RandomKey
    assert schema.object["Holder"]._key.__class__ is RandomKey
