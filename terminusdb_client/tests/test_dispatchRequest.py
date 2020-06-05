import sys
import unittest.mock as mock

import requests
from connectCapabilitiesResponse import ConnectResponse
from mockResponse import mocked_requests
from woqlclient.api_endpoint_const import APIEndpointConst
from woqlclient.dispatchRequest import DispatchRequest

sys.path.append("woqlclient")


def send_dispatch_request(
    url, action_type, payload={}, basic_auth=None
):  # don't use empty dict as default
    return DispatchRequest.send_request_by_action(url, action_type, payload, basic_auth)


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connect_call(mocked_requests):
    # Assert requests.get calls
    # assert (1 == 2) == True
    response = send_dispatch_request(
        "http://localhost:6363/", APIEndpointConst.CONNECT, None, "admin:mykey"
    )

    requests.get.assert_called_once_with(
        "http://localhost:6363/", headers={"Authorization": "Basic OmFkbWluOm15a2V5"}
    )
    assert response == ConnectResponse


@mock.patch("requests.post", side_effect=mocked_requests)
def test_create_database(mocked_requests):
    full_url = "http://localhost:6363/db/admin/myFirstTerminusDB"

    payload = {
        "label": "my first db",
        "comment": "my first db",
        "prefixes": {
            "scm": "terminus://admin/myFirstTerminusDB/schema#",
            "doc": "terminus://admin/myFirstTerminusDB/data/",
        },
    }
    send_dispatch_request(
        full_url, APIEndpointConst.CREATE_DATABASE, payload, "admin:mykey"
    )
    requests.post.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={
            "Authorization": "Basic OmFkbWluOm15a2V5",
            "content-type": "application/json",
        },
        json={
            "label": "my first db",
            "comment": "my first db",
            "prefixes": {
                "scm": "terminus://admin/myFirstTerminusDB/schema#",
                "doc": "terminus://admin/myFirstTerminusDB/data/",
            },
        },
    )


@mock.patch("requests.delete", side_effect=mocked_requests)
def test_delete_database(mocked_requests):
    full_url = "http://localhost:6363/db/admin/myFirstTerminusDB"
    send_dispatch_request(
        full_url, APIEndpointConst.DELETE_DATABASE, None, "admin:mykey"
    )

    requests.delete.assert_called_once_with(
        "http://localhost:6363/db/admin/myFirstTerminusDB",
        headers={"Authorization": "Basic OmFkbWluOm15a2V5"},
    )
    # print("call_args_list", requests.delete.call_args_list)
