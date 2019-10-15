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

def test_connect(mocker):
	__woqlClient__= WOQLClient()

	
	#raises a connection error no requests mock
	with pytest.raises(requests.exceptions.ConnectionError):
		__woqlClient__.connect("http://localhost:6363",'mykey')


	with mocker.patch('requests.get', side_effect=mockResponse.mocked_requests):
		__woqlClient__.connect("http://localhost:6363",'mykey')

	with open ('tests/connectionDictionary.json') as json_file:
		dictTest = json.load(json_file)
		assert (dictTest==__woqlClient__.conCapabilities.connection) ==True


def test_createDatabase(mocker):
	__woqlClient__= WOQLClient()

	details={
		  "@context": {
		    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
		    "terminus": "http://terminusdb.com/schema/terminus#"
		  },
		  "@type": "terminus:Database",
		  "rdfs:label": {
		    "@language": "en",
		    "@value": "my first test"
		  },
		  "rdfs:comment": {
		    "@language": "en",
		    "@value": "document test"
		  },
		  "terminus:allow_origin": {
		    "@type": "xsd:string",
		    "@value": "*"
		  }
		}

	with mocker.patch('requests.post', side_effect=mockResponse.mocked_requests):
		__woqlClient__.createDatabase("http://localhost:6363/myFirstTerminusDB",details,'mykey');


    


