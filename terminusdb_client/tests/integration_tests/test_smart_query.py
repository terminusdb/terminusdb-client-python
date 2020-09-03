import os
import subprocess

import pytest

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
    subprocess.run(["docker-compose", "rm", "--force", "--stop", "-v"])


#
# def test_main_service_run(docker_url):
#     result = requests.get(docker_url)
#     assert result.status_code == 200
#
#
# def test_init_terminusdb(docker_url):
#     db = TerminusDB(docker_url, "test")
#     assert db._client.db("test") == "test"
#
#
# def test_add_class_and_object(
#     docker_url, one_class_obj, one_class_prop, one_object, one_prop_val
# ):
#     db = TerminusDB(docker_url, "test")
#     my_class = WOQLClass(
#         "Journey",
#         label="Bike Journey",
#         description="Bike Journey object that capture each bike joourney.",
#     )
#     my_class.add_property("Duration", "integer")
#     db.add_class(my_class)
#
#     assert db.run(WOQLLib().classes()) == one_class_obj
#     assert db.run(WOQLLib().property()) == one_class_prop
#
#     my_obj = WOQLObj("myobj", my_class)
#     my_obj.add_property("Duration", 75)
#     db.add_object(my_obj)
#
#     assert db.run(WOQLLib().objects()) == one_object
#     assert db.run(WOQLLib().property_values()) == one_prop_val
