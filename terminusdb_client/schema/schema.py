import json
import urllib.parse as urlparse
import weakref
from copy import copy, deepcopy
from enum import Enum, EnumMeta, _EnumDict
from io import StringIO, TextIOWrapper
from typing import List, Optional, Set, Union

from numpydoc.docscrape import ClassDoc
from typeguard import check_type

from .. import woql_type as wt
from ..client.Client import Client
from ..woql_type import to_woql_type


class TerminusKey:
    def __init__(self, keys: Union[str, list, None] = None):
        if keys is not None:
            if isinstance(keys, str):
                self._keys = [keys]
            elif isinstance(keys, list):
                self._keys = keys
            else:
                ValueError(f"keys need to be either str or list but got {keys}")


class HashKey(TerminusKey):
    """Generating ID with SHA256 using provided keys"""

    at_type = "Hash"


class LexicalKey(TerminusKey):
    """Generating ID with urllib.parse.quote using provided keys"""

    at_type = "Lexical"


class ValueHashKey(TerminusKey):
    """Generating ID with SHA256"""

    at_type = "ValueHash"


class RandomKey(TerminusKey):
    """Generating ID with UUID4"""

    at_type = "Random"


def _check_cycling(class_obj: "TerminusClass"):
    """Helper function to check if the embedded subdocument is cycling"""
    if hasattr(class_obj, "_subdocument"):
        mro_names = [obj.__name__ for obj in class_obj.__mro__]
        for prop_type in class_obj._annotations.values():
            if str(prop_type) in mro_names:
                raise RecursionError(f"Embbding {prop_type} cause recursions.")


def _check_mismatch_type(prop, prop_value, prop_type):
    if hasattr(prop_type, "_to_dict"):
        prop_value_id = prop_value.__class__._to_dict().get("@id")
        prop_type_id = prop_type._to_dict().get("@id")
        if prop_value_id != prop_type_id:
            raise ValueError(
                f"Property {prop} should be of type {prop_type_id} but got value of type {prop_value_id}"
            )
    else:
        check_type(prop, prop_value, prop_type)


def _check_missing_prop(doc_obj: "DocumentTemplate"):
    """Helper function to check if the the document is missing properties (and if they are right types)"""
    class_obj = doc_obj.__class__
    for prop, prop_type in class_obj._annotations.items():
        try:  # check to let Optional pass
            check_type("None (Optional)", None, prop_type)
        except TypeError:
            try:  # extra check to let Set pass
                check_type("Empty set", set(), prop_type)
            except TypeError:
                if not hasattr(doc_obj, prop):
                    raise ValueError(f"{doc_obj} missing property: {prop}")
                else:
                    prop_value = eval(f"doc_obj.{prop}")  # noqa: S307
                    _check_mismatch_type(prop, prop_value, prop_type)
                    # raise TypeError(f"Property of {doc_obj} missing should be type {prop_type} but got {prop_value} which is {type(prop_value)}")


def _check_and_fix_custom_id(class_name, custom_id):
    if custom_id[: len(class_name) + 1] != (class_name + "/"):
        custom_id = class_name + "/" + custom_id
    return urlparse.quote(custom_id)


class TerminusClass(type):
    def __init__(cls, name, bases, nmspc):

        cls._capture_order = 0

        if "__annotations__" in nmspc:
            cls._annotations = copy(nmspc["__annotations__"])
        else:
            cls._annotations = {}

        for parent in bases:
            base_annotations = (
                parent._annotations if hasattr(parent, "_annotations") else {}
            )
            cls._annotations.update(base_annotations)

        abstract = False
        if "_abstract" in nmspc:
            if isinstance(nmspc.get("_abstract"), bool):
                abstract = nmspc.get("_abstract")
            else:
                abstract = True

        if "_subdocument" in nmspc:
            allow_custom_id = False
        elif "_key" in nmspc:
            if nmspc.get("_key").__class__ == RandomKey:
                allow_custom_id = True
            else:
                allow_custom_id = False
        else:
            allow_custom_id = True

        # _abstract should not be inherited
        cls._abstract = nmspc.get("_abstract")
        cls._instances = set()

        def init(obj, *args, **kwargs):
            if abstract:
                raise TypeError(f"{name} is an abstract class.")
            for key in cls._annotations:
                if key in kwargs:
                    value = kwargs[key]
                else:
                    value = None
                setattr(obj, key, value)
            if allow_custom_id:
                if kwargs.get("_id"):
                    obj._custom_id = kwargs.get("_id")
                else:
                    obj._custom_id = None
            else:
                if kwargs.get("_id"):
                    raise ValueError(
                        f"Customized id is not allowed. {str(obj.__class__)} is a subdocument or has set id key scheme."
                    )
            if kwargs.get("_backend_id"):
                obj._backend_id = kwargs.get("_backend_id")
            obj._isinstance = True
            obj._annotations = cls._annotations
            obj._instances.add(weakref.ref(obj))

            obj._capture = f"{name}{id(cls)}/{cls._capture_order}"
            cls._capture_order += 1

        cls.__init__ = init

        if cls._schema is not None:
            if not hasattr(cls._schema, "object"):
                cls._schema.object = {}
            cls._schema.add_obj(name, cls)

        # super().__init__(name, bases, nmspc)
        globals()[name] = cls

    def get_instances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def __repr__(cls):
        return cls.__name__


