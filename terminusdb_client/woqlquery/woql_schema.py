from copy import deepcopy

from ..woqlclient.woqlClient import WOQLClient


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
    domain = set()
    prop_range = set()
    cardinality = None


class WOQLSchema:
    def __init__(self):
        pass

    def commit(self, client: WOQLClient):
        pass

    def all_obj(self):
        return iter(self.object)

    def all_prop(self):
        return iter(self.property)

    def copy(self):
        return deepcopy(self)
