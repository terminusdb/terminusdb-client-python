from  woqlclient import ConnectionConfig
import pytest
from woqlclient import (InvalidURIError)

def test_connectionConfig_noParameter():
	connectionConfig=ConnectionConfig()

	"""
	 you need to set the terminusServer and the terminusDB id
	"""
	with pytest.raises(InvalidURIError):
		connectionConfig.serverURL
		connectionConfig.dbID
		connectionConfig.schemaURL()
		connectionConfig.docURL()
		connectionConfig.queryURL()
		connectionConfig.dbURL()

	assert connectionConfig.connectedMode == True, "start value of connectedMode is True"
	assert connectionConfig.checkCapabilities == True, "start value of checkCapabilities is True"
	assert connectionConfig.includeKey == True, "start value of includeKey is True"


def test_connectionConfig_withParameter():
	
	startParameters={"server":"http://localhost:6363/",
					 "db":"myFirstTerminusDB",
					 "doc":"chess",
					 "connected_mode":False,
					 "include_key":False,
					 "checks_capabilities":False}
	

	connectionConfig=ConnectionConfig(**startParameters)

	assert connectionConfig.serverURL== "http://localhost:6363/"
	assert connectionConfig.dbID== "myFirstTerminusDB"
	assert connectionConfig.connectedMode == False
	assert connectionConfig.checkCapabilities == False
	assert connectionConfig.includeKey == False
	assert connectionConfig.dbURL() == "http://localhost:6363/myFirstTerminusDB", "dbURL"
	assert connectionConfig.schemaURL() == "http://localhost:6363/myFirstTerminusDB/schema", "schemaURL"
	assert connectionConfig.docURL() == "http://localhost:6363/myFirstTerminusDB/document/chess", "docURL"
	assert connectionConfig.queryURL() == "http://localhost:6363/myFirstTerminusDB/woql", "queryURL"


def test_setServer():
	connectionConfig=ConnectionConfig()
	connectionConfig.setServer("http://localhost:6363")
	assert connectionConfig.serverURL== "http://localhost:6363/"
