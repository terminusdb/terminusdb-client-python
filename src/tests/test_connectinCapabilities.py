import sys
sys.path.append('woqlclient')

from  connectionConfig import ConnectionConfig
from  connectionCapabilities import ConnectionCapabilities
import pytest
import json
import const
from errors import (AccessDeniedError,InvalidURIError)

def test_connectionCapabilities_noParameter():
	conConfig=ConnectionConfig()
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')
	
	"""
	  set a key without server return False
	"""
	conCapabilities.getClientKey()==False
	assert conCapabilities.serverConnected() == False

	with pytest.raises(InvalidURIError):
		with open('tests/capabilitiesResponse.json') as json_file:
			capResponse = json.load(json_file)
			conCapabilities.addConnection(capResponse);


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
	conConfig=ConnectionConfig({"server":"http://localhost:6363","db":"myFirstTerminusDB"})
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')

	with open('tests/capabilitiesResponseNoAllAction.json') as json_file:
		capResponse = json.load(json_file)
		conCapabilities.addConnection(capResponse)

	"""
	 if the action are not permits the method raise an Exception
	"""
	with pytest.raises(AccessDeniedError):
		conCapabilities.capabilitiesPermit(const.DELETE_DATABASE)

	with pytest.raises(AccessDeniedError):
		conCapabilities.capabilitiesPermit(const.DELETE_DOCUMENT)	

	
	assert conCapabilities.capabilitiesPermit(const.CREATE_DATABASE)==True
	assert conCapabilities.capabilitiesPermit(const.CREATE_DOCUMENT)==True	

def test_deleteDatabaseForTheConnectionList():
	conConfig=ConnectionConfig({"server":"http://localhost:6363","db":"myFirstTerminusDB"})
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')

	with open('tests/capabilitiesResponse.json') as json_file:
		capResponse = json.load(json_file)
		conCapabilities.addConnection(capResponse)

	assert ("doc:myFirstTerminusDB" in conCapabilities.connection["http://localhost:6363/"]) == True

	conCapabilities.removeDB();

	assert ("doc:myFirstTerminusDB" in conCapabilities.connection["http://localhost:6363/"]) == False

