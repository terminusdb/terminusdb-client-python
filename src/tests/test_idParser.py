import pytest
import sys
sys.path.append('woqlclient')

from idParser import IDParser

def test_idParser01():
	servURL="http://localhost:6363/"	
	idParser=IDParser()
	assert idParser.serverURL== False, "start value of serverURL is False"
	assert idParser.dbID== False, "start value of dbID is False "
	assert idParser.docID == False, "start value of docID is False"

def test_parseServerURL():
	servURL="http://localhost:6363/"	
	idParser=IDParser()
	assert idParser.validURL(servURL)==True
	assert idParser.parseServerURL(servURL)== servURL
	assert idParser.serverURL == servURL

def test_parseDBID():
	servURL="http://localhost:6363/"
	dbName="myFirstTerminusDB"
	idParser=IDParser()
	#check db as TerminusDB name
	assert idParser.parseDBID(dbName)==dbName
	assert idParser.dbID==dbName
	assert idParser.serverURL== False
	#check db name as TerminusDB Url
	assert idParser.parseDBID(servURL+dbName)==dbName
	assert idParser.dbID==dbName
	assert idParser.serverURL== servURL

#@param {string} docURL Terminus Document URL or Terminus Document ID
def test_parseDocumentURL():
	docURL="http://localhost:6363/myFirstTerminusDB/document/chess"
	serverURL="http://localhost:6363/"
	dbName="myFirstTerminusDB"
	documentName="chess"

	idParser=IDParser()
	assert idParser.parseDocumentURL(docURL)==documentName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName
	assert idParser.docID == documentName

	newDocumentName='newDocument'
	#set a document as documentName this didn't change serverURL and dbID name
	assert idParser.parseDocumentURL(newDocumentName)==newDocumentName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName
	assert idParser.docID == newDocumentName

#check if the url of get schema is corrects
def test_parseSchemaURL():
	schemaFullUrl="http://localhost:6363/myFirstTerminusDB/schema"
	serverURL="http://localhost:6363/"
	dbName="myFirstTerminusDB"
	idParser=IDParser()
	idParser.parseSchemaURL(schemaFullUrl)==dbName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName

def test_validURL():
	fullURL="http://localhost:6363/myFirstTerminusDB/woql";
	idParser=IDParser()
	assert idParser.validURL(fullURL)== True;

#check if the url of get schema is corrects
def test_parseQueryURL():
	woqlclientFullURL="http://localhost:6363/myFirstTerminusDB/woql"
	serverURL="http://localhost:6363/"
	dbName="myFirstTerminusDB"
	idParser=IDParser()
	idParser.parseQueryURL(woqlclientFullURL)==dbName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName

#check if the url of get frame is corrects
def test_parseClassFrameURL():
	frameFullUrl="http://localhost:6363/myFirstTerminusDB/frame"
	serverURL="http://localhost:6363/"
	dbName="myFirstTerminusDB"
	idParser=IDParser()
	idParser.parseClassFrameURL(frameFullUrl)==dbName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName
