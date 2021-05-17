from copy import deepcopy
from enum import Enum
from typing import Optional

from .. import woql_type as wt
from ..woqlclient.woqlClient import WOQLClient
from .woql_query import WOQLQuery as WQ

# from typeguard import check_type


class TerminusClass(type):
    def __init__(cls, name, bases, nmspc):
        if "__annotations__" in nmspc:
            annotations = nmspc["__annotations__"]
            cls.__init__

            def init(obj, *args, **kwargs):
                for key in annotations:
                    if key in kwargs:
                        value = kwargs[key]
                        # ty = annotations[key]
                        # if type(ty) == _GenericAlias:
                        #     try:
                        #         check_type('value',value,ty)
                        #     except TypeError as e:
                        #         message = f"Bad type for member: '{key}' with value '{value}' because " + e.__str__()
                        #         raise TypeError(message)
                        # elif isinstance(value,ty):
                        #     pass
                        # else:
                        #     raise TypeError(f"Bad type for member: '{key}' with value '{value}' and type '{ty.__name__}'")
                    else:
                        value = None
                    setattr(obj, key, value)
                obj.annotations = annotations

            cls.__init__ = init

        if cls._schema is not None:
            if not hasattr(cls._schema, "object"):
                cls._schema.object = set()
            cls._schema.object.add(cls)

        super().__init__(name, bases, nmspc)

    def __repr__(cls):
        return cls.__name__

    def to_dict(cls):
        result = {"@type": cls.__base__.__name__, "@id": cls.__name__}
        if result["@type"] == "ObjectTemplate":
            result["@type"] = "Object"
        elif result["@type"] == "DocumentTemplate":
            result["@type"] = "Document"
        if hasattr(cls, "__annotations__"):
            for attr, attr_type in cls.__annotations__.items():
                result[attr] = wt.convert_type(attr_type)
        return result


class ObjectTemplate(metaclass=TerminusClass):
    _schema = None

    def __init__(self):
        pass


class DocumentTemplate(ObjectTemplate):
    _is_doc = True


class EnumTemplate(Enum):
    # def __new__(cls, *args):
    #     if args:
    #         value = args[0]
    #         if not hasattr(value, "object"):
    #             value.object = set()
    #         value.object.add(cls)
    #         return None
    #     obj = object.__new__(cls)
    #     obj._value_ = obj.name
    #     return obj
    def __init__(self, value=None):
        if self.name == "_schema":
            if not hasattr(value, "object"):
                value.object = set()
            value.object.add(self.__class__)
        elif not value:
            self._value_ = self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"

    @classmethod
    def to_dict(cls):
        result = {"@type": "Enum", "@id": cls.__name__}
        # if hasattr(self, "__annotations__"):
        #     for attr, attr_type in self.__annotations__.items():
        #         result[attr] = str(attr_type)
        return result


class WOQLSchema:
    def __init__(self):
        pass

    def commit(self, client: WOQLClient, commit_msg: Optional[str] = None):
        (
            WQ().quad("v:x", "v:y", "v:z", "schema")
            + WQ().delete_quad("v:x", "v:y", "v:z", "schema")
        ).execute(client)
        query = []
        parents = {}
        for obj in self.object:
            for sub in obj.__subclasses__():
                if sub in parents:
                    parents[sub].append(obj)
                else:
                    parents[sub] = [obj]

        for obj in self.object:
            comment = obj.__doc__ if obj.__doc__ else ""
            label = obj.__name__
            obj_iri = "scm:" + label
            if obj in parents:
                parent_list = parents[obj]
                for parent in parent_list:
                    query.append(
                        WQ().add_quad(
                            obj_iri,
                            "rdfs:subClassOf",
                            "scm:" + parent.__name__,
                            "schema",
                        )
                    )
            if hasattr(obj, "is_doc"):
                query.append(
                    WQ().add_quad(
                        obj_iri, "rdfs:subClassOf", "terminus:Document", "schema"
                    )
                )
            elif hasattr(obj, "value_set"):
                choice_list = list(map(lambda x: "doc:" + x, obj.value_set))
                query.append(
                    WQ().generate_choice_list(
                        "scm:" + obj.__name__, choices=choice_list, graph="schema"
                    )
                )

            query.append(
                WQ()
                .add_quad(obj_iri, "rdf:type", WQ().iri("owl:Class"), "schema")
                .add_quad(obj_iri, "rdfs:comment", comment, "schema")
                .add_quad(obj_iri, "rdfs:label", label, "schema")
            )
        for prop in self.property:
            comment = prop.__doc__ if prop.__doc__ else ""
            label = prop.__name__
            prop_iri = "scm:" + label
            domain = "scm:" + prop.domain.__name__
            if isinstance(prop.prop_range, str):
                prop_range = prop.prop_range
                prop_type = "owl:DatatypeProperty"
            else:
                prop_range = "scm:" + prop.prop_range.__name__
                prop_type = "owl:ObjectProperty"
            query.append(
                WQ()
                .add_quad(prop_iri, "rdf:type", WQ().iri(prop_type), "schema")
                .add_quad(prop_iri, "rdfs:comment", comment, "schema")
                .add_quad(prop_iri, "rdfs:label", label, "schema")
                .add_quad(prop_iri, "rdfs:domain", domain, "schema")
                .add_quad(prop_iri, "rdfs:range", prop_range, "schema")
            )
        WQ().woql_and(*query)._context({"_": "_:"}).execute(client, commit_msg)

    def all_obj(self):
        return self.object

    def to_dict(self):
        return list(map(lambda cls: cls.to_dict(), self.object))

    def copy(self):
        return deepcopy(self)
