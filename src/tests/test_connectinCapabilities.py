#import sys
#sys.path.append('woqlclient')

from  connectionConfig import ConnectionConfig
from  connectionCapabilities import ConnectionCapabilities
import pytest
import json
import const
from errors import (AccessDeniedError,InvalidURIError,APIError)

def test_connectionCapabilities_noParameter():
	conConfig=ConnectionConfig()
	
	"""
	  the key is related with a server you have to set both of 
	  the method raise an APIerror
	"""

	with pytest.raises(InvalidURIError):
		conCapabilities=ConnectionCapabilities(conConfig,'mykey')

		with pytest.raises(InvalidURIError):
			conCapabilities.getClientKey()

		assert conCapabilities.serverConnected() == False

		with pytest.raises(InvalidURIError):
			with open('src/tests/capabilitiesResponse.json') as json_file:
				capResponse = json.load(json_file)
				conCapabilities.addConnection(capResponse);


def test_addConnection():
	#No server url in intialization
	
	conConfig=ConnectionConfig({"server":"http://localhost:6363"})
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')

	assert ({"http://localhost:6363/":{'key':"mykey"}}==conCapabilities.connection)==True

	with open('src/tests/capabilitiesResponse.json') as json_file:
		capResponse = json.load(json_file)
		conCapabilities.addConnection(capResponse);

	with open ('src/tests/connectionDictionary.json') as json_file:
		dictTest = json.load(json_file)
		assert (dictTest==conCapabilities.connection) ==True
		
		#you have setServer or the serverConnected is False
		
	assert conCapabilities.serverConnected() == True
	assert conCapabilities.getClientKey()=="mykey"


def test_set_getClientKey():
	conConfig=ConnectionConfig({"server":"http://localhost:6363"})
	conCapabilities=ConnectionCapabilities(conConfig)

	conCapabilities.setClientKey("mykey")
	serverURL=conConfig.serverURL;

	assert conCapabilities.getClientKey(serverURL) =="mykey"
	
	with pytest.raises(APIError):
		assert conCapabilities.getClientKey("http://testServer")


def test_capabilitiesPermit():
	conConfig=ConnectionConfig({"server":"http://localhost:6363","db":"myFirstTerminusDB"})
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')

	with open('src/tests/capabilitiesResponseNoAllAction.json') as json_file:
		capResponse = json.load(json_file)
		conCapabilities.addConnection(capResponse)

	#if the action are not permits the method raise an Exception
	with pytest.raises(AccessDeniedError):
		conCapabilities.capabilitiesPermit(const.DELETE_DATABASE)

	with pytest.raises(AccessDeniedError):
		conCapabilities.capabilitiesPermit(const.DELETE_DOCUMENT)	

	
	assert conCapabilities.capabilitiesPermit(const.CREATE_DATABASE)==True
	assert conCapabilities.capabilitiesPermit(const.CREATE_DOCUMENT)==True	


def test_deleteDatabaseForTheConnectionList():
	conConfig=ConnectionConfig({"server":"http://localhost:6363","db":"myFirstTerminusDB"})
	conCapabilities=ConnectionCapabilities(conConfig,'mykey')

	with open('src/tests/capabilitiesResponse.json') as json_file:
		capResponse = json.load(json_file)
		conCapabilities.addConnection(capResponse)

	assert ("doc:myFirstTerminusDB" in conCapabilities.connection["http://localhost:6363/"]) == True

	conCapabilities.removeDB();

	assert ("doc:myFirstTerminusDB" in conCapabilities.connection["http://localhost:6363/"]) == False

