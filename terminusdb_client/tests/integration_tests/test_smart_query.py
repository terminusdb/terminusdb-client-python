import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.smart_query import TerminusDB

test_url = 'http://127.0.0.1:6363'

def test_main_service_run():
    result = requests.get(test_url)
    assert result.status_code == 200

def test_init_terminusdb():
    db = TerminusDB(test_url, "test")
    print(db._client.db("test"))
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