class DocumentTemplate(metaclass=TerminusClass):
    _schema = None
    _key = RandomKey()  # default key

    def __setattr__(self, name, value):
        if name[0] != "_" and value is not None:
            correct_type = self._annotations.get(name)
            _check_mismatch_type(name, value, correct_type)
        if (
            self._id
            and hasattr(self, "_key")
            and hasattr(self._key, "_keys")
            and name in self._key._keys
        ):
            raise ValueError(
                f"{name} has been used to generated id hance cannot be changed."
            )
        super().__setattr__(name, value)

    @classmethod
    def _to_dict(cls, skip_checking=False):
        if not skip_checking:
            _check_cycling(cls)
        result = {"@type": "Class", "@id": cls.__name__}
        if cls.__base__.__name__ == "TaggedUnion":
            result["@type"] = "TaggedUnion"
        elif cls.__base__.__name__ not in ["DocumentTemplate", "TaggedUnion"]:
            # result["@inherits"] = cls.__base__.__name__
            parents = [x.__name__ for x in cls.__mro__]
            result["@inherits"] = parents[1 : parents.index("DocumentTemplate")]

        if cls.__doc__:
            doc_obj = ClassDoc(cls)
            prop_doc = {}
            for thing in doc_obj["Attributes"]:
                if thing.desc:
                    prop_doc[thing.name] = "\n".join(thing.desc)
            result["@documentation"] = {
                "@comment": "\n".join(doc_obj["Summary"] + doc_obj["Extended Summary"]),
                "@properties": prop_doc,
            }

        if hasattr(cls, "_base"):
            result["@base"] = cls._base
        if hasattr(cls, "_subdocument"):
            result["@subdocument"] = cls._subdocument
            result["@key"] = {"@type": "Random"}
        if hasattr(cls, "_abstract") and cls._abstract is not None:
            result["@abstract"] = cls._abstract
        if hasattr(cls, "_key") and not hasattr(cls, "_subdocument"):
            if hasattr(cls._key, "_keys"):
                result["@key"] = {
                    "@type": cls._key.__class__.at_type,
                    "@fields": cls._key._keys,
                }
            else:
                result["@key"] = {"@type": cls._key.__class__.at_type}
        if hasattr(cls, "_annotations"):
            for attr, attr_type in cls._annotations.items():
                result[attr] = wt.to_woql_type(attr_type)
        return result

    @property
    def _id(self):
        if hasattr(self, "_backend_id") and self._backend_id:
            return self._backend_id
        if hasattr(self, "_custom_id") and self._custom_id:
            return _check_and_fix_custom_id(str(self.__class__), self._custom_id)
        else:
            return None

    @_id.setter
    def _id(self, custom_id):
        if hasattr(self, "_custom_id"):
            self._custom_id = custom_id
        else:
            raise ValueError(
                f"Customized id is not allowed. {str(self.__class__)} is a subdocument or has set id key scheme."
            )

    def _embedded_rep(self):
        """get representation for embedding as object property"""
        if hasattr(self.__class__, "_subdocument"):
            return self._obj_to_dict()
        elif hasattr(self, "_id") and self._id:
            return {"@id": self._id, "@type": "@id"}
        else:
            return {"@ref": self._capture}

    def _obj_to_dict(self, skip_checking=False):
        if not skip_checking:
            _check_missing_prop(self)
        result = {"@type": str(self.__class__)}
        if hasattr(self, "_id") and self._id:
            result["@id"] = self._id
        elif not hasattr(self, "_subdocument"):
            result["@capture"] = self._capture

        references = {}
        for item in self._annotations.keys():
            if hasattr(self, item):
                the_item = eval(f"self.{item}")  # noqa: S307
                if the_item is not None:
                    # object properties
                    if hasattr(the_item, "_embedded_rep"):
                        ref_obj = the_item._embedded_rep()
                        if '@ref' in ref_obj:
                            references[ref_obj['@ref']] = the_item
                        elif '@id' in ref_obj:
                            pass
                        else:
                            (sub_item, refs) = ref_obj
                            references = {**references, **refs}
                            ref_obj = sub_item
                        result[item] = ref_obj
                    # handle list and set (set end up passing as list for jsonlize)
                    elif isinstance(the_item, (list, set)):
                        new_item = []
                        for sub_item in the_item:
                            # inner is object properties
                            if hasattr(sub_item, "_embedded_rep"):
                                ref_obj = sub_item._embedded_rep()
                                if '@ref' in ref_obj:
                                    references[ref_obj['@ref']] = sub_item
                                elif '@id' in ref_obj:
                                    pass
                                else:
                                    (sub_item, refs) = ref_obj
                                    references = {**references, **refs}
                                    ref_obj = sub_item
                                new_item.append(ref_obj)
                            # inner is Enum
                            elif isinstance(sub_item, Enum):
                                new_item.append(str(sub_item))
                            # inner is datatypes
                            else:
                                new_item.append(sub_item)
                        result[item] = new_item
                    # Enum and datatypes
                    else:
                        if isinstance(the_item, Enum):
                            result[item] = str(the_item)
                        else:
                            result[item] = wt.datetime_to_woql(the_item)
        return (result, references)


