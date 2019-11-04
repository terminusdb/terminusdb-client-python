import pytest
import requests
#import sys
#sys.path.append('woqlclient')
import mockResponse
import json

from woqlClient import WOQLClient

#def test_realCall():
	#resp=WOQLClient.directDeleteDatabase("http://localhost:6363/test0009","root")
	#print('test_realCall',resp)

def test_ConnectionError():
	__woqlClient__= WOQLClient()
	
	#raises a connection error no requests mock
	with pytest.raises(requests.exceptions.ConnectionError):
		__woqlClient__.connect("https://testServer.com",'mykey')

def test_DirectConnect(mocker):
	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		WOQLClient.directConnect("http://localhost:6363","mykey")


def test_Connection(mocker):
	__woqlClient__= WOQLClient()
	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		__woqlClient__.connect("http://localhost:6363",'mykey')

	with open ('src/tests/connectionDictionary.json') as json_file:
		dictTest = json.load(json_file)
		assert (dictTest==__woqlClient__.conCapabilities.connection) ==True


def test_createDatabaseConnectMode(mocker):
	__woqlClient__= WOQLClient({'server':"http://localhost:6363"
							    ,'key':'mykey'})
	print('__woqlClient__' ,__woqlClient__.conConfig.serverURL)
	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		__woqlClient__.connect();
		requests.get.assert_called_once_with('http://localhost:6363/', headers={'Authorization': 'Basic Om15a2V5'})
"""	
	 I use the current server 
	
	with mocker.patch('requests.post', side_effect=mockResponse.mocked_requests):
		
		#with pytest.raises(requests.exceptions.ConnectionError):
		__woqlClient__.createDatabase("myFirstTerminusDB",'my first db')
"""


def test_directCreateDatabase(mocker):
	with mocker.patch('requests.post', side_effect=mockResponse.mocked_requests):
		WOQLClient.directCreateDatabase("http://localhost:6363/myFirstTerminusDB","my first terminusDB","mykey", comment="test terminusDB")
	

def test_deleteDatabase(mocker):
	__woqlClient__= WOQLClient({"server":"http://localhost:6363",'key':"mykey"})

	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		__woqlClient__.connect()

	with mocker.patch('requests.delete', side_effect=mockResponse.mocked_requests):
		__woqlClient__.deleteDatabase("myFirstTerminusDB")
		requests.delete.assert_called_once_with('http://localhost:6363/myFirstTerminusDB', headers={'Authorization': 'Basic Om15a2V5'})

def test_directDeleteDatabase(mocker):
	with mocker.patch('requests.delete', side_effect=mockResponse.mocked_requests):
		WOQLClient.directDeleteDatabase("http://localhost:6363/myFirstTerminusDB","mykey")
		requests.delete.assert_called_once_with('http://localhost:6363/myFirstTerminusDB', headers={'Authorization': 'Basic Om15a2V5'})

	
def test_getSchema(mocker):
	__woqlClient__= WOQLClient({"server":"http://localhost:6363",'key':"mykey",'db':'myFirstTerminusDB'})

	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		__woqlClient__.connect()

	"""
	 getSchema with no parameter
	"""
	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
 		__woqlClient__.getSchema()
 		requests.get.assert_called_once_with('http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle', headers={'Authorization': 'Basic Om15a2V5'})

def test_directGetSchema(mocker):
	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		WOQLClient.directGetSchema("http://localhost:6363/myFirstTerminusDB","directCallKey")
		requests.get.assert_called_once_with('http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle', headers={'Authorization': 'Basic OmRpcmVjdENhbGxLZXk='})	






#http://localhost:6363/myFirstTerminusDB/schema



    


