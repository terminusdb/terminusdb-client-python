# Pydantic models for TerminusDB — user guide

This guide covers the pydantic-native schema interface for the TerminusDB
Python client: declare your domain model once as pydantic models, and let
TerminusDB hold the schema. Documents validate against the same models on the
way in and out — no second declaration, no drift.

The pydantic interface is the primary way to manage schemas from Python. The
older `DocumentTemplate`/`WOQLSchema` API remains supported; see
[Migrating from DocumentTemplate](#migrating-from-documenttemplate).

## Why pydantic + TerminusDB

A TerminusDB schema is a graph of class documents. A pydantic model is a
typed Python class. They describe the same thing — this package makes them
interchangeable:

- Declare models once. The schema in the database is generated from them, or
  the models are generated from the schema — your choice, per project.
- Documents coming out of the database validate into your models. A document
  that fails validation means schema drift, and it fails loudly.
- Everything pydantic gives you applies: FastAPI request/response models,
  `model_dump`/`model_validate`, JSON Schema export, mypy-friendly typing.

Three supported workflows:

- **Code-first** — author models in Python, `schema.commit(client)` pushes
  the schema. Best for greenfield.
- **Schema-first** — evolve the schema in TerminusDB, `tdbpy sync` regenerates
  `schema.py`. The generated file is a check-in artefact: schema changes and
  model diffs land in the same PR.
- **Dynamic** — `PydanticSchema.from_db(client)` builds models from the
  database at runtime. Drift is impossible by construction; the trade-off is
  no static types. For tools, notebooks and agents.

`tdbpy check` is the guard rail: it diffs your local models against the
schema graph and exits non-zero when they disagree.

## Installation

```bash
pip install "terminusdb[pydantic]"
```

Requires pydantic >= 2 and Python >= 3.9. The core client keeps working
without the extra; importing `terminusdb_client.schema.pydantic` without
pydantic installed raises a single `ImportError` telling you to install the
extra.

## Declaring models

Subclass `TerminusModel` and annotate fields exactly as you would in any
pydantic model:

```python
from typing import List, Optional
from terminusdb_client.schema.pydantic import TerminusModel
from terminusdb_client.schema import LexicalKey

class Person(TerminusModel):
    """A person tracked by the system.

    Attributes
    ----------
    name : str
        Full display name.
    """

    _key = LexicalKey("name")

    name: str
    age: Optional[int] = None
    tags: List[str] = []
```

This class emits the TerminusDB schema document:

```python
{"@type": "Class", "@id": "Person",
 "@documentation": {"@comment": "A person tracked by the system.",
                    "@properties": {"name": "Full display name."}},
 "@key": {"@type": "Lexical", "@fields": ["name"]},
 "name": "xsd:string",
 "age": {"@type": "Optional", "@class": "xsd:integer"},
 "tags": {"@type": "List", "@class": "xsd:string"}}
```

Everything `DocumentTemplate` can declare, a `TerminusModel` can declare:

### Class attributes

| Attribute | Effect on the schema |
|---|---|
| `_key` | `@key` — document id scheme. All key classes: `HashKey`, `LexicalKey`, `ValueHashKey`, `RandomKey` (default), `UuidV7Key` |
| `_subdocument = []` | `@subdocument` — embedded document, no independent id |
| `_shared = True` | `"@shared": []` — reference-counted document, cascade-deleted on last unreference (see Shared documents) |
| `_unfoldable = True` | `"@unfoldable": []` — always expanded on read (see links) |
| `_abstract = []` | `@abstract` — no instances |
| `_foreign = True` | `{"@type": "Foreign"}` — opaque reference to another data product (see Foreign references) |
| `_base = "prefix/"` | `@base` — id minting prefix for this class |
| `_metadata = {...}` | `@metadata` — arbitrary class metadata (`render_as`, `order_by`, embedding config, …) |
| `_schema = my_schema` | registers the class into a `Schema` at definition time |

Underscore-prefixed names are pydantic-private by convention, never
fields. `UuidV7Key` accepts any supplied IRI as `@id` (no `@base` enforcement) —
useful when loading data that already carries external identifiers.

### Field types

The annotation alone determines the schema entry — validators, defaults and
constraints (`Field(gt=)`, `pattern=`) are client-side concerns and never
appear in the schema document. `Optional` is the only way to say a field may
be absent.

| Annotation | Schema entry |
|---|---|
| `str` / `int` / `float` / `bool` | `xsd:string` / `xsd:integer` / `xsd:double` / `xsd:boolean` |
| `datetime`, `date`, `time`, `timedelta` | `xsd:dateTime`, `xsd:date`, `xsd:time`, `xsd:duration` |
| `decimal.Decimal` | `xsd:decimal` |
| `dict` | `sys:JSON` (arbitrary JSON blob) |
| `woql_type` NewTypes (`gYear`, `anyURI`, `token`, `long`, `dayTimeDuration`, …) | their `xsd:` counterparts |
| `Optional[X]` / `X \| None` | `{"@type": "Optional", "@class": X}` |

Write `Optional[X] = None` when the field should be truly optional at
construction time — `Optional[X]` alone is still a *required* field in
pydantic. `Optional[Set[X]]` and `Optional[List[X]]` are invalid
(`TypeError`): a collection already permits zero elements.
| `List[X]` / `list[X]` | `{"@type": "List", "@class": X}` |
| `Set[X]` / `set[X]` | `{"@type": "Set", "@class": X}` |
| `Set[X]` with `Field(min_length=, max_length=)` | adds `@min_cardinality`/`@max_cardinality` (equal values collapse to `@cardinality`) |
| `Annotated[list[X], Array]` | `{"@type": "Array", "@class": X}` — ordered, gaps allowed; `@dimensions` from list nesting (`list[list[float]]` → `2`) |
| `None` (inside `TerminusUnion`) | `sys:Unit` — a tagged-union member carrying no value |
| another `TerminusModel` | object property — the class name; embedded when the target is a subdocument |
| `Enum` subclass | the enum's `@id`; the enum itself emits `{"@type": "Enum", "@value": [...]}` |
| forward reference `"Person"` | the class name (self- and mutual references) |
| `Literal`, `Union[A, B]` (non-Optional), `tuple`, `frozenset`, `Callable` | `TypeError` — not representable; see `TerminusUnion` below |

### Enums

Enums register with `TerminusEnum` (a `str, Enum` subclass); member values
are the stored values:

```python
from terminusdb_client.schema.pydantic import TerminusEnum

class Colour(TerminusEnum):
    red = "red"
    blue = "blue"
    information_technology = "Information Technology"

class Widget(TerminusModel):
    shade: Colour
```

`Colour` emits `{"@type": "Enum", "@id": "Colour", "@value": ["red", "blue",
"Information Technology"]}` and registers into the same `_schema`. Values
serialise as `member.value`.

### Subdocuments

A subdocument is embedded inside its parent — it mints no id of its own:

```python
class Address(TerminusModel):
    _subdocument = []
    street: str
    city: str

class Person(TerminusModel):
    address: Optional[Address] = None
```

`address` emits `{"@type": "Optional", "@class": "Address"}` and the stored
document embeds the `Address` object inline. Engine rule: a subdocument's
key must be `RandomKey`, `UuidV7Key` or `ValueHashKey`.

### Shared documents — `_shared`

A shared document is a *regular* document — own id, any key type, linkable
from many parents — whose lifecycle is reference-counted: when its last
inbound reference is removed (parent deleted, field updated, triple
removed), the engine cascade-deletes it at commit, recursively, including
circular islands of shared documents that reference only each other.

```python
class Footnote(TerminusModel):
    _shared = True
    label: str
    content: str

class Article(TerminusModel):
    notes: Set[Footnote]    # several articles may share one Footnote
```

Constraints: `_shared` is mutually exclusive with `_subdocument` (a class
definition carrying both raises `ValueError` at declaration time), is
inherited, and unlike a subdocument it does **not** auto-unfold — add
`_unfoldable` on the class or `Unfold` on the property for that. A shared
document with zero references may be created standalone; the cascade only
fires when a reference is *removed*.

### Foreign references — `_foreign`

`Foreign` types are opaque references to documents living in another data
product: no fields, no referential integrity — just an identifier.

```python
class Person(TerminusModel):
    _foreign = True

class Event(TerminusModel):
    person: Optional[Person] = None    # stores the IRI only
```

`Person` emits `{"@type": "Foreign", "@id": "Person"}` (no properties).
Assign a plain string id/IRI on write; on read it materialises as a stub
carrying `_backend_id` — fields never unfold because nothing local exists
to unfold.

### Tagged unions — `TerminusUnion`

A tagged union says "the document carries the fields of exactly one member".
Declare members as fields on a `TerminusUnion` subclass:

```python
from terminusdb_client.schema.pydantic import TerminusUnion

class Contact(TerminusUnion):
    email: str          # "xsd:string" member
    phone: Optional[str] = None
```

emits `{"@type": "TaggedUnion", "@id": "Contact", "@oneOf": {"email": ...,
"phone": ...}}`. Non-Optional `Union[A, B]` annotations are *not* the same
thing — use `TerminusUnion`.

A member with no value is `sys:Unit`, written as a `None`-annotated field —
the canonical binary-tree example:

```python
class BinaryTree(TerminusUnion):
    leaf: None          # "leaf": "sys:Unit"
    node: "Node"
```

(TerminusDB also supports the general `@oneOf` list on ordinary `Class`
documents — multiple disjoint property groups. `TerminusUnion` covers the
`TaggedUnion` sugar only; the general form is a documented limitation, see
the reference chapter.)

### Inheritance and abstract classes

```python
class Party(TerminusModel):
    _abstract = []

class Person(Party):
    name: str
```

`Person` emits `"@inherits": "Party"` — fields resolve through `__mro__`
exactly as pydantic resolves them.

### Documentation

The class docstring is parsed with `numpydoc` (`ClassDoc`) and becomes
`@documentation`; `Field(description=...)` adds or overrides a property
entry. Per-language (`@language`) documentation is handled by the engine —
author the default text in code.

## Documents and links: the unfold contract

Links to other documents are the one place where TerminusDB storage and
pydantic models differ in shape. TerminusDB may return a link as an id
string (`"Person/bob"`), as a `{"@type", "@id"}` reference, or as a full
nested document — depending on schema markers and the request flag. The
client maps each mechanism to exactly one pydantic construct:

| TerminusDB mechanism | Pydantic equivalent |
|---|---|
| `@subdocument` class | Nested `TerminusModel` — always a full embedded object |
| `"@unfoldable": []` on the class | `_unfoldable = True` on the model — always expanded |
| `"@unfold": true` on a property | `Annotated[Sub, Unfold]` marker — this property always expands |
| `unfold` flag on a document request | `client.get_document(id, unfold=True)` — expands reachable links server-side |
| folded link (`"Class/id"` string or `{"@type","@id"}`) | **stub** — an id-carrying model with no populated fields |

```python
from typing import Annotated
from terminusdb_client.schema.pydantic import TerminusModel, Unfold

class Audit(TerminusModel):
    _subdocument = []
    _unfoldable = True       # class marker: this type always expands

class Ticket(TerminusModel):
    title: str
    audit: Annotated[Optional[Audit], Unfold] = None  # property marker
    assignee: Optional[Person] = None                 # ordinary link — may be a stub
```

`Unfold` is a metadata marker for `Annotated`; it emits `"@unfold": true`
on the property — `{"@class": "Audit", "@unfold": true}` for a required
field, `{"@type": "Optional", "@class": "Audit", "@unfold": true}` inside
complex specs (`Optional`, `Set`, `List`, `Array`). `_unfoldable` emits
`"@unfoldable": []` on the class document. Unfoldability is transitive
through inheritance, matching the engine.

Unfolding is bounded: the engine detects cycles (a document that unfolds
into itself comes back as an IRI at the repeated leaf) and caps expansion
at a configurable default of 500,000 documents.

### Stubs

A folded link loads as a **stub**: a model instance carrying only its
`_backend_id`, with no fields populated. Accessing a field on a stub raises
`AttributeError`; serialising a stub writes its id back — a document with
unresolved links round-trips losslessly.

```python
ticket = schema.parse_document(client.get_document("Ticket/1"))
ticket.assignee._backend_id        # "Person/bob"
ticket.assignee.name               # AttributeError — it's a stub

bob = schema.parse_document(client.get_document(ticket.assignee._backend_id))
```

Stubs are the same compromise `DocumentTemplate` always made — the
alternative (fetching every linked document eagerly) is not offered. When
you want real objects, fetch with `unfold=True` and every link arrives as a
full model instead:

```python
ticket = schema.parse_document(client.get_document("Ticket/1", unfold=True))
ticket.assignee.name               # works — unfolded document
```

## The schema lifecycle

### Model-first: commit

Register models into a `Schema` and push:

```python
from terminusdb_client.schema import Schema
from terminusdb_client.client import Client

schema = Schema(title="Ticketing", description="Support tickets")
for cls in (Person, Ticket, Audit, Colour):
    schema.add_obj(cls.__name__, cls)

client = Client("http://localhost:6363")
client.connect(db="tickets", team="admin", account="admin", key="root")
schema.commit(client, commit_msg="ticketing schema v1")
```

Setting `cls._schema = schema` at class-definition time registers
automatically — the same idiom as `DocumentTemplate`. `Schema` also accepts
`metadata={...}`: arbitrary JSON written verbatim into the context object's
`@metadata` — this is where data-product options such as
`terminusdb.options` (`store_indices`, `store_clustering`) live.

### Schema-first: `tdbpy sync`

Inside a `tdbpy` project (`tdbpy startproject` creates `config.json` +
`.TDB`):

```bash
tdbpy sync --format pydantic      # writes schema.py with TerminusModel classes
tdbpy sync                        # writes schema.py with DocumentTemplate classes (default)
```

`sync --format pydantic` also records `"model_backend": "pydantic"` in
`config.json`; subsequent `sync` runs keep the pydantic emitter, and
`commit`/`check` know which module shape to expect. The generated file is
meant to be committed to version control — review schema and code together.

### Drift gate: `tdbpy check`

```bash
tdbpy check                    # exit 0: models match the schema graph
tdbpy check --ignore-docs      # ignore @documentation differences
```

On drift it prints which classes are missing on each side and a unified
diff of differing classes, then exits 1. Wire it into CI and "the schema
changed without regenerating models" becomes impossible to merge.
`Schema.diff(client, ignore_docs=False)` exposes the same comparison
(returning a list of diff lines) for tests and tooling.

## Typed documents

`parse_document` is the single entry point — it finds the model by `@type`
and validates:

```python
schema = PydanticSchema().from_db(client)   # or a Schema with models added via add_obj/_schema

ticket = schema.parse_document(client.get_document("Ticket/1"))
ticket.title                        # str, validated
ticket._backend_id                  # "Ticket/1"
```

Writing uses the ordinary document API — models serialise through
`_obj_to_dict`, which the client already understands:

```python
new_ticket = Ticket(title="Login broken", audit=Audit(by="alice"))
client.insert_document(new_ticket)       # mints + stamps id
new_ticket._backend_id                   # "Ticket/<minted>"

client.update_document(new_ticket)       # writes changed fields
client.replace_document(new_ticket)      # full replace
client.delete_document(new_ticket)       # or an id string
```

After a successful insert, `client` stamps the minted id onto the object
(`_backend_id`), exactly as it does for `DocumentTemplate` instances.

Multi-object writes use the same `@capture`/`@ref` graph the engine
expects: linking a not-yet-inserted object emits a `@ref`, and
`insert_document` writes the whole reachable graph in one call:

```python
bob = Person(name="bob")
ticket = Ticket(title="x", assignee=bob)
client.insert_document(ticket)    # writes bob + ticket in one request
```

`to_document()` returns `(doc, references)` — the dict your model becomes
on the wire. `from_document(doc)` / `schema.parse_document(doc)` is the
inverse, for when you fetch raw dicts yourself (e.g. via WOQL).

## Evolving the schema

Two loops, one source of truth.

**Database-first (recommended for production).** Evolve the schema in
TerminusDB — via the migration API or a schema push — then regenerate:

```bash
tdbpy sync --format pydantic   # models follow the database
git diff schema.py             # review what changed
tdbpy check                    # 0 — local matches server
```

The regenerated file *is* the reviewable artefact of the migration.

**Model-first (local development).** Edit the model, check the diff, push:

```bash
tdbpy check                    # shows the pending schema diff
tdbpy commit                   # pushes schema.py, full_replace
```

When a model-first push would lose data (dropped fields, narrowed types)
the engine's migration machinery decides what happens — see the schema
migration reference. `--ignore-docs` on `check` separates cosmetic doc
edits from structural drift.

## Dynamic loading

```python
from terminusdb_client.schema.pydantic import PydanticSchema

schema = PydanticSchema().from_db(client, select=["Person", "Ticket"])
Person = schema.object["Person"]
person = schema.parse_document(client.get_document("Person/bob"))
```

`from_db` rebuilds the full class graph — inheritance, enums, tagged
unions, subdocuments, keys, forward and self references — as real pydantic
models. Use it for tools, notebooks and agents that must match whatever the
database currently says; use codegen (`sync`) for application code, where
static types and reviewable diffs matter.

## Migrating from DocumentTemplate

The declaration syntaxes coexist in one `Schema` — migrate a class at a
time, and the emitted schema document (hence the database) does not change:

| `DocumentTemplate` | `TerminusModel` |
|---|---|
| `class P(DocumentTemplate):` | `class P(TerminusModel):` |
| `name: str` | `name: str` — unchanged |
| `_key = LexicalKey("name")` | unchanged |
| `_subdocument`, `_abstract`, `_base` | unchanged |
| `EnumTemplate` + `transform_enum_dict` | `TerminusEnum` (`str, Enum`) with explicit values |
| `TaggedUnion` | `TerminusUnion` (fields are the union members) |
| `typeguard` on `__setattr__` | pydantic validators |
| `obj._id` | `obj._backend_id` for loaded ids; `_id` still computes custom ids |
| — (new constructs) | `_shared`, `_foreign`, `_metadata`, `Unfold`, `Array`, `Field` cardinality — pydantic-only additions |

`DocumentTemplate` stays supported — existing code keeps working. New code
should use `TerminusModel`: it is the documented interface going forward,
and the only one that gains the codegen/check tooling.

## Recipes

**FastAPI.** The same model is the API contract and the database schema:

```python
@app.post("/tickets")
async def create_ticket(ticket: Ticket):            # pydantic validates the request
    client.insert_document(ticket)                  # and the document
    return {"id": ticket._backend_id}
```

**Notebooks.** Pull the live schema, explore:

```python
schema = PydanticSchema().from_db(client)
for name, cls in schema.object.items():
    print(name, list(cls.model_fields))
```

**CI drift gate.**

```yaml
- run: tdbpy sync --format pydantic && tdbpy check
```

## Reference

### Error catalogue

- `TypeError: use TerminusUnion for non-Optional unions` — `Union[A, B]`
  or `Literal` is not a schema type; declare `TerminusUnion`/`Enum`.
- `AttributeError` on a model field — the value is a **stub**, not a
  populated object; fetch with `unfold=True` or resolve `_backend_id`.
- `ValidationError` from `parse_document` — the stored document does not
  satisfy the model. That is drift: sync the models or fix the data.
- `ImportError: install terminusdb[pydantic]` — missing the extra.
- `ValueError` from `client` on insert — "Subdocument cannot be added
  directly" (subdocuments only exist embedded) or a non-model object.
- `ValueError` at class definition — `_shared` and `_subdocument` on one
  class (mutually exclusive), or `_foreign` with declared fields.

### Limitations

Not yet mapped to pydantic constructs — `from_db` raises a precise error
rather than round-tripping these incorrectly:

- the general `@oneOf` list on `Class` documents (only the `TaggedUnion`
  sugar is covered by `TerminusUnion`)
- the `Table` type family (engine surface without reference-guide docs)
- `@language` multilingual `@documentation` (author the default language;
  per-language docs are engine-managed)
- custom context prefixes and prefixed names (`layer:Layer`,
  `layer:identifier`) — `_base`/`schema_ref` cover the common cases
- per-member enum docs (`@values` on `Enum` `@documentation`)
- `sys:JSONDocument` — unstructured JSON storage is an insert-flag feature
  (`client.insert_document(raw_dict)` / CLI `-j`), not a schema construct

### FAQ

- *Do field defaults go into the schema?* No — defaults and constraints
  are client-side. Only `Optional[]` changes the schema.
- *Can a project mix `DocumentTemplate` and `TerminusModel`?* Yes — one
  `Schema`, both kinds of class, one commit.
- *Which file does `sync` write?* Always `schema.py`; `model_backend` in
  `config.json` decides whether it contains `TerminusModel` or
  `DocumentTemplate` classes.
- *What about `Literal` fields?* Not schema types; use an `Enum`.
- *Is `pydantic` required for the rest of the client?* No — it is an
  optional extra; everything else works as before.
