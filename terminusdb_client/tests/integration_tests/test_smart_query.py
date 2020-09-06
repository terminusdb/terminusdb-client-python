import os
import subprocess
import time

import pytest
import requests

from terminusdb_client.woqlquery.smart_query import TerminusDB

MAX_CONTAINER_STARTUP_TIME = 30


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
        stderr=subprocess.PIPE
    )
    if output.returncode != 0:
        raise RuntimeError(output.stderr)

    test_url = "http://127.0.0.1:6363"
    is_server_started = False

    seconds_waited = 0
    while not is_server_started:
        service = subprocess.run(
            ["docker-compose", "--file", os.path.dirname(os.path.realpath(__file__)) + "/test-docker-compose.yml", "ps",
             "--services", "--filter",
             "status=running"]
            , stdout=subprocess.PIPE, check=True)

        if service.stdout == b'terminusdb-server\n':
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
    subprocess.run(["docker-compose",
                    "--file",
                    os.path.dirname(os.path.realpath(__file__)) + "/test-docker-compose.yml", "down"], check=True)
    subprocess.run(["docker-compose",
                    "--file",
                    os.path.dirname(os.path.realpath(__file__)) + "/test-docker-compose.yml", "rm", "--force", "--stop",
                    "-v"], check=True)


def test_main_service_run(docker_url):
    result = requests.get(docker_url)
    assert result.status_code == 200


def test_init_terminusdb(docker_url):
    db = TerminusDB(docker_url, "test")

    print(db._client.db("test"))
    assert db is not None
