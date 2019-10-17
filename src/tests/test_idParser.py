import pytest
from errors import (InvalidURIError)
#import sys
#sys.path.append('woqlclient')

from idParser import IDParser

def test_idParser():
	idParser=IDParser()
	with pytest.raises(InvalidURIError):
		idParser.serverURL  

	with pytest.raises(InvalidURIError):
		idParser.dbID 

	assert idParser.docID==False 

def test_parseServerURL():
	servURL="http://localhost:6363/"	
	idParser=IDParser()
	idParser.parseServerURL(servURL)
	assert idParser.serverURL == servURL

def test_parseDBID():
	dbName="myFirstTerminusDB"
	idParser=IDParser()
	#check db as TerminusDB name
	idParser.parseDBID(dbName)
	assert idParser.dbID==dbName
	#check db name as TerminusDB Url	

def test_parseDBURL():
	idParser=IDParser()
	idParser.parseDBURL("http://localhost:6363/myFirstTerminusDB")
	assert idParser.dbID=="myFirstTerminusDB"
	assert idParser.serverURL== "http://localhost:6363/"


#@param {string} docURL Terminus Document URL or Terminus Document ID
def test_parseDocumentID():
	documentName="chess"

	idParser=IDParser()
	idParser.parseDocumentID(documentName)
	assert idParser.docID==documentName


def test_validURL():
	fullURL="http://localhost:6363/myFirstTerminusDB";
	idParser=IDParser()
	assert idParser.validURL(fullURL)== True;

	fullURL="localhost&899900/myFirstTerminusDB";
	assert idParser.validURL(fullURL)== False;


def test_validIDString():
	idString="myFirstTerminusDB";
	idParser=IDParser()
	assert idParser.validIDString(idString)== True;

	idString="my First //";
	assert idParser.validIDString(idString)== False;

