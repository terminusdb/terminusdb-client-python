import sys
sys.path.append('woqlclient')

from  connectionConfig import ConnectionConfig
import pytest

def test_connectionConfig_noParameter():
	connectionConfig=ConnectionConfig()

	assert connectionConfig.serverURL== False, "start value of serverURL is False"
	assert connectionConfig.dbID== False, "start value of dbID is False "
	assert connectionConfig.connectedMode == True, "start value of connectedMode is True"
	assert connectionConfig.checkCapabilities == True, "start value of checkCapabilities is True"
	assert connectionConfig.includeKey == True, "start value of includeKey is True"
	assert connectionConfig.dbURL() == False, "no dbURL"
	assert connectionConfig.schemaURL() == False, "No schemaURL"
	assert connectionConfig.frameURL() == False, "No frameURL"
	assert connectionConfig.docURL() == False, "No docURL"
	assert connectionConfig.queryURL() == False, "No queryURL"
	assert connectionConfig.platformEndpoint() == False, "No platformEndpoint URL"



def test_connectionConfig_withParameter():
	startParameters={"server":"http://localhost:6363/",
					 "db":"myFirstTerminusDB",
					 "doc":"chess",
					 "connected_mode":False,
					 "include_key":False,
					 "checks_capabilities":False}

	connectionConfig=ConnectionConfig(startParameters)
	assert connectionConfig.serverURL== "http://localhost:6363/"
	assert connectionConfig.dbID== "myFirstTerminusDB"
	assert connectionConfig.connectedMode == False
	assert connectionConfig.checkCapabilities == False
	assert connectionConfig.includeKey == False
	assert connectionConfig.dbURL() == "http://localhost:6363/myFirstTerminusDB", "dbURL"
	assert connectionConfig.schemaURL() == "http://localhost:6363/myFirstTerminusDB/schema", "schemaURL"
	assert connectionConfig.frameURL() == "http://localhost:6363/myFirstTerminusDB/frame", "frameURL"
	assert connectionConfig.docURL() == "http://localhost:6363/myFirstTerminusDB/document/chess", "docURL"
	assert connectionConfig.queryURL() == "http://localhost:6363/myFirstTerminusDB/woql", "queryURL"
	assert connectionConfig.platformEndpoint() == False, "No platformEndpoint URL"


def test_setServer():
	connectionConfig=ConnectionConfig()
	connectionConfig.setServer("http://localhost:6363")
	assert connectionConfig.serverURL== "http://localhost:6363/"

def test_setDB():
	connectionConfig=ConnectionConfig()
	connectionConfig.setDB("myFirstTerminusDB")
	assert connectionConfig.serverURL==False
	assert connectionConfig.dbID== "myFirstTerminusDB"

	connectionConfig.setDB("http://localhost:6363/myFirstTerminusDB")
	assert connectionConfig.serverURL== "http://localhost:6363/"
	assert connectionConfig.dbID== "myFirstTerminusDB"

	connectionConfig.deletedbID("myFirstTerminusDB")
	assert connectionConfig.dbID == False

def test_setSchemaURL():
	connectionConfig=ConnectionConfig()
	connectionConfig.setSchemaURL("http://localhost:6363/myFirstTerminusDB/schema")
	assert connectionConfig.serverURL== "http://localhost:6363/"
	assert connectionConfig.dbID== "myFirstTerminusDB"

def test_setQueryURL():
	connectionConfig=ConnectionConfig()
	connectionConfig.setQueryURL("http://localhost:6363/myFirstTerminusDB/woql")
	assert connectionConfig.serverURL== "http://localhost:6363/"
	assert connectionConfig.dbID== "myFirstTerminusDB"

def test_setClassFrameURL():
	connectionConfig=ConnectionConfig()
	connectionConfig.setClassFrameURL("http://localhost:6363/myFirstTerminusDB/frame")
	assert connectionConfig.serverURL== "http://localhost:6363/"
	assert connectionConfig.dbID== "myFirstTerminusDB"

