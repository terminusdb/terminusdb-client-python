import sys
sys.path.append('woqlclient')

from  connectionConfig import ConnectionConfig
from  connectionCapabilities import ConnectionCapabilities
import pytest
import json

def test_connectionCapabilities_noParameter():
	conConfig=ConnectionConfig()
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')
	
	"""
	  set a key without server return False
	"""
	conCapabilities.getClientKey()==False
	assert conCapabilities.serverConnected() == False


def test_addConnection():
	"""
	  No server url in intialization
	"""
	conConfig=ConnectionConfig({"server":"http://localhost:6363"})
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')

	assert ({"http://localhost:6363/":{'key':"mykey"}}==conCapabilities.connection)==True

	with open('tests/capabilitiesResponse.json') as json_file:
		capResponse = json.load(json_file)
		conCapabilities.addConnection(capResponse);

	with open ('tests/connectionDictionary.json') as json_file:
		dictTest = json.load(json_file)
		assert (dictTest==conCapabilities.connection) ==True
		"""
		  you have setServer or the serverConnected is False
		"""
	assert conCapabilities.serverConnected() == True
	assert conCapabilities.getClientKey()=="mykey"


def test_set_getClientKey():
	conConfig=ConnectionConfig({"server":"http://localhost:6363"})
	conCapabilities=ConnectionCapabilities(conConfig)

	conCapabilities.setClientKey("mykey")
	serverURL=conConfig.serverURL;

	assert conCapabilities.getClientKey(serverURL) =="mykey"
	assert conCapabilities.getClientKey("http://testServer") ==False


def test_capabilitiesPermit():
	
	self.connection.capabilitiesPermit(action);	


