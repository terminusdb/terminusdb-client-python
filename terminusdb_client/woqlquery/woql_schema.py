from copy import deepcopy

from ..woqlclient.woqlClient import WOQLClient
from .woql_query import WOQLQuery as WQ


class WOQLClass(type):
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)

        if cls.schema is not None:
            if hasattr(cls, "domain") and cls.domain is not None:
                print(cls.domain)
                if not hasattr(cls.schema, "property"):
                    cls.schema.property = set()
                cls.schema.property.add(cls)
                if cls.domain.properties is None:
                    cls.domain.properties = set()
                cls.domain.properties.add(cls)
                # cls.schema.property -= set(bases)  # Remove base classes

            if hasattr(cls, "properties"):
                if not hasattr(cls.schema, "object"):
                    cls.schema.object = set()
                cls.schema.object.add(cls)
                if cls.properties:
                    for item in cls.properties:
                        item.domain = cls
                # cls.schema.object -= set(bases)  # Remove base classes

        # if hasattr(cls, "domain") and cls.domain is not None:
        #     cls.domain.properties.add(cls)

        # if hasattr(cls, "properties"):
        #     for item in cls.properties:
        #         item.domain = cls

    def __str__(cls):
        # if hasattr(cls, "value_set"):
        #     return (
        #         cls.__name__ + ", values: " + ", ".join([val for val in cls.value_set])
        #     )
        # if hasattr(cls, "properties"):
        #     return (
        #         cls.__name__
        #         + "has properties: "
        #         + ", ".join([prop for prop in cls.properties])
        #     )
        # if hasattr(cls, "prop_range"):
        #     return cls.__name__ + "has range: " + cls.prop_range
        return cls.__name__


class WOQLObject(metaclass=WOQLClass):
    schema = None
    properties = None

    def __init__(self):
        pass


class Document(WOQLObject):
    is_doc = True


class Enums(WOQLObject):
    value_set = set()


class Property(metaclass=WOQLClass):
    schema = None
    domain = None
    prop_range = None
    cardinality = None


class WOQLSchema:
    def __init__(self):
        pass

    def commit(self, client: WOQLClient):
        query = []
        parents = {}
        for obj in iter(self.object):
            for sub in obj.__subclasses__():
                if sub in parents:
                    parents[sub].append(obj)
                else:
                    parents[sub] = [obj]

        for obj in iter(self.object):
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

            query.append(
                WQ()
                .add_quad(obj_iri, "rdf:type", WQ().iri("owl:Class"), "schema")
                .add_quad(obj_iri, "rdfs:comment", comment, "schema")
                .add_quad(obj_iri, "rdfs:label", label, "schema")
            )
        for prop in iter(self.property):
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

        WQ().woql_and(*query).execute(client)

    def all_obj(self):
        return self.object

    def all_prop(self):
        return self.property

    def copy(self):
        return deepcopy(self)