class EnumMetaTemplate(EnumMeta):
    def __new__(
        metacls,
        cls,
        bases,
        classdict,
        *,
        boundary=None,
        _simple=False,
        **kwds,
    ):
        if "_schema" in classdict:
            schema = classdict.pop("_schema")
            classdict._member_names.remove("_schema")
            new_cls = super().__new__(metacls, cls, bases, classdict)
            new_cls._schema = schema
            if not hasattr(schema, "object"):
                schema.object = {}
            schema.object[cls] = new_cls
        else:
            new_cls = super().__new__(metacls, cls, bases, classdict)
        globals()[cls] = new_cls
        return new_cls


class EnumTemplate(Enum, metaclass=EnumMetaTemplate):
    def __init__(self, value=None):
        if not value:
            self._value_ = str(self.name)
        else:
            self._value_ = value

    def __str__(self):
        return self._value_

    @classmethod
    def _to_dict(cls):
        result = {"@type": "Enum", "@id": cls.__name__, "@value": []}
        for item in cls.__members__:
            if item[0] != "_":
                result["@value"].append(str(eval(f"cls.{item}")))  # noqa: S307
        # if hasattr(self, "__annotations__"):
        #     for attr, attr_type in self.__annotations__.items():
        #         result[attr] = str(attr_type)
        return result


class TaggedUnion(DocumentTemplate):
    pass


