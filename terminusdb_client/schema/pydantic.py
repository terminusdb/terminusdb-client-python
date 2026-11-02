"""Pydantic-native schema layer for TerminusDB.

TerminusModel subclasses declare the same schema DocumentTemplate declares,
and emit byte-identical class documents. Instances serialise through
``_obj_to_dict`` so the client document API works unchanged.
"""
import decimal
import types as _types
from enum import Enum
from typing import (
    Annotated,
    ClassVar,
    ForwardRef,
    List,
    Optional,
    Set,
    Union,
    get_args,
    get_origin,
)

from numpydoc.docscrape import ClassDoc

try:
    from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, create_model
    from pydantic.fields import FieldInfo
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "install terminusdb[pydantic] to use pydantic models"
    ) from e

from .. import woql_type as wt
from ..client.Client import Client
from .schema import (
    HashKey,
    LexicalKey,
    RandomKey,
    Schema,
    UuidV7Key,
    ValueHashKey,
    _check_and_fix_custom_id,
)

_PY_CONVERT_TYPE = dict(wt.CONVERT_TYPE)
_PY_CONVERT_TYPE[decimal.Decimal] = "xsd:decimal"

_KEY_TYPES = {
    k.at_type: k
    for k in (HashKey, LexicalKey, ValueHashKey, RandomKey, UuidV7Key)
}
_SUBDOC_KEYS = {"Random", "ValueHash", "UuidV7"}


class Unfold:
    """Annotated marker: emit ``"@unfold": true`` on this property."""


class Array:
    """Annotated marker: emit ``"@type": "Array"`` for this property.

    ``@dimensions`` is inferred from list nesting depth.
    """


def _is_subdoc(cls):
    return getattr(cls, "_subdocument", None) is not None


def _unwrap_optional(ann):
    """Return (is_optional, inner) for Optional[...] / X | None."""
    origin = get_origin(ann)
    if origin is Union or origin is _types.UnionType:
        args = get_args(ann)
        if len(args) == 2 and type(None) in args:
            inner = args[0] if args[1] is type(None) else args[1]
            return True, inner
        raise TypeError(
            f"use TerminusUnion for non-Optional unions: {ann}"
        )
    return False, ann


def _annotation_to_woql(ann):
    """Map a pydantic field annotation to a TerminusDB property spec."""
    if ann is None or ann is type(None):
        return "sys:Unit"
    _, ann = _unwrap_optional_pair(ann)

    origin = get_origin(ann)
    if origin is not None and (origin is Union or origin is _types.UnionType):
        # only reachable for unions whose optional-ness was already consumed
        raise TypeError(f"use TerminusUnion for non-Optional unions: {ann}")
    if origin in (list, List):
        return {"@type": "List", "@class": _annotation_to_woql(get_args(ann)[0])}
    if origin is frozenset:
        raise TypeError(
            "frozenset is not a TerminusDB type; use Set[X] / set[X]"
        )
    if origin in (set, Set):
        return {"@type": "Set", "@class": _annotation_to_woql(get_args(ann)[0])}
    if isinstance(ann, str):
        return ann  # class-name reference (generated code, mutual refs)
    if isinstance(ann, ForwardRef):
        return ann.__forward_arg__
    if ann in _PY_CONVERT_TYPE:
        return _PY_CONVERT_TYPE[ann]
    if isinstance(ann, type):
        if issubclass(ann, (TerminusModel, Enum)):
            return ann.__name__
    raise TypeError(
        f"annotation {ann!r} cannot be converted to a TerminusDB type; "
        "declare an Enum or TerminusUnion instead"
    )


def _unwrap_optional_pair(ann):
    """Return (optional_wrapped_spec_or_None, inner_ann)."""
    is_opt, inner = _unwrap_optional(ann)
    return is_opt, inner


