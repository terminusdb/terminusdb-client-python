import unittest

import requests

from terminusdb_client.woqlquery.smart_query import (
    TerminusDB,
    WOQLClass,
    WOQLLib,
    WOQLObj,
)


def test_main_service_run(docker_url):
    result = requests.get(docker_url)
    assert result.status_code == 200


def test_init_terminusdb(docker_url):
    db = TerminusDB(docker_url, "test")
    assert db._client.db("test") == "test"


def test_add_class_and_object(
    docker_url, one_class_obj, one_class_prop, one_object, one_prop_val
):
    db = TerminusDB(docker_url, "test")
    my_class = WOQLClass(
        "Journey",
        label="Bike Journey",
        description="Bike Journey object that capture each bike joourney.",
    )
    my_class.add_property("Duration", "integer")
    db.add_class(my_class)

    case = unittest.TestCase()
    case.assertCountEqual(db.run(WOQLLib().classes()), one_class_obj)
    case.assertCountEqual(db.run(WOQLLib().property()), one_class_prop)
    # assert db.run(WOQLLib().classes()) == one_class_obj
    # assert db.run(WOQLLib().property()) == one_class_prop

    my_obj = WOQLObj("myobj", my_class)
    my_obj.add_property("Duration", 75)
    db.add_object(my_obj)

    case.assertCountEqual(db.run(WOQLLib().objects()), one_object)
    case.assertCountEqual(db.run(WOQLLib().property_values()), one_prop_val)
    # assert db.run(WOQLLib().objects()) == one_object
    # assert db.run(WOQLLib().property_values()) == one_prop_val
