import pytest
import requests
#import sys
#sys.path.append('woqlclient')
import unittest.mock as mock
from .mockResponse import *
import json
import os

from woqlclient import WOQLClient

#def test_realCall():
	#resp=WOQLClient.directDeleteDatabase("http://localhost:6363/test0009","root")
	#print('test_realCall',resp)

def mock_func_with_1arg(_):
	return True

def mock_func_no_arg():
	return True

def test_ConnectionError():
	__woqlClient__= WOQLClient()

	#raises a connection error no requests mock
	with pytest.raises(requests.exceptions.ConnectionError):
		__woqlClient__.connect("https://testServer.com",'mykey')

@mock.patch('requests.get')
def test_DirectConnect(mocked_requests):
	WOQLClient.directConnect("http://localhost:6363","mykey")


@mock.patch('requests.get')
def test_Connection(mocked_requests, monkeypatch):

	__woqlClient__= WOQLClient()

	__woqlClient__.connect("http://localhost:6363",'mykey')

	with open ('connectionDictionary.json') as json_file:
		dictTest = json.load(json_file)
		monkeypatch.setattr(__woqlClient__.conCapabilities, "connection", dictTest)
		assert (dictTest==__woqlClient__.conCapabilities.connection) ==True


@mock.patch('requests.get')
def test_createDatabaseConnectMode(mocked_requests):
	__woqlClient__= WOQLClient({'server':"http://localhost:6363"
							    ,'key':'mykey'})
	print('__woqlClient__' ,__woqlClient__.conConfig.serverURL)

	__woqlClient__.connect();
	requests.get.assert_called_once_with('http://localhost:6363/', headers={'Authorization': 'Basic Om15a2V5'})
"""
	 I use the current server

	with mocker.patch('requests.post', side_effect=mockResponse.mocked_requests):

		#with pytest.raises(requests.exceptions.ConnectionError):
		__woqlClient__.createDatabase("myFirstTerminusDB",'my first db')
"""


@mock.patch('requests.post')
def test_directCreateDatabase(mocked_requests):

	WOQLClient.directCreateDatabase("http://localhost:6363/myFirstTerminusDB","my first terminusDB","mykey", comment="test terminusDB")


@mock.patch('requests.delete')
@mock.patch('requests.get')
def test_deleteDatabase(mocked_requests, mocked_requests2, monkeypatch):
	__woqlClient__= WOQLClient({"server":"http://localhost:6363",'key':"mykey"})

	__woqlClient__.connect()

	monkeypatch.setattr(__woqlClient__.conCapabilities, "capabilitiesPermit", mock_func_with_1arg)

	monkeypatch.setattr(__woqlClient__.conCapabilities, "removeDB", mock_func_no_arg)

	__woqlClient__.deleteDatabase("myFirstTerminusDB")

	requests.delete.assert_called_once_with('http://localhost:6363/myFirstTerminusDB', headers={'Authorization': 'Basic Om15a2V5'})


@mock.patch('requests.delete')
def test_directDeleteDatabase(mocked_requests):

	WOQLClient.directDeleteDatabase("http://localhost:6363/myFirstTerminusDB","mykey")
	requests.delete.assert_called_once_with('http://localhost:6363/myFirstTerminusDB', headers={'Authorization': 'Basic Om15a2V5'})


@mock.patch('requests.get')
def test_getSchema(mocked_requests, monkeypatch):
	__woqlClient__= WOQLClient({"server":"http://localhost:6363",'key':"mykey",'db':'myFirstTerminusDB'})

	__woqlClient__.connect()

	"""
	 getSchema with no parameter
	"""

	monkeypatch.setattr(__woqlClient__.conCapabilities, "capabilitiesPermit", mock_func_with_1arg)

	__woqlClient__.getSchema()

	requests.get.assert_called_with('http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle', headers={'Authorization': 'Basic Om15a2V5'})


@mock.patch('requests.get')
def test_directGetSchema(mocked_requests):

	WOQLClient.directGetSchema("http://localhost:6363/myFirstTerminusDB","directCallKey")
	requests.get.assert_called_once_with('http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle', headers={'Authorization': 'Basic OmRpcmVjdENhbGxLZXk='})






#http://localhost:6363/myFirstTerminusDB/schema
