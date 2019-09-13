import pytest
from woqlclient.idParser import IDParser


def idParserTest():

	servURL="http://localhost:6363/"
	
	idParser=IDParser()
	assert idParser.serverURL== False
	assert idParser.dbID== False
	assert idParser.docID == False
	assert idParser.parseServerURL(servURL)== servURL
	assert idParser.serverURL == servURL

idParserTest()