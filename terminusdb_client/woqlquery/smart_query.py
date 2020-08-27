from datetime import datetime
from typing import Union, List, Dict
from urllib.parse import quote
from .woql_query import WOQLQuery
from .woql_library import WOQLLib
from ..woqlclient import WOQLClient

WOQLTYPE_TO_PYTYPE = {
"string": str,
"boolean": bool,
"integer": int,
"decimal": float,
"dateTime": datetime
}

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

    def __str__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, WOQLClass):
            return self.id == other.id
        else:
            return False

    @property
    def label(self) -> str:
        if self._label is None:
            return ""
        return self._label

    @label.setter
    def label(self, label:str):
        self.query_obj = self.query_obj.label(label)
        self._label = label

    @property
    def description(self) -> str:
        if self._description is None:
            return ""
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
    def __init__(self, id:str, obj_type:WOQLClass, label:str =None, description:str =None, property:dict = None):
        self.id = id
        self._type = obj_type
        self.woql_id = self._idgen()
        self.label = label
        self.description = description

        if property is not None:
            for pro_id, prop in property.items():
                prop_val = prop.get('value')
                self._check_prop(pro_id, prop_val)
            self._property = property
        else:
            self._property = {}

    def __str__(self):
        return self.id

    def _idgen(self) -> str:
        # mimic what a idgen would do in the back end
        # TODO: quote the ids ot make it url firendly
        return f"doc:{quote(self._type.id)}_{quote(self.id)}"

    def _check_prop(self, pro_id, pro_value):
        prop = self._type._property.get(pro_id)
        if prop is None:
            raise ValueError(f"No {pro_id} property in {self._type.id}")
        if isinstance(pro_value, WOQLObj):
            if pro_value._type != prop['type']:
                raise ValueError(f"{pro_id} property in {self._type.id} is of type {prop['type']} not {pro_value._type}")
        else:
            if not isinstance(pro_value, WOQLTYPE_TO_PYTYPE[prop['type']]):
                raise ValueError(f"{pro_id} property in {self._type.id} is of type {prop['type']} not {type(pro_value)}")

    def add_property(self, pro_id:str, pro_value, label:str =None, description:str =None):
        # check if the pro_value matches the property of the self._type
        self._check_prop(self, pro_id, pro_value)
        # add new prop in self._property
        self._property[pro_id] = {'value': pro_value, 'label': label, 'description': description}
        return self

class TerminusDB:
    def __init__(
        self, server_url:str, db_id:str, key:str ="root", account:str ="admin", user:str ="admin", db_label:str =None, db_description:str =None, **kwargs
        ):

        self._client = WOQLClient(server_url , **kwargs)
        self._client.connect(key=key, account=account, user=user)
        existing = self._client.get_database(db_id, self._client.uid())
        if not existing:
            self._client.create_database(db_id, account, db_label, db_description)
            self.classes: Dict[str, WOQLClass] = {}
        else:
            self._client.db(db_id)
            #get all classes from db and store them
            cls_result = WOQLLib().classes().execute(self._client)
            for item in cls_result['bindings']:
                class_id = item['Class ID'].split('#')[-1]
                class_name = item['Class Name']['@value']
                class_des = item['Description']['@value']
                self.classes['class_id'] = WOQLClass(class_id, class_name, class_des)
            #get all peoperties from db and add to classes
            prop_result = WOQLLib().property().execute(self._client)
            for item in prop_result['bindings']:
                prop_domain = item['Property Domain'].split('#')[-1]
                prop_id = item['Property ID'].split('#')[-1]
                prop_name = item['Property Name']['@value']
                prop_des = item['Property Description']['@value']
                prop_type = item['Property Domain'].split('#')[-1]
                if item['Property Type']['@value'] == 'Object':
                    prop_type = self.classes[prop_type]
                self.classes[prop_domain].add_property(prop_id, prop_type, prop_name, prop_des)


    def add_class(self, obj:Union[WOQLClass,List[WOQLClass]]):
        if isinstance(obj, WOQLClass):
            self.classes[obj.id] = obj
            return obj.query_obj.execute(self._client)
        elif isinstance(obj, list):
            for item in obj:
                self.classes[item.id] = item
            return WOQLQuery().woql_and(*obj).execute(self._client)
        else:
            raise ValueError("object(s) added need to be WOQLClass object or a list of WOQLClass objects.")

    def add_object(self, obj:Union[WOQLObj,List[WOQLObj]]):
        pass