def _field_to_woql(field):
    """Map a pydantic FieldInfo to a TerminusDB property spec,
    applying Unfold/Array markers and Set cardinality."""
    ann = field.annotation
    metadata = list(field.metadata)
    # peel Annotated if it survived on .annotation
    while get_origin(ann) is Annotated:
        inner_args = get_args(ann)
        metadata = list(inner_args[1:]) + metadata
        ann = inner_args[0]

    is_opt, inner = _unwrap_optional(ann)
    while get_origin(inner) is Annotated:
        inner_args = get_args(inner)
        metadata = list(inner_args[1:]) + metadata
        inner = inner_args[0]
    spec = _annotation_to_woql(inner)
    if is_opt:
        if isinstance(spec, dict) and spec.get("@type") in ("Set", "List"):
            raise TypeError(
                "Optional cannot wrap Set/List — a collection already "
                "permits zero elements"
            )
        spec = {"@type": "Optional", "@class": spec}

    if any(m is Array or isinstance(m, Array) for m in metadata):
        spec = _to_array_spec(inner)

    if any(m is Unfold or isinstance(m, Unfold) for m in metadata):
        if isinstance(spec, dict):
            spec = {**spec, "@unfold": True}
        else:
            spec = {"@class": spec, "@unfold": True}

    # Set cardinality from Field(min_length=, max_length=)
    if isinstance(spec, dict) and spec.get("@type") == "Set":
        lo = hi = None
        for m in metadata:
            if getattr(m, "min_length", None) is not None:
                lo = m.min_length
            if getattr(m, "max_length", None) is not None:
                hi = m.max_length
        if lo is not None or hi is not None:
            if lo == hi:
                spec["@cardinality"] = lo
            else:
                if lo is not None:
                    spec["@min_cardinality"] = lo
                if hi is not None:
                    spec["@max_cardinality"] = hi
    return spec


def _to_array_spec(ann):
    """Build an Array spec; @dimensions from list nesting depth."""
    dims = 0
    inner = ann
    while get_origin(inner) in (list, List):
        dims += 1
        inner = get_args(inner)[0]
    spec = {"@type": "Array", "@class": _annotation_to_woql(inner)}
    if dims > 1:
        spec["@dimensions"] = dims
    return spec


def _enum_to_dict(cls):
    """Schema document for an Enum subclass."""
    return {
        "@type": "Enum",
        "@id": cls.__name__,
        "@value": [m.value for m in cls],
    }


