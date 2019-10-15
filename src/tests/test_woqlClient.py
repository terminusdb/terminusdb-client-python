import pytest
import requests
#import sys
#sys.path.append('woqlclient')
import mockResponse
import json

from woqlClient import WOQLClient


"""
@pytest.fixture(scope="function", autouse=True)
def beforeEach():
	print("BEFORE EVERY TEST")
	#initialize empty
	__woqlClient__= WOQLClient()
	print("__woqlClient__")
"""

def test_ConnectionError():
	__woqlClient__= WOQLClient()
	
	#raises a connection error no requests mock
	with pytest.raises(requests.exceptions.ConnectionError):
		__woqlClient__.connect("https://testServer.com",'mykey')

def test_Connection(mocker):
	__woqlClient__= WOQLClient()
	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		__woqlClient__.connect("http://localhost:6363",'mykey')

	with open ('tests/connectionDictionary.json') as json_file:
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

    


