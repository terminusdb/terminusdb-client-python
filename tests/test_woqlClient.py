import json

# import sys
# sys.path.append('woqlclient')
import unittest.mock as mock

import requests
from mockResponse import mocked_requests
from woqlclient import WOQLClient

# def test_realCall():
# resp=WOQLClient.directDeleteDatabase("http://localhost:6363/test0009","root")
# print('test_realCall',resp)


def mock_func_with_1arg(_):
    return True


def mock_func_no_arg():
    return True


def test_connection_error():
    # this test is weird
    WOQLClient()
    print("___MOCKED______", mocked_requests("http://...").status_code)

    # raises a connection error no requests mock
    # with pytest.raises(requests.exceptions.ConnectionError):
    # __woql_client__.connect("https://testServer.com",'mykey')


@mock.patch("requests.get", side_effect=mocked_requests)
def test_direct_connect(mocked_requests):
    WOQLClient.directConnect("http://localhost:6363", "mykey")


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connection(mocked_requests, monkeypatch):

    __woql_client__ = WOQLClient()

    __woql_client__.connect("http://localhost:6363", "mykey")

    with open("tests/connectionDictionary.json") as json_file:
        dict_test = json.load(json_file)
        monkeypatch.setattr(__woql_client__.conCapabilities, "connection", dict_test)
        assert dict_test == __woql_client__.conCapabilities.connection


@mock.patch("requests.get", side_effect=mocked_requests)
def test_create_database_connect_mode(mocked_requests):
    __woql_client__ = WOQLClient(server="http://localhost:6363", key="mykey")

    __woql_client__.connect()
    requests.get.assert_called_once_with(
        "http://localhost:6363/", headers={"Authorization": "Basic Om15a2V5"}
    )


"""
    #I use the current server

    #with mocker.patch('requests.post', side_effect=mockResponse.mocked_requests):

    #with pytest.raises(requests.exceptions.ConnectionError):
    #__woql_client__.createDatabase("myFirstTerminusDB",'my first db')
"""


@mock.patch("requests.post", side_effect=mocked_requests)
def test_direct_create_database(mocked_requests):

    WOQLClient.directCreateDatabase(
        "http://localhost:6363/myFirstTerminusDB",
        "my first terminusDB",
        "mykey",
        comment="test terminusDB",
    )


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


# http://localhost:6363/myFirstTerminusDB/schema
