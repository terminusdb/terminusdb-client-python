import pprint

from terminusdb_client.woqlquery.smart_query import WOQLClass

from .ans_doctype import *  # noqa
from .ans_property import *  # noqa

class TestWOQLClass:
    def test_init(
        self, doctype_without, doctype_with_label, doctype_with_des, property_without, property_with_des
    ):
        woql_object = WOQLClass("Station")
        woql_object_label = WOQLClass("Station", label="Station Object")
        woql_object_des = WOQLClass(
            "Station", label="Station Object", description="A bike station object."
        )
        woql_object_prop = WOQLClass("Journey", property={"Duration": {"type": "dateTime"}})
        woql_object_prop_des = WOQLClass("Journey",
         property={"Duration": {"type": "dateTime",
                                "label": "Journey Duration",
                                "description": "Journey duration in minutes."}
                                }
                                )
        assert woql_object.to_dict() == doctype_without
        assert woql_object_label.to_dict() == doctype_with_label
        assert woql_object_des.to_dict() == doctype_with_des
        assert woql_object_prop.to_dict() == property_without
        assert woql_object_prop_des.to_dict() == property_with_des

    def test_label(
        self, doctype_with_label
    ):
        woql_object = WOQLClass("Station")
        assert woql_object.label == None
        woql_object.label = "Station Object"
        assert woql_object.label == "Station Object"
        assert woql_object.to_dict() ==  doctype_with_label

    def test_description(
        self, doctype_with_des
    ):
        woql_object = WOQLClass("Station", label="Station Object")
        assert woql_object.description == None
        woql_object.description = "A bike station object."
        assert woql_object.description == "A bike station object."
        assert woql_object.to_dict() ==  doctype_with_des

    def test_add_datatype_property(
        self, property_without, property_with_des
    ):
        woql_object = WOQLClass("Journey")
        woql_object.add_property("Duration", "dateTime")
        assert woql_object.to_dict() == property_without

        woql_object = WOQLClass("Journey")
        woql_object.add_property("Duration", "dateTime", label="Journey Duration", description="Journey duration in minutes.")
        assert woql_object.to_dict() == property_with_des

    def test_add_object_property(
        self, obj_property_without
    ):
        station_obj = WOQLClass("Station")
        woql_object = WOQLClass("Journey")
        woql_object.add_property("start_station", station_obj)
        assert woql_object.to_dict() == obj_property_without
