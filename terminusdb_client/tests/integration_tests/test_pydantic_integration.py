import datetime as dt

import pytest

from terminusdb_client.client.Client import Client
from terminusdb_client.schema.pydantic import (
    PydanticSchema,
    TerminusEnum,
    TerminusModel,
    TerminusUnion,
    Unfold,
)
from terminusdb_client.schema.schema import (
    DocumentTemplate,
    LexicalKey,
    Schema,
    WOQLSchema,
)
from typing import Annotated, Optional, Set

test_user_agent = "terminusdb-client-python-tests"
_DB = "test_pydantic_integration"


class Genre(TerminusEnum):
    fiction = "fiction"
    non_fiction = "non_fiction"


class Address(TerminusModel):
    _subdocument = []
    street: str
    city: str


class Person(TerminusModel):
    _key = LexicalKey("name")
    name: str
    age: Optional[int] = None
    home: Optional[Address] = None
    friend_of: Set["Person"] = set()


class Employee(Person):
    staff_since: Optional[dt.date] = None
    contact: Optional["Either"] = None


class Either(TerminusUnion):
    local_number: Optional[int] = None
    international: Optional[str] = None


class Shelf(TerminusModel):
    _shared = True
    _unfoldable = True
    genre: Optional[Genre] = None
    label: str


class Library(TerminusModel):
    name: str
    shelves: Annotated[Set[Shelf], Unfold] = set()


@pytest.fixture(scope="module", autouse=True)
def cleanup_databases(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect()
    for db in (_DB, _DB + "_mixed"):
        try:
            client.delete_database(db)
        except Exception:
            pass
        client.create_database(db)
    yield
    for db in (_DB, _DB + "_mixed"):
        try:
            client.delete_database(db)
        except Exception:
            pass


def test_push_pydantic_schema_and_load_legacy(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(db=_DB)
    schema = PydanticSchema(
        title="Pydantic test schema",
        description="Schema pushed from pydantic models",
        authors=["integration test"],
    )
    for cls in (Genre, Address, Person, Employee, Either, Shelf, Library):
        schema.add_obj(cls.__name__, cls)
    schema.commit(client)

    # the same schema loads as legacy DocumentTemplate classes
    legacy = WOQLSchema()
    legacy.from_db(client)
    assert issubclass(legacy.object["Employee"], legacy.object["Person"])
    legacy_docs = legacy._all_existing_classes
    for cls in (Address, Person, Employee, Shelf, Library):
        doc = cls._to_dict()
        ref = legacy_docs[cls.__name__]
        for key, value in doc.items():
            if key == "@documentation":
                continue
            if key == "@inherits" and isinstance(ref.get(key), str):
                value = value[0]
            assert ref.get(key) == value, f"{cls.__name__}.{key}"

    # and reloads back as pydantic models
    pyd = PydanticSchema().from_db(client)
    assert issubclass(pyd.object["Employee"], pyd.object["Person"])
    assert pyd.object["Shelf"]._shared is True
    assert pyd.object["Shelf"]._unfoldable is True


def test_insert_and_parse_document(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(db=_DB)
    schema = PydanticSchema().from_db(client)

    jane = schema.object["Person"](
        name="Jane",
        age=36,
        home=schema.object["Address"](street="Main", city="Dublin"),
    )
    client.insert_document(jane)

    doc = client.get_document("Person/Jane")
    back = schema.parse_document(doc)
    assert back.name == "Jane"
    assert back.age == 36
    assert back.home.street == "Main"
    assert back._backend_id == "Person/Jane"

    # a folded link materialises as a stub
    john = schema.object["Person"](name="John", friend_of={back})
    client.insert_document(john)
    johndoc = client.get_document("Person/John")
    jback = schema.parse_document(johndoc)
    friend = next(iter(jback.friend_of))
    assert friend._backend_id == "Person/Jane"

    # replacing through a stub-free path keeps working
    back.age = 37
    client.replace_document(back)
    doc = client.get_document("Person/Jane")
    assert doc["age"] == 37


def test_shared_and_unfold(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(db=_DB)
    schema = PydanticSchema().from_db(client)

    shelf = schema.object["Shelf"](label="A1", genre=schema.object["Genre"].fiction)
    lib = schema.object["Library"](name="Central", shelves={shelf})
    client.insert_document(lib)

    # Shelf is @unfoldable so get_document returns JSONL; list docs instead
    docs = client.get_all_documents(as_list=True)
    lib_doc = next(d for d in docs if d.get("@type") == "Library")
    back = schema.parse_document(lib_doc)
    s = next(iter(back.shelves))
    assert s.label == "A1" or s._backend_id.startswith("Shelf/")


def test_schema_diff_and_check(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(db=_DB)
    schema = PydanticSchema().from_db(client)
    assert schema.diff(client) == []

    # perturb: same @id, extra field the db does not have
    class Person(TerminusModel):
        _key = LexicalKey("name")
        name: str
        nickname: Optional[str] = None

    schema2 = PydanticSchema()
    schema2.add_obj("Person", Person)
    lines = schema2.diff(client)
    assert any("nickname" in line for line in lines)


def test_mixed_template_and_pydantic_commit(docker_url):
    client = Client(docker_url, user_agent=test_user_agent)
    client.connect(db=_DB + "_mixed")

    class LegPerson(DocumentTemplate):
        _key = LexicalKey("name")
        name: str

    class PyDoc(TerminusModel):
        label: str

    schema = Schema()
    schema.add_obj("LegPerson", LegPerson)
    schema.add_obj("PyDoc", PyDoc)
    schema.commit(client)

    loaded = PydanticSchema().from_db(client)
    assert "LegPerson" in loaded.object
    assert "PyDoc" in loaded.object
    assert issubclass(loaded.object["PyDoc"], TerminusModel)