class TerminusEnum(str, Enum):
    """``str, Enum`` with TerminusDB schema emission and optional
    ``_schema`` registration. Values are the stored wire values."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        schema = cls.__dict__.get("_schema")
        if schema is not None:
            if not hasattr(schema, "object"):
                schema.object = {}
            schema.add_obj(cls.__name__, cls)

    def __str__(self):
        return self.value

    @classmethod
    def _to_dict(cls):
        return _enum_to_dict(cls)


class TerminusModel(BaseModel):
    """A TerminusDB document class declared as a pydantic model."""

    model_config = ConfigDict(extra="ignore")

    _schema: ClassVar = None
    _key: ClassVar = RandomKey()
    _subdocument: ClassVar = None
    _abstract: ClassVar = None
    _shared: ClassVar = None
    _unfoldable: ClassVar = None
    _foreign: ClassVar = None
    _metadata: ClassVar = None
    _base: ClassVar = None
    _backend_id = PrivateAttr(default=None)
    _custom_id = PrivateAttr(default=None)
    _isinstance = PrivateAttr(default=True)
    _capture = PrivateAttr(default=None)

    def __hash__(self):
        return id(self)

    def __init__(self, _id=None, _backend_id=None, **data):
        super().__init__(**data)
        if _backend_id is not None:
            self._backend_id = _backend_id
        if _id is not None:
            if not self._allows_custom_id():
                raise ValueError(
                    f"Customized id is not allowed. {self.__class__} is a"
                    " subdocument or has set id key scheme."
                )
            self._custom_id = _id
        cls = self.__class__
        self._capture = f"{cls.__name__}{id(cls)}/{cls._capture_order}"
        cls._capture_order += 1

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        cls._capture_order = 0
        # declaration-time validations
        if _is_subdoc(cls) and getattr(cls, "_shared", None):
            raise ValueError(
                f"{cls.__name__}: @shared and @subdocument are mutually exclusive"
            )
        if getattr(cls, "_foreign", None) and cls.model_fields:
            raise ValueError(
                f"{cls.__name__}: a Foreign class declares no fields"
            )
        declared_key = cls.__dict__.get("_key")
        if (
            _is_subdoc(cls)
            and declared_key is not None
            and declared_key.__class__.at_type not in _SUBDOC_KEYS
        ):
            raise ValueError(
                f"{cls.__name__}: a subdocument key must be Random, "
                "ValueHash or UuidV7"
            )
        schema = cls.__dict__.get("_schema", cls._schema)
        if schema is not None:
            if not hasattr(schema, "object"):
                schema.object = {}
            schema.add_obj(cls.__name__, cls)

    @classmethod
    def _allows_custom_id(cls):
        if _is_subdoc(cls):
            return False
        declared = cls.__dict__.get("_key")
        if declared is None:
            return True
        return isinstance(declared, (RandomKey, UuidV7Key))

    @property
    def _id(self):
        if self._backend_id:
            return self._backend_id
        if self._custom_id:
            if isinstance(self.__class__._key, UuidV7Key):
                return self._custom_id
            return _check_and_fix_custom_id(
                self.__class__.__name__, self._custom_id
            )
        return None

    @_id.setter
    def _id(self, custom_id):
        if self._allows_custom_id():
            self._custom_id = custom_id
        else:
            raise ValueError(
                f"Customized id is not allowed. {self.__class__} is a"
                " subdocument or has set id key scheme."
            )

    def _embedded_rep(self):
        """Representation when embedded as an object property."""
        if _is_subdoc(self.__class__):
            return self._obj_to_dict()
        if self._id:
            return {"@id": self._id, "@type": "@id"}
        return {"@ref": self._capture}

    @classmethod
    def _to_dict(cls, skip_checking=False):
        """Emit the TerminusDB class document."""
        if not skip_checking:
            _check_cycling(cls)
        if getattr(cls, "_foreign", None):
            return {"@type": "Foreign", "@id": cls.__name__}
        is_union = issubclass(cls, TerminusUnion) and cls is not TerminusUnion
        result = {
            "@type": "TaggedUnion" if is_union else "Class",
            "@id": cls.__name__,
        }
        stop = TerminusUnion if is_union else TerminusModel
        parents = [x.__name__ for x in cls.__mro__]
        inherited = parents[1 : parents.index(stop.__name__)]
        if inherited:
            result["@inherits"] = inherited

        if cls.__doc__:
            doc_obj = ClassDoc(cls)
            prop_doc = {}
            for thing in doc_obj["Attributes"]:
                if thing.desc and thing.name in cls.model_fields:
                    prop_doc[thing.name] = "\n".join(thing.desc)
            for fname, field in cls.model_fields.items():
                if field.description:
                    prop_doc[fname] = field.description
            result["@documentation"] = {
                "@comment": "\n".join(
                    doc_obj["Summary"] + doc_obj["Extended Summary"]
                ),
                "@properties": prop_doc,
            }

        if getattr(cls, "_base", None) is not None:
            result["@base"] = cls._base
        if _is_subdoc(cls):
            result["@subdocument"] = cls._subdocument
            key_type = "Random"
            key = getattr(cls, "_key", None)
            if key is not None and key.__class__.at_type in _SUBDOC_KEYS:
                key_type = key.__class__.at_type
            result["@key"] = {"@type": key_type}
        if getattr(cls, "_abstract", None) is not None:
            result["@abstract"] = cls._abstract
        if getattr(cls, "_unfoldable", None):
            result["@unfoldable"] = []
        if getattr(cls, "_shared", None):
            result["@shared"] = []
        if getattr(cls, "_metadata", None) is not None:
            result["@metadata"] = cls._metadata
        if not _is_subdoc(cls) and getattr(cls, "_key", None) is not None:
            if hasattr(cls._key, "_keys"):
                result["@key"] = {
                    "@type": cls._key.__class__.at_type,
                    "@fields": cls._key._keys,
                }
            else:
                result["@key"] = {"@type": cls._key.__class__.at_type}
        for attr, field in cls.model_fields.items():
            result[attr] = _field_to_woql(field)
        return result

    def _obj_to_dict(self, skip_checking=False):
        """Emit the instance document; returns (doc, references)."""
        result = {"@type": self.__class__.__name__}
        if self._id:
            result["@id"] = self._id
        elif not _is_subdoc(self.__class__):
            result["@capture"] = self._capture

        references = {}
        for item, field in self.__class__.model_fields.items():
            if not hasattr(self, item):
                continue
            the_item = getattr(self, item)
            if the_item is None:
                if (
                    field.annotation is type(None)
                    and item in self.model_fields_set
                ):
                    result[item] = []
                continue
            if hasattr(the_item, "_embedded_rep"):
                ref_obj = the_item._embedded_rep()
                if "@ref" in ref_obj:
                    references[ref_obj["@ref"]] = the_item
                elif "@id" in ref_obj:
                    pass
                else:
                    (sub_item, refs) = ref_obj
                    references = {**references, **refs}
                    ref_obj = sub_item
                result[item] = ref_obj
            elif isinstance(the_item, (list, set, frozenset)):
                new_item = []
                for sub_item in the_item:
                    if hasattr(sub_item, "_embedded_rep"):
                        ref_obj = sub_item._embedded_rep()
                        if "@ref" in ref_obj:
                            references[ref_obj["@ref"]] = sub_item
                        elif "@id" in ref_obj:
                            pass
                        else:
                            (sub_item2, refs) = ref_obj
                            references = {**references, **refs}
                            ref_obj = sub_item2
                        new_item.append(ref_obj)
                    elif isinstance(sub_item, Enum):
                        new_item.append(sub_item.value)
                    else:
                        new_item.append(sub_item)
                result[item] = new_item
            else:
                if isinstance(the_item, Enum):
                    result[item] = the_item.value
                else:
                    result[item] = wt.datetime_to_woql(the_item)
        return (result, references)

    def to_document(self):
        """Public alias for :meth:`_obj_to_dict`."""
        return self._obj_to_dict()

    @classmethod
    def _stub(cls, doc_id):
        """An id-carrying instance with no fields — a folded link."""
        obj = cls.model_construct()
        obj._backend_id = doc_id
        return obj

    @classmethod
    def from_document(cls, doc, registry=None):
        """Build a validated instance from a TerminusDB document dict.

        ``registry`` maps class names to classes for resolving linked
        documents (stubs) — pass ``schema.object``.
        """
        data = {}
        for key, value in doc.items():
            if key.startswith("@"):
                continue
            field = cls.model_fields.get(key)
            if field is not None:
                value = _coerce_value(field.annotation, value, registry)
            data[key] = value
        obj = cls.model_validate(data)
        if doc.get("@id"):
            obj._backend_id = doc["@id"]
        return obj


class TerminusUnion(TerminusModel):
    """Declares ``"@type": "TaggedUnion"`` — fields are the members.

    A ``None``-annotated field emits ``"sys:Unit"`` (a member carrying no
    value).
    """


def _check_cycling(cls):
    """A subdocument may not embed (a superclass of) itself."""
    if getattr(cls, "_subdocument", None) is None:
        return
    mro_names = {c.__name__ for c in cls.__mro__}
    for field in cls.model_fields.values():
        ann = field.annotation
        _, inner = _unwrap_optional(ann)
        while get_origin(inner) in (list, List, set, Set):
            inner = get_args(inner)[0]
        if isinstance(inner, ForwardRef):
            name = inner.__forward_arg__.split(".")[-1].strip("'\"")
        elif isinstance(inner, str):
            name = inner
        else:
            name = getattr(inner, "__name__", str(inner))
        if name in mro_names:
            raise RecursionError(f"Embbding {inner} cause recursions.")


def _coerce_value(ann, value, registry):
    """Convert a wire value into what pydantic can validate for ``ann``."""
    if value is None:
        return value
    is_opt, inner = _unwrap_optional(ann)
    origin = get_origin(inner)
    if origin in (list, List):
        items = value if isinstance(value, list) else [value]
        return [_coerce_value(get_args(inner)[0], v, registry) for v in items]
    if origin in (set, frozenset, Set):
        items = value if isinstance(value, (list, set)) else [value]
        return {
            _coerce_value(get_args(inner)[0], v, registry) for v in items
        }
    target = inner
    if isinstance(target, (str, ForwardRef)):
        name = target if isinstance(target, str) else target.__forward_arg__
        name = name.split(".")[-1].strip("'\"")
        target = registry.get(name) if registry else None
    if isinstance(target, type) and issubclass(target, TerminusModel):
        if isinstance(value, str):
            return target._stub(value)
        if isinstance(value, dict):
            keys = [k for k in value if not k.startswith("@")]
            if not keys or value.get("@type") == "@id":
                return target._stub(value.get("@id"))
            return target.from_document(value, registry)
        return value
    if inner is type(None) and value == []:
        return None
    return value


def _spec_to_annotation(spec):
    """Convert a TerminusDB property spec to (annotation, default) for
    ``create_model``."""
    if isinstance(spec, str):
        if spec == "sys:Unit":
            return (Optional[type(None)], None)
        if spec[:4] == "xsd:" or spec[:4] == "sys:":
            return (wt.from_woql_type(spec, skip_convert_error=True), ...)
        return (spec, ...)  # class-name reference
    if not isinstance(spec, dict):
        raise RuntimeError(f"{spec} is not a TerminusDB property spec")
    spec = dict(spec)
    unfold = spec.pop("@unfold", None)
    cardinality = {}
    for key in ("@cardinality", "@min_cardinality", "@max_cardinality"):
        if key in spec:
            cardinality[key] = spec.pop(key)
    ann, default = _spec_inner(spec)
    if cardinality:
        lo = cardinality.get("@min_cardinality", cardinality.get("@cardinality"))
        hi = cardinality.get("@max_cardinality", cardinality.get("@cardinality"))
        default = Field(min_length=lo, max_length=hi)
        if lo is None and hi is None:
            default = Field()
    if unfold:
        ann = Annotated[ann, Unfold]
    return (ann, default)


def _spec_inner(spec):
    spec_type = spec.get("@type")
    inner_spec = spec.get("@class")
    if inner_spec is None:
        raise RuntimeError(f"{spec} is not a TerminusDB property spec")
    if spec_type is None:
        # bare {"@class": X} — a plain link property
        ann, default = _spec_to_annotation(inner_spec)
        return (ann, ...)
    if spec_type == "Optional":
        ann, _ = _spec_to_annotation(inner_spec)
        return (Optional[ann], None)
    if spec_type == "Set":
        ann, _ = _spec_to_annotation(inner_spec)
        return (Set[ann], Field(default_factory=set))
    if spec_type == "List":
        ann, _ = _spec_to_annotation(inner_spec)
        return (List[ann], Field(default_factory=list))
    if spec_type == "Array":
        dims = spec.get("@dimensions", 1)
        ann, _ = _spec_to_annotation(inner_spec)
        for _ in range(dims):
            ann = list[ann]
        return (Annotated[ann, Array], ...)
    if spec_type == "Cardinality":
        # deprecated family: treat as Set; caller adds cardinality props
        ann, _ = _spec_to_annotation(inner_spec)
        return (Set[ann], ...)
    raise RuntimeError(f"{spec} is not a TerminusDB property spec")


class PydanticSchema(Schema):
    """A Schema whose ``from_db`` rebuilds pydantic models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._building = set()

    def _construct_context(self, context_dict):
        super()._construct_context(context_dict)
        if context_dict.get("@metadata") is not None:
            self.metadata = context_dict["@metadata"]

    def _construct_class(self, class_obj_dict):
        class_id = class_obj_dict.get("@id")
        existing = self.object.get(class_id)
        if existing is not None and not isinstance(existing, str):
            return existing
        if class_id in self._building:
            raise RuntimeError(f"inheritance cycle involving {class_id}")
        obj_type = class_obj_dict.get("@type")

        if obj_type == "Enum":
            members = class_obj_dict.get("@value")
            if not members:
                raise RuntimeError(f"{class_obj_dict} not exist in database schema")
            enum_dict = {
                v.lower().replace(" ", "_"): v for v in members
            }
            new_class = TerminusEnum(class_id, enum_dict)
            self.add_obj(class_id, new_class)
            return new_class

        self._building.add(class_id)
        try:
            if obj_type == "TaggedUnion":
                base = TerminusUnion
                superclasses = [base]
            elif obj_type == "Foreign":
                superclasses = [TerminusModel]
            elif obj_type == "Class":
                inherits = class_obj_dict.get("@inherits")
                if inherits:
                    if isinstance(inherits, str):
                        inherits = [inherits]
                    superclasses = []
                    for parent in inherits:
                        parent_obj = self.object.get(parent)
                        if parent_obj is None or isinstance(parent_obj, str):
                            parent_doc = self._all_existing_classes.get(parent)
                            if parent_doc is None:
                                raise RuntimeError(
                                    f"{parent} not exist in database schema"
                                )
                            parent_obj = self._construct_class(parent_doc)
                        superclasses.append(parent_obj)
                else:
                    superclasses = [TerminusModel]
            else:
                raise RuntimeError(f"{class_obj_dict} is not a schema class")

            fields = {}
            attrs = {}
            docstring = None
            prop_docs = {}
            for key, value in class_obj_dict.items():
                if key[0] != "@":
                    fields[key] = _spec_to_annotation(value)
                elif key == "@subdocument":
                    attrs["_subdocument"] = value
                elif key == "@abstract":
                    attrs["_abstract"] = value
                elif key == "@unfoldable":
                    attrs["_unfoldable"] = True
                elif key == "@shared":
                    attrs["_shared"] = True
                elif key == "@metadata":
                    attrs["_metadata"] = value
                elif key == "@base":
                    attrs["_base"] = value
                elif key == "@key":
                    key_type = _KEY_TYPES.get(value.get("@type"))
                    if key_type is None:
                        raise RuntimeError(
                            f"{value} is not a TerminusDB key type"
                        )
                    fields_key = value.get("@fields")
                    attrs["_key"] = (
                        key_type(fields_key) if fields_key else key_type()
                    )
                elif key == "@documentation":
                    doc = value[0] if isinstance(value, list) else value
                    docstring = doc.get("@comment") or None
                    prop_docs = doc.get("@properties") or {}
            for prop, descr in prop_docs.items():
                if prop in fields:
                    ann, default = fields[prop]
                    if isinstance(default, FieldInfo):
                        default.description = descr
                    else:
                        default = Field(default=default, description=descr)
                    fields[prop] = (ann, default)

            new_class = create_model(
                class_id,
                __base__=tuple(superclasses),
                __doc__=docstring,
                __config__=ConfigDict(extra="ignore"),
                **fields,
            )
            for attr, val in attrs.items():
                setattr(new_class, attr, val)
            if obj_type == "Foreign":
                new_class._foreign = True
            self.add_obj(class_id, new_class)
            return new_class
        finally:
            self._building.discard(class_id)

    def from_db(self, client: Client, select: Optional[List[str]] = None):
        super().from_db(client, select=select)
        namespace = self.object
        for cls in list(namespace.values()):
            if isinstance(cls, type) and issubclass(cls, TerminusModel):
                try:
                    cls.model_rebuild(_types_namespace=namespace)
                except Exception:
                    pass  # unresolved refs stay ForwardRef; _to_dict still works
        return self

    def parse_document(self, doc):
        """Materialise a document dict into the registered class."""
        obj_type = doc.get("@type")
        cls = self.object.get(obj_type)
        if cls is None or isinstance(cls, str):
            raise ValueError(
                f"{obj_type} is not in current schema. (Received {doc})"
            )
        if isinstance(cls, type) and issubclass(cls, TerminusModel):
            return cls.from_document(doc, self.object)
        return self._construct_object(doc)

    def import_objects(self, obj_dict):
        if isinstance(obj_dict, dict):
            return self.parse_document(obj_dict)
        return [self.parse_document(d) for d in obj_dict]
