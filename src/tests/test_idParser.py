#python -m pytest tests/
#/home/francesca/.local/share/virtualenvs/woql-client-p-8xHZxgu2/lib
import pytest
from woqlclient.idParser import IDParser

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
	dbName="terminus"
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
	docURL="http://localhost:6363/masterdb/document/admin"
	serverURL="http://localhost:6363/"
	dbName="masterdb"
	documentName="admin"

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
	schemaFullUrl="http://localhost:6363/masterdb/schema"
	serverURL="http://localhost:6363/"
	dbName="masterdb"
	idParser=IDParser()
	idParser.parseSchemaURL(schemaFullUrl)==dbName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName

#check if the url of get schema is corrects
def test_parseQueryURL():
	woqlclientFullURL="http://localhost:6363/terminus/woql"
    serverURL="http://localhost:6363/"
	dbName="masterdb"
	idParser=IDParser()
	idParser.parseSchemaURL(woqlclientFullURL)==dbName
	assert idParser.serverURL== serverURL
	assert idParser.dbID == dbName

