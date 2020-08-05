from typing import Union
from .woql_query import WOQLQuery

class WOQLClass:
    def __init__(self, id:str, label:str =None, description:str =None, property:dict = None):
        self.id = id
        self._label = label
        self._description = description
        if property is not None:
            self._property = property
        else:
            self._property = {}

        self.query_obj = WOQLQuery().doctype(id,
                            label=label,
                            description=description)
        if property is not None:
            for key, item in property.items():
                self.query_obj = self.query_obj.property(key,
                            item.get('type'),
                            item.get('label'),
                            item.get('description'))

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label:str):
        self.query_obj = self.query_obj.label(label)
        self._label = label

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description:str):
        self.query_obj = self.query_obj.description(description)
        self._description = description

    def add_property(self, pro_id:str, property_type: Union[str,'WOQLClass'], label:str =None, description:str =None):
        if isinstance(property_type, str):
            self.query_obj = self.query_obj.property(pro_id, property_type, label, description)
        elif isinstance(property_type, WOQLClass):
            self.query_obj = self.query_obj.property(pro_id, property_type.id, label, description)
        else:
            raise ValueError("property_type needs to be either string or WOQLClass")
        self._property[pro_id] = {'type': property_type, 'label': label, 'description': description}
        return self

    def to_dict(self,):
        return self.query_obj.to_dict()

    def to_json(self):
        return self.query_obj.to_json()


class WOQLObj:
    def __init__(self, id:str, type:WOQLClass, label:str =None, description:str =None):
        self.id = id
        self.label = label
        self.description = description
        self.type = type