class Schema:
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        authors: Optional[List[str]] = None,
        schema_ref=None,
        base_ref=None,
    ):
        self.object = {}
        self._all_existing_classes = {}
        self.title = title
        self.description = description
        self.authors = authors
        self.schema_ref = schema_ref
        self.base_ref = base_ref

    @property
    def context(self):
        if self.title is None:
            title = ""
        else:
            title = self.title
        if self.description is None:
            description = ""
        else:
            description = self.description
        documentation = {"@title": title, "@description": description}
        if self.authors is not None:
            documentation["@authors"] = self.authors
        return {
            "@type": "@context",
            "@documentation": documentation,
            "@schema": self.schema_ref,
            "@base": self.base_ref,
        }

    @context.setter
    def context(self, value):
        raise Exception("Cannot set context")

    def _construct_class(self, class_obj_dict):
        # if the class is already constructed properly
        if (
            class_obj_dict.get("@id")
            and class_obj_dict["@id"] in self.object
            and not isinstance(self.object[class_obj_dict["@id"]], str)
        ):
            return self.object[class_obj_dict["@id"]]
        # if the class is Enum
        if class_obj_dict.get("@type") == "Enum":
            attributedict = _EnumDict()
            attributedict._cls_name = class_obj_dict.get("@id")
        else:
            attributedict = {}
        annotations = {}
        superclasses = []
        inherits = class_obj_dict.get("@inherits")
        if inherits:
            if isinstance(inherits, str):
                inherits = [inherits]
            for parent in inherits:
                if parent == "TaggedUnion":
                    superclasses.append(TaggedUnion)
                elif parent not in self._all_existing_classes:
                    raise RuntimeError(f"{parent} not exist in database schema")
                else:
                    self._construct_class(self._all_existing_classes[parent])
                    superclasses.append(self.object[parent])
        else:
            inherits = []
        if class_obj_dict.get("@type") == "Class":
            superclasses.append(DocumentTemplate)
        elif class_obj_dict.get("@type") == "Enum":
            superclasses.append(EnumTemplate)
            if class_obj_dict.get("@value"):
                for members in class_obj_dict.get("@value"):
                    attributedict[members.lower().replace(" ", "_")] = members
            else:
                raise RuntimeError(f"{class_obj_dict} not exist in database schema")
        for key, value in class_obj_dict.items():
            if key[0] != "@":
                attributedict[key] = None
                if isinstance(value, str):
                    if value[:4] == "xsd:":
                        annotations[key] = wt.from_woql_type(value)
                    else:
                        if value not in self._all_existing_classes:
                            raise RuntimeError(f"{value} not exist in database schema")
                        elif value not in self.object:
                            self.object[value] = value
                        annotations[key] = self.object[value]
                elif isinstance(value, dict):
                    if value.get("@type") and value.get("@type") == "Set":
                        annotations[key] = Set[
                            wt.from_woql_type(
                                value.get("@class"), skip_convert_error=True
                            )
                        ]
                    elif value.get("@type") and value.get("@type") == "List":
                        annotations[key] = List[
                            wt.from_woql_type(
                                value.get("@class"), skip_convert_error=True
                            )
                        ]
                    elif value.get("@type") and value.get("@type") == "Optional":
                        annotations[key] = Optional[
                            wt.from_woql_type(
                                value.get("@class"), skip_convert_error=True
                            )
                        ]
                    else:
                        raise RuntimeError(
                            f"{value} is not in the right format for TerminusDB type"
                        )
            # when key stars with @
            elif key == "@subdocument":
                attributedict["_subdocument"] = value
            elif key == "@abstract":
                attributedict["_abstract"] = value
            elif key == "@key":
                key_type = value.get("@type")
                if key_type and key_type == "Random":
                    attributedict["_key"] = RandomKey()
                elif key_type and key_type == "ValueHash":
                    attributedict["_key"] = ValueHashKey()
                elif key_type and key_type == "Lexical":
                    attributedict["_key"] = LexicalKey(value.get("@fields"))
                elif key_type and key_type == "Hash":
                    attributedict["_key"] = HashKey(value.get("@fields"))
                else:
                    raise RuntimeError(
                        f"{value} is not in the right format for TerminusDB key"
                    )
            elif key == "@documentation":
                docstring = f'{value["@comment"]}'
                if value.get("@properties"):
                    docstring += "\n\n    Attributes\n    ----------\n"
                    for prop, discription in value["@properties"].items():
                        docstring += f"    {prop} : {wt.from_woql_type(class_obj_dict[prop], skip_convert_error=True, as_str=True)}\n        {discription}\n"
                attributedict["__doc__"] = docstring

        attributedict["__annotations__"] = annotations
        new_class = type(class_obj_dict["@id"], tuple(superclasses), attributedict)
        self.add_obj(class_obj_dict["@id"], new_class)
        return new_class

    def _construct_context(self, context_dict):
        documentation = context_dict.get("@documentation")
        if documentation:
            if documentation.get("@title"):
                self.title = documentation["@title"]
            if documentation.get("@description"):
                self.description = documentation["@description"]
            if documentation.get("@authors"):
                self.authors = documentation["@authors"]
        self.base_ref = context_dict.get("@base")
        self.schema_ref = context_dict.get("@schema")

    def _construct_object(self, obj_dict):
        obj_type = obj_dict.get("@type")
        if obj_type and obj_type not in self.object:
            raise ValueError(
                f"{obj_type} is not in current schema. (Received {obj_dict})"
            )
        type_class = self.object.get(obj_type)
        type_dict = type_class._to_dict()
        params = {}

        def create_obj(type_class, obj_id, params):
            for obj in type_class.get_instances():
                if obj._id == obj_id:
                    for key, value in params.items():
                        setattr(obj, key, value)
                    return obj
            params["_backend_id"] = obj_id
            new_obj = type_class.__new__(type_class)
            new_obj.__init__(new_obj, **params)
            return new_obj

        def convert_if_object(obj_type, value):
            if value is None:
                return None

            if isinstance(obj_type, str) and obj_type[:4] == "xsd:":
                # it's datatype
                if obj_type in [
                    "xsd:dateTime",
                    "xsd:date",
                    "xsd:time",
                    "xsd:duration",
                ]:
                    return wt.datetime_from_woql(value, obj_type)
                return value
            elif isinstance(obj_type, dict):
                # it's List, Set, Optional etc
                if obj_type["@type"] == "Optional":
                    return value
                if isinstance(value, str):
                    value = [value]
                value = [convert_if_object(obj_type["@class"], x) for x in value]
                if obj_type["@type"] == "Set":
                    value = set(value)
                return value
            elif isinstance(obj_type, str):
                value_class = self.object.get(obj_type)
                if not value_class:
                    raise ValueError(f"{obj_type} is not in current schema.")
                if isinstance(value, dict):
                    if hasattr(value_class, "_subdocument"):
                        # it's a subdocument
                        return self._construct_object(value)
                    else:
                        # document is expressed as dict with '@id'
                        value = value.get("@id")
                # it's a document or enum, value is id
                if isinstance(value_class, TerminusClass):
                    return create_obj(value_class, value, {})
                else:
                    the_key = None
                    for key, item in value_class.__members__.items():
                        if item._value_ == value:
                            the_key = key
                    return eval(f"value_class.{the_key}")  # noqa: S307
            else:
                raise ValueError(f"Schema {type_dict} is not correct.")

        for key, value in obj_dict.items():
            if key[0] != "@":
                params[key] = convert_if_object(type_dict[key], value)
            elif key == "@id":
                # params["_id"] = value
                obj_id = value
        # new_obj = type_class.__new__(type_class)
        # new_obj.__init__(new_obj, **params)
        # return new_obj
        return create_obj(type_class, obj_id, params)

    def add_enum_class(self, class_name: str, class_values: list):
        """Construct a TerminusDB Enum class by provideing class name and member values then add into the schema.

        Parameters
        ----------
        class_name: str
            Name of the class object constructed.
        class_values : list
            A list of values in this Enum.

        Returns
        -------
        EnumMetaTemplate
            A Enum object with the sepcified name and members
        """
        attributedict = _EnumDict()
        attributedict._cls_name = class_name
        for value in class_values:
            attributedict[value.lower().replace(" ", "_")] = value
        new_class = type(class_name, (EnumTemplate,), attributedict)
        self.add_obj(class_name, new_class)
        return new_class

    def commit(
        self, client: Client, commit_msg: Optional[str] = None, full_replace=False
    ):
        """Commit the schema to database

        Parameters
        ----------
        client: Client
            A client that is connected to a database.
        commit_msg : str
            Commit message.
        full_replace : bool
            Does the commit fully wiped out the old shcema graph. Default to be False.
        """
        if self.context["@schema"] is None or self.context["@base"] is None:
            prefixes = client._get_prefixes()
            if self.context["@schema"] is None:
                self.schema_ref = prefixes["@schema"]
            if self.context["@base"] is None:
                self.base_ref = prefixes["@base"]
        if commit_msg is None:
            commit_msg = "Schema object insert/ update by Python client."
        if full_replace:
            client.insert_document(
                self, commit_msg=commit_msg, graph_type="schema", full_replace=True
            )
        else:
            client.update_document(
                self,
                commit_msg=commit_msg,
                graph_type="schema",
            )

    def from_db(self, client: Client, select: Optional[List[str]] = None):
        """Load classes in the database schema into schema

        Parameters
        ----------
        client: Client
            Client that is connected to the database
        select: list of str, optional
            The classes (and depended classes) that will be imported, default to None which will import all classes
        """
        all_existing_class_raw = client.get_all_documents(graph_type="schema")
        # clean up and update all_existing_classes
        for item in all_existing_class_raw:
            item_id = item.get("@id")
            if item_id:
                self._all_existing_classes[item_id] = item
            elif item.get("@type") == "@context":
                self._construct_context(item)

        for item_id, class_obj_dict in self._all_existing_classes.items():
            if select is None or (select is not None and item_id in select):
                self._construct_class(class_obj_dict)
        return self

    def import_objects(self, obj_dict: Union[List[dict], dict]):
        """Import a list of documents in json format to Python objects. The schema of those documents need to be in this schema."""
        if isinstance(obj_dict, dict):
            return self._construct_object(obj_dict)
        return list(map(self._construct_object, obj_dict))

    def from_json_schema(
        self,
        name: str,
        json_schema: Union[dict, str, StringIO],
        pipe=False,
        subdoc=False,
    ):
        """Load class object from json schema (http://json-schema.org/) and, if pipe mode is off, add into schema. All referenced object will be treated as subdocuments.

        Parameters
        ----------
        name: str
            Name of the class object.
        json_schema: dict or str or StringIO
            Json Schema in dictionary or jsonisable string format or json file stream.
        pipe: bool
            Pipe mode, if True will return the schema in TerminusDB dictionary format (just like calling to_dict) WITHOUT loading the schema into the schema object. Default to False.
        subdoc: bool
            If not in pipe mode, the class object will be added as a subdocument class.
        """
        if isinstance(json_schema, str):
            json_schema = json.loads(json_schema)
        elif isinstance(json_schema, TextIOWrapper):
            json_schema = json.load(json_schema)

        properties = json_schema.get("properties")
        defs = json_schema.get("$defs")
        if properties is None:
            raise RuntimeError(
                "json_schema not in proper format: 'properties' is missing"
            )

        class_dict = {"@id": name, "@type": "Class"}
        if subdoc:
            class_dict["@subdocument"] = []
        convert_dict = {
            "string": str,
            "integer": int,
            "boolean": bool,
            "number": float,
        }

        def convert_property(prop_name, prop):
            # it's datetime
            if "format" in prop and prop["format"] == "date-time":
                return "xsd:dataTime"
            # it's a subdocument
            elif prop.get("type") is not None and prop["type"] == "object":
                if prop.get("properties") is None:
                    raise RuntimeError(
                        f"subdocument {prop_name} not in proper format: 'properties' is missing"
                    )
                sub_dict = {"@id": prop_name, "@type": "Class", "@subdocument": []}
                for sub_prop_name, sub_prop in prop["properties"].items():
                    sub_dict[sub_prop_name] = convert_property(sub_prop_name, sub_prop)
                if pipe:  # end of journey for pipemode
                    return sub_dict
                self._construct_class(sub_dict)
                return prop_name
            # it's another document
            elif prop.get("type") is None and prop.get("$ref") is not None:
                prop_type = prop["$ref"].split("/")[-1]
                if defs is None or prop_type not in defs:
                    raise RuntimeError(f"{prop_type} not found in defs.")
                if pipe:
                    return self.from_json_schema(prop_type, defs[prop_type], pipe=True)
                else:
                    self.from_json_schema(prop_type, defs[prop_type], subdoc=True)
                    return self.object[prop_type]._to_dict()
            # it's enum
            elif prop.get("type") is None and prop.get("enum") is not None:
                # create enum name from snake case to camal case
                enum_name = prop_name.replace("_", " ").capitalize().replace(" ", "")
                enum_dict = {"@id": enum_name, "@type": "Enum", "@value": prop["enum"]}
                if pipe:
                    return enum_dict
                else:
                    self._construct_class(enum_dict)
                    return self.object[enum_name]._to_dict()
            # it's a List
            elif prop["type"] == "array":
                prop_type = convert_property(prop["items"])
                return {"@type": "List", "@class": prop_type}
            elif isinstance(prop["type"], list):
                prop_type = prop["type"]
                # it's Optional
                if "null" in prop_type:
                    prop_type.remove("null")
                    prop_type = prop_type[0]  # can only have one type
                    # it's list in a 'type' so assume no ref
                    return to_woql_type(Optional.__getitem__(convert_dict[prop_type]))
                # THIS SHOULD BE TaggedUnion
                # elif len(prop_type) > 1:
                #     prop_type = to_woql_type(
                #         Union.__getitem__(*map(lambda x: convert_dict[x], prop_type))
                #     )
                # type is wrapped in a list
                else:
                    return to_woql_type(convert_dict[prop_type[0]])
            else:
                return to_woql_type(convert_dict[prop["type"]])

        for prop_name, prop in properties.items():
            class_dict[prop_name] = convert_property(prop_name, prop)

        if pipe:  # end of journey for pipemode
            return class_dict

        self._construct_class(class_dict)

    def add_obj(self, name, obj):
        self.object[name] = obj

    def all_obj(self):
        return set(self.object.values())

    def to_dict(self):
        """Return the schema in the TerminusDB dictionary format"""
        all_obj = [cls._to_dict() for cls in self.all_obj()]
        all_obj.sort(key=lambda item: item.get("@id"))
        return [self.context] + all_obj

    def to_json_schema(self, class_object: Union[str, dict]):
        """Return the schema in the json schema (http://json-schema.org/) format as a dictionary for the class object.

        Parameters
        ----------
        class object: str or dict
            Name of the class object or the class object represented as dictionary.
        """
        if isinstance(class_object, dict):
            class_dict = class_object
        elif class_object not in self.object.keys():
            raise RuntimeError(f"{class_object} not found in schema.")
        else:
            class_dict = self.object[class_object]._to_dict()
        class_doc = class_dict.get("@documentation")
        if class_doc is not None:
            doc_dict = class_doc.get("@properties")
        else:
            doc_dict = {}
        json_properties = {}
        defs = {}
        for key, item in class_dict.items():
            if key[0] != "@":
                if isinstance(item, str):
                    # datatype properties
                    if item[:4] == "xsd:":
                        if item[4:] == "decimal":
                            json_properties[key] = {"type": "number"}
                        else:
                            json_properties[key] = {"type": item[4:]}
                    # object properties
                    else:
                        if isinstance(class_object, dict):
                            raise RuntimeError(
                                f"{item} not embedded in input. Cannot be created as json schema."
                            )
                        if item == class_object:
                            raise RuntimeError(
                                f"{class_object} depends on itself and created a loop. Cannot be created as json schema."
                            )
                        json_properties[key] = {"$ref": "#/$defs/" + item}
                        defs[item] = self.to_json_schema(item)
                elif isinstance(item, dict):
                    prop_type = item["@type"]
                    # if prop_type is None:
                    #     raise RuntimeError(f"Format of property {key} is not valid.")
                    # obejct properties, subdocument
                    if prop_type == "Class":
                        item_id = item["@id"]
                        # if item_id is None:
                        #     raise RuntimeError(f"Format of property {key} is not valid.")
                        json_properties[key] = {"$ref": "#/$defs/" + item_id}
                        defs[item_id] = self.to_json_schema(item_id)
                    elif prop_type == "Enum":
                        item_id = item["@id"]
                        json_properties[key] = {"enum": item["@value"]}
                    elif prop_type in ["List", "Set", "Optional"]:
                        item = item["@class"]
                        # datatype properties
                        if item[:4] == "xsd:":
                            if item[4:] == "decimal":
                                dtype = "number"
                            else:
                                dtype = item[4:]
                            if prop_type == "Optional":
                                json_properties[key] = {"type": ["null", dtype]}
                            else:
                                json_properties[key] = {
                                    "type": "array",
                                    "items": {"type": dtype},
                                }
                        # object properties
                        else:
                            if isinstance(class_object, dict):
                                raise RuntimeError(
                                    f"{item} not embedded in input. Cannot be created as json schema."
                                )
                            if item == class_object:
                                raise RuntimeError(
                                    f"{class_object} depends on itself and created a loop. Cannot be created as json schema."
                                )
                            json_properties[key] = {
                                "type": "array",
                                "items": {"$ref": "#/$defs/" + item},
                            }
                            defs[item] = self.to_json_schema(item)
            if doc_dict and key in doc_dict:
                json_properties[key]["description"] = doc_dict[key]
        json_properties["id"] = {"type": "string"}
        json_schema = {"type": ["null", "object"], "additionalProperties": False}
        json_schema["properties"] = json_properties
        json_schema["$defs"] = defs
        if class_doc is not None:
            if class_doc.get("@comment"):
                json_schema["description"] = class_doc.get("@comment")
        return json_schema

    def copy(self):
        return deepcopy(self)

WOQLSchema = Schema # noqa
