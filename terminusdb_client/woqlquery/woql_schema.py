from ..woqlclient.woqlClient import WOQLClient


class WOQLClass(type):
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        # cls.registry holds all subclasses
        if not hasattr(cls, "registry"):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases)  # Remove base classes

        if hasattr(cls, "domain"):
            for item in cls.domain:
                item.properties.add(cls)

        if hasattr(cls, "properties"):
            for item in cls.properties:
                item.domain.add(cls)

    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])


class WOQLObject(metaclass=WOQLClass):
    properties = set()

    def __init__(self):
        pass


class Document(WOQLObject):
    pass


class Enums(WOQLObject):
    value_set = set()


class Property(metaclass=WOQLClass):
    domain = set()
    prop_range = set()

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        for item in cls.domain:
            item.properties.append(cls)
            print("add domain:", cls.__name__)


class WOQLSchema(list):
    def commit(self, client: WOQLClient):
        for item in self:
            print(item)
