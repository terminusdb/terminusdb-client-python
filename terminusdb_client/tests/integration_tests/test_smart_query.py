import os
import subprocess
import time
import unittest

import pytest
import requests
from terminusdb_client.woqlquery.smart_query import (
    TerminusDB,
    WOQLClass,
    WOQLLib,
    WOQLObj,
)

MAX_CONTAINER_STARTUP_TIME = 30


def is_docker_installed():
    try:
        output = subprocess.run(["docker", "--version"], stderr=subprocess.PIPE)
    except FileNotFoundError:
        return False
    return output.returncode == 0


pytestmark = pytest.mark.skipif(
    not is_docker_installed(), reason="docker not installed"
)


@pytest.fixture(scope="module")
def docker_url(pytestconfig):
    # we are using subprocess in case we need to access some of the outputs
    # most likely
    pytestconfig.getoption("docker_compose")
    output = subprocess.run(
        [
            "docker-compose",
            "--file",
            os.path.dirname(os.path.realpath(__file__)) + "/test-docker-compose.yml",
            "up",
            "-d",
        ],
        stderr=subprocess.PIPE,
    )
    if output.returncode != 0:
        raise RuntimeError(output.stderr)

    test_url = "http://127.0.0.1:6363"
    is_server_started = False

    seconds_waited = 0
    while not is_server_started:
        service = subprocess.run(
            [
                "docker-compose",
                "--file",
                os.path.dirname(os.path.realpath(__file__))
                + "/test-docker-compose.yml",
                "ps",
                "--services",
                "--filter",
                "status=running",
            ],
            stdout=subprocess.PIPE,
            check=True,
        )

        if service.stdout == b"terminusdb-server\n":
            try:
                response = requests.get(test_url)
                assert response.status_code == 200
                break
            except (requests.exceptions.ConnectionError, AssertionError):
                pass

        seconds_waited += 1
        time.sleep(1)

        if seconds_waited > MAX_CONTAINER_STARTUP_TIME:
            clean_up_container()
            raise RuntimeError("Container was to slow to startup")

    yield test_url
    clean_up_container()


def clean_up_container():
    subprocess.run(
        [
            "docker-compose",
            "--file",
            os.path.dirname(os.path.realpath(__file__)) + "/test-docker-compose.yml",
            "down",
        ],
        check=True,
    )
    subprocess.run(
        [
            "docker-compose",
            "--file",
            os.path.dirname(os.path.realpath(__file__)) + "/test-docker-compose.yml",
            "rm",
            "--force",
            "--stop",
            "-v",
        ],
        check=True,
    )
    subprocess.run(["docker-compose", "down"])
    subprocess.run(["docker-compose", "rm", "--force", "--stop", "-v"])


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
