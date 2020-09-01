import os
import subprocess

import pytest
import requests

from terminusdb_client.woqlquery.smart_query import WOQLClass, WOQLObj, TerminusDB
from terminusdb_client.woqlquery.woql_library import WOQLLib

from .ans_test_db import *  # noqa

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
    # is_server_started = False
    #
    # # while not is_server_started:
    # #     service = subprocess.run(["docker-compose", "--file",  f"{docker_compose_path}", "ps", "--services", "--filter",
    # #                               "status=running", "|", "grep", "terminusdb-server"]
    # #                              , stdout=subprocess.PIPE, check=True)
    # #     print(service.stdout)
    # #     is_server_started = True
    test_url = "http://127.0.0.1:6363"
    yield test_url
    subprocess.run(["docker-compose", "down"])


def test_main_service_run(docker_url):
    result = requests.get(docker_url)
    assert result.status_code == 200


def test_init_terminusdb(docker_url):
    db = TerminusDB(docker_url, "test")
    assert db._client.db("test") == "test"

def test_add_class(docker_url, one_class_obj):
    db = TerminusDB(docker_url, "test")
    my_class = WOQLClass(
        "Journey", label="Bike Journey", description="Bike Journey object that capture each bike joourney."
    )
    db.add_class(my_class)
    print(db.run(WOQLLib().classes()))
    assert db.run(WOQLLib().classes()) == one_class_obj

def add_obj(docker_url, one_class_obj):
    # should be after test_add_class
    db = TerminusDB(docker_url, "test")
    assert db.run(WOQLLib().classes()) == one_class_obj
