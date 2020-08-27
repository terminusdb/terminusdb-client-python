import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.smart_query import TerminusDB


@pytest.fixture(scope="module")
def main_app_url(session_scoped_container_getter):
    """ Wait for the api to become responsive """
    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    request_session.mount("http://", HTTPAdapter(max_retries=retries))
    service = session_scoped_container_getter.get("terminusdb-server").network_info[0]
    api_url = f"http://{service.hostname}:{service.host_port}"
    #assert request_session.get(api_url)
    return api_url #f"http://127.0.0.1:{service.host_port}"

def test_main_service_run(main_app_url):
    result = requests.get(main_app_url)
    assert result.status_code == 200

def test_init_terminusdb(main_app_url):
    db = TerminusDB(main_app_url, "test")
    print(main_app_url)
    print(db._client.db("test"))
    #assert False
    assert db is not None


# @pytest.fixture(scope="module")
# def admin_url(module_scoped_container_getter):
#     """ Wait for the api from fastapi_main_app_admin to become responsive """
#     request_session = requests.Session()
#     retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
#     request_session.mount("http://", HTTPAdapter(max_retries=retries))
#
#     service = module_scoped_container_getter.get("fastapi_main_app_admin").network_info[0]
#     api_url = f"http://{service.hostname}:{service.host_port}/admin"
#     return api_url
