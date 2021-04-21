from copy import deepcopy

from ..woqlclient.woqlClient import WOQLClient
from .woql_query import WOQLQuery as WQ


class WOQLClass(type):
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)

        if cls.schema is not None:
            if hasattr(cls, "domain"):
                if not hasattr(cls.schema, "property"):
                    cls.schema.property = set()
                cls.schema.property.add(cls)
                # cls.schema.property -= set(bases)  # Remove base classes

            if hasattr(cls, "properties"):
                if not hasattr(cls.schema, "object"):
                    cls.schema.object = set()
                cls.schema.object.add(cls)
                # cls.schema.object -= set(bases)  # Remove base classes

        if hasattr(cls, "domain"):
            for item in cls.domain:
                item.properties.add(cls)

        if hasattr(cls, "properties"):
            for item in cls.properties:
                item.domain.add(cls)

    def __str__(cls):
        if hasattr(cls, "value_set"):
            return (
                cls.__name__ + ", values: " + ", ".join([val for val in cls.value_set])
            )
        if hasattr(cls, "properties"):
            return (
                cls.__name__
                + "has properties: "
                + ", ".join([prop for prop in cls.properties])
            )
        if hasattr(cls, "prop_range"):
            return (
                cls.__name__
                + "has range: "
                + ", ".join([rang for rang in cls.prop_range])
            )
        return cls.__name__


class WOQLObject(metaclass=WOQLClass):
    schema = None
    properties = set()

    def __init__(self):
        pass


class Document(WOQLObject):
    pass


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
            parent_list = parents[obj]
            for parent in parent_list:
                query.append(
                    WQ().add_triple(
                        obj_iri, "rdfs:subClassOf", "scm:" + parent.__name__
                    )
                )
            query.append(
                WQ()
                .add_triple(obj_iri, "rdf:type", WQ().iri("owl:Class"))
                .add_triple(obj_iri, "rdfs:comment", comment)
                .add_triple(obj_iri, "rdfs:label", label)
            )
        for prop in property:
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
                .add_triple(prop_iri, "rdf:type", WQ().iri(prop_type))
                .add_triple(prop_iri, "rdfs:comment", comment)
                .add_triple(prop_iri, "rdfs:label", label)
                .add_tryple(prop_iri, "rdfs:domain", domain)
                .add_tryple(prop_iri, "rdfs:range", prop_range)
            )

        WQ().using(client.db() + "/local/branch/main/schema/main").woql_and(
            *query
        ).execute(client)

    def all_obj(self):
        return self.object

    def all_prop(self):
        return self.property

    def copy(self):
        return deepcopy(self)
