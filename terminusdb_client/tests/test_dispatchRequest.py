import sys
import unittest.mock as mock

import requests
from terminusdb_client.woqlclient.api_endpoint_const import APIEndpointConst
from terminusdb_client.woqlclient.dispatchRequest import DispatchRequest

from .connectCapabilitiesResponse import ConnectResponse
from .mockResponse import mocked_requests

sys.path.append("woqlclient")


def send_dispatch_request(url, action_type, payload=None, basic_auth=None):
    if payload is None:
        payload = {}
    return DispatchRequest.send_request_by_action(url, action_type, payload, basic_auth)


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connect_call(mocked_requests):
    # Assert requests.get calls
    # assert (1 == 2) == True
    response = send_dispatch_request(
        "http://localhost:6363/", APIEndpointConst.CONNECT, None, "admin:root"
    )

    requests.get.assert_called_once_with(
        "http://localhost:6363/",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
    )
    assert response == ConnectResponse


@mock.patch("requests.post", side_effect=mocked_requests)
def test_create_database(mocked_requests):
    full_url = "http://localhost:6363/db/admin/myFirstTerminusDB"

    payload = {
        "label": "my first db",
        "comment": "my first db",
    }
    send_dispatch_request(
        full_url, APIEndpointConst.CREATE_DATABASE, payload, "admin:root"
    )
    requests.post.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={
            "Authorization": "Basic YWRtaW46cm9vdA==",
            "content-type": "application/json",
        },
        verify=False,
        json={"label": "my first db", "comment": "my first db"},
    )


@mock.patch("requests.delete", side_effect=mocked_requests)
def test_delete_database(mocked_requests):
    full_url = "http://localhost:6363/db/admin/myFirstTerminusDB"
    send_dispatch_request(
        full_url, APIEndpointConst.DELETE_DATABASE, None, "admin:root"
    )

    requests.delete.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={"Authorization": "Basic YWRtaW46cm9vdA=="},
        verify=False,
    )
    # print("call_args_list", requests.delete.call_args_list)
