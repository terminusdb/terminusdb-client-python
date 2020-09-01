import subprocess
import os

import pytest
import requests
from terminusdb_client.woqlquery.smart_query import TerminusDB


@pytest.fixture(scope="module")
def docker_url(pytestconfig):
    # we are using subprocess in case we need to access some of the outputs
    # most likely
    docker_compose_path = pytestconfig.getoption("docker_compose")
    output = subprocess.run(
        ["docker-compose", "--file", docker_compose_path, "up", "-d"],
        stderr=subprocess.PIPE
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

    print(db._client.db("test"))
    assert db is not None
