from copy import copy, deepcopy
from enum import Enum, EnumMeta, _EnumDict
from hashlib import sha256
from typing import List, Optional, Set, Union
from urllib.parse import quote
from uuid import uuid4

from numpydoc.docscrape import ClassDoc
from typeguard import check_type

from .. import woql_type as wt
from ..woql_type import CONVERT_TYPE
from ..woqlclient.woqlClient import WOQLClient


class TerminusKey:
    def __init__(self, keys: Union[str, list, None] = None):
        if keys is not None:
            self._keys = keys

    def _idgen_prep(self, obj: Union["DocumentTemplate", dict]):
        """Helper function to prepare prefix and key_list for idgen to use."""
        key_list = []
        if hasattr(self, "_keys"):
            for item in self._keys:
                if hasattr(obj, item):
                    key_item = eval(f"obj.{item}")  # noqa: S307
                elif isinstance(obj, dict) and obj.get(item) is not None:
                    key_item = obj.get(item)
                else:
                    raise ValueError(f"Cannot get {item} from {obj}")

                if isinstance(key_item, tuple(CONVERT_TYPE.keys())):
                    key_list.append(str(key_item))
                else:
                    raise ValueError("Keys need to be datatype object")

        if isinstance(obj, dict) and obj.get("@type") is not None:
            prefix = obj.get("@type") + "_"
        elif hasattr(obj.__class__, "_base"):
            prefix = obj.__class__._base + "_"
        elif hasattr(obj.__class__, "__name__"):
            prefix = obj.__class__.__name__ + "_"
        else:
            raise ValueError(f"Cannot determine prefix from {obj}")
        return prefix, key_list


class HashKey(TerminusKey):
    """Generating ID with SHA256 using provided keys"""

    at_type = "Hash"

    def idgen(self, obj: Union["DocumentTemplate", dict]):
        prefix, key_list = self._idgen_prep(obj)
        return prefix + sha256((quote("_".join(key_list))).encode("utf-8")).hexdigest()


class LexicalKey(TerminusKey):
    """Generating ID with urllib.parse.quote using provided keys"""

    at_type = "Lexical"

    def idgen(self, obj: Union["DocumentTemplate", dict]):
        prefix, key_list = self._idgen_prep(obj)
        return prefix + quote("_".join(key_list))


class ValueHashKey(TerminusKey):
    """Generating ID with SHA256"""

    at_type = "ValueHash"

    def __init__(self):
        raise RuntimeError("ValueHashKey is not avaliable yet.")

    # TODO: idgen


class RandomKey(TerminusKey):
    """Generating ID with UUID4"""

    at_type = "Random"

    def idgen(self, obj: Union["DocumentTemplate", dict]):
        prefix, _ = self._idgen_prep(obj)
        return prefix + uuid4().hex


def _check_cycling(class_obj: "TerminusClass"):
    """Helper function to check if the embedded subdocument is cycling"""
    if hasattr(class_obj, "_subdocument"):
        mro_names = list(map(lambda obj: obj.__name__, class_obj.__mro__))
        for prop_type in class_obj._annotations.values():
            if str(prop_type) in mro_names:
                raise RecursionError(f"Embbding {prop_type} cause recursions.")


def _check_missing_prop(doc_obj: "DocumentTemplate"):
    """Helper function to check if the the document is missing properties (and if they are right types)"""
    class_obj = doc_obj.__class__
    for prop, prop_type in class_obj._annotations.items():
        try:
            check_type(str(None), None, prop_type)
        except TypeError:
            if not hasattr(doc_obj, prop):
                raise ValueError(f"{doc_obj} missing property: {prop}")
            else:
                prop_value = eval(f"doc_obj.{prop}")  # noqa: S307
                check_type(prop, prop_value, prop_type)
                # raise TypeError(f"Property of {doc_obj} missing should be type {prop_type} but got {prop_value} which is {type(prop_value)}")


class TerminusClass(type):
    def __init__(cls, name, bases, nmspc):

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
        if hasattr(cls, "_abstract"):
            if isinstance(cls._abstract, bool):
                abstract = cls._abstract
            else:
                abstract = True

        def init(obj, *args, **kwargs):
            if abstract:
                raise TypeError(f"{name} is an abstract class.")
            for key in cls._annotations:
                if key in kwargs:
                    value = kwargs[key]
                else:
                    value = None
                setattr(obj, key, value)
            if (
                not hasattr(obj, "_subdocument")
                and hasattr(obj, "_key")
                and hasattr(obj._key, "idgen")
            ):
                obj._id = obj._key.idgen(obj)
            obj._isinstance = True
            obj._annotations = cls._annotations

        cls.__init__ = init

        if cls._schema is not None:
            if not hasattr(cls._schema, "object"):
                cls._schema.object = {}
            cls._schema.add_obj(name, cls)

        # super().__init__(name, bases, nmspc)
        globals()[name] = cls

    def __repr__(cls):
        return cls.__name__


