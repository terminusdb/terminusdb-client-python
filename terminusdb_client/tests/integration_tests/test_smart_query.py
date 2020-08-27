import pytest
import requests
import subprocess
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from terminusdb_client.woqlquery.smart_query import TerminusDB


@pytest.fixture(scope="module")
def docker_url(pytestconfig):
    # we are using subprocess in case we need to access some of the outputs
    # most likely
    docker_compose_path = pytestconfig.getoption("docker_compose")
    subprocess.run(["docker-compose", "--file",  f"{docker_compose_path}", "up", "-d"], check=True)
    # is_server_started = False
    #
    # # while not is_server_started:
    # #     service = subprocess.run(["docker-compose", "--file",  f"{docker_compose_path}", "ps", "--services", "--filter",
    # #                               "status=running", "|", "grep", "terminusdb-server"]
    # #                              , stdout=subprocess.PIPE, check=True)
    # #     print(service.stdout)
    # #     is_server_started = True
    test_url = 'http://127.0.0.1:6363'
    yield test_url
    subprocess.run(["docker-compose", "down"])


def test_main_service_run(docker_url):
    print(docker_url)
    result = requests.get(docker_url)
    assert result.status_code == 200


def test_init_terminusdb(docker_url):
    db = TerminusDB(docker_url, "test")
    print(db._client.db("test"))
    assert db is not None




# @pytest.fixture(scope="module")
# def admin_url(config):
#     print(config)
#     """ Wait for the api from fastapi_main_app_admin to become responsive """
#     # request_session = requests.Session()
#     # retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
#     # request_session.mount("http://", HTTPAdapter(max_retries=retries))
#     #
#     # service = module_scoped_container_getter.get("fastapi_main_app_admin").network_info[0]
#     # api_url = f"http://{service.hostname}:{service.host_port}/admin"

