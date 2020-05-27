import json

# import sys
# sys.path.append('woqlclient')
import unittest.mock as mock

import requests
from mockResponse import mocked_requests
from woqlclient import WOQLClient

from connectionObjDump import ConnectionDump

# def test_realCall():
# resp=WOQLClient.directDeleteDatabase("http://localhost:6363/test0009","root")
# print('test_realCall',resp)


def mock_func_with_1arg(_):
    return True


def mock_func_no_arg():
    return True


def test_connection_error():
    # this test is weird
    WOQLClient("http://localhost:6363")
    print("___MOCKED______", mocked_requests("http://...").status_code)

    # raises a connection error no requests mock
    # with pytest.raises(requests.exceptions.ConnectionError):
    # __woql_client__.connect("https://testServer.com",'mykey')


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connection(mocked_requests, monkeypatch):

    __woql_client__ = WOQLClient("http://localhost:6363")

    #before connect it connection is empty
    assert  __woql_client__.conCapabilities.connection == {}
    __woql_client__.connect(key="mykey", account="admin" , user="admin")
    requests.get.assert_called_once_with(
       "http://localhost:6363/", headers={"Authorization": "Basic OmFkbWluOm15a2V5"}
    )
    assert  __woql_client__.conCapabilities.connection == ConnectionDump 


@mock.patch("requests.post", side_effect=mocked_requests)
def test_create_database(mocked_requests):
    __woql_client__ = WOQLClient("http://localhost:6363", user="admin", key="mykey", account="admin")

    __woql_client__.key() == "admin:mykey"
    
    __woql_client__.create_database("myFirstTerminusDB",'my first db')

    #requests.post.assert_called_once_with(
     #  "http://localhost:6363/db/admin/myFirstTerminusDB", headers={"Authorization": "Basic OmFkbWluOm15a2V5"},
      # body={"label":"my first db","comment":"my first db","prefixes":{"scm":"terminus://admin/myFirstTerminusDB/schema#","doc":"terminus://admin/myFirstTerminusDB/data/"}}
    #)

    #with mocker.patch('requests.post', side_effect=mockResponse.mocked_requests):

    #with pytest.raises(requests.exceptions.ConnectionError):
    #
"""



@mock.patch("requests.delete", side_effect=mocked_requests)
@mock.patch("requests.get", side_effect=mocked_requests)
def test_delete_database(mocked_requests, mocked_requests2, monkeypatch):
    __woql_client__ = WOQLClient(server="http://localhost:6363", key="mykey")

    __woql_client__.connect()

    monkeypatch.setattr(
        __woql_client__.conCapabilities, "capabilitiesPermit", mock_func_with_1arg
    )

    monkeypatch.setattr(__woql_client__.conCapabilities, "removeDB", mock_func_no_arg)

    __woql_client__.deleteDatabase("myFirstTerminusDB")

    requests.delete.assert_called_once_with(
        "http://localhost:6363/myFirstTerminusDB",
        headers={"Authorization": "Basic Om15a2V5"},
    )


@mock.patch("requests.delete", side_effect=mocked_requests)
def test_direct_delete_database(mocked_requests):

    WOQLClient.directDeleteDatabase("http://localhost:6363/myFirstTerminusDB", "mykey")
    requests.delete.assert_called_once_with(
        "http://localhost:6363/myFirstTerminusDB",
        headers={"Authorization": "Basic Om15a2V5"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
def test_get_schema(mocked_requests, monkeypatch):
    __woql_client__ = WOQLClient(
        server="http://localhost:6363", key="mykey", db="myFirstTerminusDB"
    )

    __woql_client__.connect()

    # getSchema with no parameter

    monkeypatch.setattr(
        __woql_client__.conCapabilities, "capabilitiesPermit", mock_func_with_1arg
    )

    __woql_client__.getSchema()

    requests.get.assert_called_with(
        "http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle",
        headers={"Authorization": "Basic Om15a2V5"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
def test_direct_get_schema(mocked_requests):

    WOQLClient.directGetSchema(
        "http://localhost:6363/myFirstTerminusDB", "directCallKey"
    )
    requests.get.assert_called_once_with(
        "http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle",
        headers={"Authorization": "Basic OmRpcmVjdENhbGxLZXk="},
    )

"""
# http://localhost:6363/myFirstTerminusDB/schema
