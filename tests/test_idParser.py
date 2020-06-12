import pytest
from woqlclient import (InvalidURIError)
#import sys
#sys.path.append('woqlclient')

from woqlclient import IDParser

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
        idParser=IDParser()
        # Normal localhost URI with port
        assert idParser.validURL("http://localhost:6363/myFirstTerminusDB") == True
        # Normal hostname with port
        assert idParser.validURL('http://someURL:6363/aDatabase')
        # Invalid URI with illegal characters
        assert idParser.validURL('http://!illegalURI:6363@@@@@e21e21d2faf') == False
        # Wrong port number identifier
        assert idParser.validURL("localhost&899900/myFirstTerminusDB") == False
        # Normal IP address
        assert idParser.validURL("http://127.0.0.1:6363/aDatabase")
        # IP address without port
        assert idParser.validURL("http://127.0.0.1/aDatabase")


def test_validIDString():
	idString="myFirstTerminusDB";
	idParser=IDParser()
	assert idParser.validIDString(idString)== True;

	idString="my First:";
	assert idParser.validIDString(idString)== False;
