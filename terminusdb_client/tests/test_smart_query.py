from datetime import datetime

from terminusdb_client.woqlquery.smart_query import WOQLClass, WOQLObj

from .ans_doctype import *  # noqa
from .ans_property import *  # noqa


class TestWOQLClass:
    def test_init(
        self,
        doctype_without,
        doctype_with_label,
        doctype_with_des,
        property_without,
        property_with_des,
    ):
        woql_object = WOQLClass("Station")
        woql_object_label = WOQLClass("Station", label="Station Object")
        woql_object_des = WOQLClass(
            "Station", label="Station Object", description="A bike station object."
        )
        woql_object_prop = WOQLClass(
            "Journey", obj_property={"Duration": {"type": "dateTime"}}
        )
        woql_object_prop_des = WOQLClass(
            "Journey",
            obj_property={
                "Duration": {
                    "type": "dateTime",
                    "label": "Journey Duration",
                    "description": "Journey duration in minutes.",
                }
            },
        )
        assert woql_object.to_dict() == doctype_without
        assert woql_object_label.to_dict() == doctype_with_label
        assert woql_object_des.to_dict() == doctype_with_des
        assert woql_object_prop.to_dict() == property_without
        assert woql_object_prop_des.to_dict() == property_with_des

    def test_label(self, doctype_with_label):
        woql_object = WOQLClass("Station")
        assert woql_object.label == ""
        woql_object.label = "Station Object"
        assert woql_object.label == "Station Object"
        assert woql_object.to_dict() == doctype_with_label

    def test_description(self, doctype_with_des):
        woql_object = WOQLClass("Station", label="Station Object")
        assert woql_object.description == ""
        woql_object.description = "A bike station object."
        assert woql_object.description == "A bike station object."
        assert woql_object.to_dict() == doctype_with_des

    def test_add_datatype_property(self, property_without, property_with_des):
        woql_object = WOQLClass("Journey")
        woql_object.add_property("Duration", "dateTime")
        assert woql_object.to_dict() == property_without

        woql_object = WOQLClass("Journey")
        woql_object.add_property(
            "Duration",
            "dateTime",
            label="Journey Duration",
            description="Journey duration in minutes.",
        )
        assert woql_object.to_dict() == property_with_des

    def test_add_object_property(self, obj_property_without):
        station_obj = WOQLClass("Station")
        woql_object = WOQLClass("Journey")
        woql_object.add_property("start_station", station_obj)
        assert woql_object.to_dict() == obj_property_without


class TestWOQLObj:
    def test_init_int_prop(self):
        my_id = "my_journey"
        my_label = "My Journey"
        my_des = "This is my journey to work"
        my_prop = {"Duration": {"value": 30}}
        journey_class = WOQLClass("Journey")
        journey_class.add_property(
            "Duration",
            "integer",
            label="Journey Duration",
            description="Journey duration in minutes.",
        )
        woql_obj = WOQLObj(my_id, journey_class, my_label, my_des, obj_property=my_prop)

        assert woql_obj.id == my_id
        assert woql_obj.label == my_label
        assert woql_obj.description == my_des
        assert woql_obj._type == journey_class
        assert woql_obj._property == my_prop

        def test_init_dt_prop(self):
            my_id = "my_journey"
            my_label = "My Journey"
            my_des = "This is my journey to work"
            my_prop = {"Duration": {"value": datetime("2020-08-08")}}
            journey_class = WOQLClass("Journey")
            journey_class.add_property(
                "Duration",
                "dateTime",
                label="Journey Duration",
                description="Journey duration in minutes.",
            )
            woql_obj = WOQLObj(
                my_id, journey_class, my_label, my_des, obj_property=my_prop
            )

            assert woql_obj.id == my_id
            assert woql_obj.label == my_label
            assert woql_obj.description == my_des
            assert woql_obj._type == journey_class
            assert woql_obj._property == my_prop

    def test_idgen(self):
        journey_class = WOQLClass("Journey")
        woql_obj = WOQLObj("my_journey", journey_class)
        assert woql_obj.woql_id == "doc:Journey_my_journey"

    def test_idgen_quote(self):
        journey_class = WOQLClass("My Journey")
        woql_obj = WOQLObj("my journey", journey_class)
        assert woql_obj.woql_id == "doc:My%20Journey_my%20journey"