class DocumentTemplate(metaclass=TerminusClass):
    _schema = None
    _key = RandomKey()  # default key

    def __setattr__(self, name, value):
        if name[0] != "_" and value is not None:
            correct_type = self._annotations.get(name)
            check_type(str(value), value, correct_type)
            # if not correct_type or not check_type(str(value), value, correct_type):
            #     raise AttributeError(f"{value} is not type {correct_type}")
        super().__setattr__(name, value)

    @classmethod
    def _to_dict(cls, skip_checking=False):
        if not skip_checking:
            _check_cycling(cls)
        result = {"@type": "Class", "@id": cls.__name__}
        if cls.__base__.__name__ != "DocumentTemplate":
            # result["@inherits"] = cls.__base__.__name__
            parents = list(map(lambda x: x.__name__, cls.__mro__))
            result["@inherits"] = parents[1 : parents.index("DocumentTemplate")]
        elif cls.__base__.__name__ == "TaggedUnion":
            result["@type"] = "TaggedUnion"

        if cls.__doc__:
            doc_obj = ClassDoc(cls)
            result["@documentation"] = {
                "@comment": "\n".join(doc_obj["Summary"] + doc_obj["Extended Summary"]),
                "@properties": {
                    thing.name: "\n".join(thing.desc) for thing in doc_obj["Attributes"]
                },
            }

        if hasattr(cls, "_base"):
            result["@base"] = cls._base
        if hasattr(cls, "_subdocument"):
            result["@subdocument"] = cls._subdocument
            result["@key"] = {"@type": "Random"}
        if hasattr(cls, "_abstract"):
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

    def _embeded_rep(self):
        """get representation for embedding as object property"""
        if hasattr(self.__class__, "_subdocument"):
            return self._obj_to_dict()
        elif hasattr(self, "_id"):
            return {"@id": self._id, "@type": "@id"}

    def _obj_to_dict(self, skip_checking=False):
        if not skip_checking:
            _check_missing_prop(self)
        result = {"@type": str(self.__class__)}
        if hasattr(self, "_id"):
            result["@id"] = self._id
        # elif hasattr(self.__class__, "_key") and hasattr(self.__class__._key, "idgen"):
        #     result["@id"] = self.__class__._key.idgen(self)

        for item in self._annotations.keys():
            if hasattr(self, item):
                the_item = eval(f"self.{item}")  # noqa: S307
                if the_item is not None:
                    # object properties
                    if hasattr(the_item, "_embeded_rep"):
                        result[item] = the_item._embeded_rep()
                    # handle list and set (set end up passing as list for jsonlize)
                    elif isinstance(the_item, (list, set)):
                        new_item = []
                        for sub_item in the_item:
                            # inner is object properties
                            if hasattr(sub_item, "_embeded_rep"):
                                new_item.append(sub_item._embeded_rep())
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
                            result[item] = the_item
        return result


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


class WOQLSchema:
    def __init__(self):
        self.object = {}

    def commit(self, client: WOQLClient, commit_msg: Optional[str] = None):
        if commit_msg is None:
            commit_msg = "Schema object insert/ update by Python client."
        client.update_document(
            self,
            commit_msg=commit_msg,
            graph_type="schema",
        )

    def sync_wth_db(self, client: WOQLClient):
        """Add all the classes in the database shcema in the global namespace"""
        all_existing_class_raw = client.get_all_documents(graph_type="schema")
        # clean up and make a dict
        all_existing_class = {}
        for item in all_existing_class_raw:
            if item.get("@id"):
                all_existing_class[item["@id"]] = item

        def contruct_class(class_obj_dict):
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
                    elif parent not in all_existing_class:
                        raise RuntimeError(f"{parent} not exist in database schema")
                    else:
                        contruct_class(all_existing_class[parent])
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
                    raise RuntimeError(f"{value} not exist in database schema")
            for key, value in class_obj_dict.items():
                if key[0] != "@":
                    attributedict[key] = None
                    if isinstance(value, str):
                        if value[:4] == "xsd:":
                            annotations[key] = wt.from_woql_type(value)
                        else:
                            if value not in all_existing_class:
                                raise RuntimeError(
                                    f"{value} not exist in database schema"
                                )
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

        for _, class_obj_dict in all_existing_class.items():
            contruct_class(class_obj_dict)

    def add_obj(self, name, obj):
        self.object[name] = obj

    def all_obj(self):
        return set(self.object.values())

    def to_dict(self):
        return list(map(lambda cls: cls._to_dict(), self.all_obj()))

    def copy(self):
        return deepcopy(self)
