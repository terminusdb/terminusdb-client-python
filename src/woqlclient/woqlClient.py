# woqlClient.py
from dispatchRequest import DispatchRequest

import errorMessage
from  connectionConfig import ConnectionConfig
from  connectionCapabilities import ConnectionCapabilities

import const
from errorMessage import ErrorMessage
from errors import (InvalidURIError)

from documentTemplate import DocumentTemplate

from idParser import IDParser
import json

	# WOQL client object
	#license Apache Version 2
	#summary Python module for accessing the Terminus DB API

class WOQLClient:

	def __init__(self,params={}):
		#current conCapabilities context variables
		key = params.get('key')
		self.conConfig = ConnectionConfig(params);
		self.conCapabilities = ConnectionCapabilities(self.conConfig, key)

	"""
		Connect to a Terminus server at the given URI with an API key
		Stores the terminus:ServerCapability document returned
		in the conCapabilities register which stores, the url, key, capabilities,
		and database meta-data for the connected server
	 
		If the serverURL argument is omitted,
		self.conConfig.serverURL will be used if present
		or an error will be raise.

		:param  {string} serverURL Terminus server URI
		:param  {string} API  key
		:return dict or raise an InvalidURIError
		:public
	"""
	def connect(self,serverURL=None, key=None): 
		if serverURL:
			self.conConfig.setServer(serverURL)
			
		if key:
			self.conCapabilities.setClientKey(key)
			
		jsonObj=self.dispatch(self.conConfig.serverURL, const.CONNECT,key)
		self.conCapabilities.addConnection(jsonObj)
		return jsonObj;
		

	"""
		connect directly without create a new class instance
	"""
	@staticmethod
	def directConnect(serverURL,key):
		idParser=IDParser()
		idParser.parseServerURL(serverURL)
		return DispatchRequest.sendRequestByAction(idParser.serverURL, const.CONNECT, key)


	"""
		Create a Terminus Database by posting
		a terminus:Database document to the Terminus Server

		:param {string} dbID TerminusDB id
		:param {string} label Terminus label 
		:param {string} key you can omit the key if you have set it before
		:param **kwargs: Optional arguments that ``createDatabase`` takes.
		:return {dict} {"terminus:status":"terminus:success"} 
		
		:public 
	"""
	def createDatabase(self,dbID,label,key=None,**kwargs):
		self.conConfig.setDB(dbID)
		createDBTemplate=DocumentTemplate.createDBTemplate(self.conConfig.serverURL,self.conConfig.dbID,label,**kwargs);
		return self.dispatch(self.conConfig.dbURL, const.CREATE_DATABASE, key, createDBTemplate)

	"""
		:param {string} dbURL  TerminusDB full URL like http://localhost:6363/myDB
		:param {label}  the terminus db title
		:param {string} key is the server API key
		:param **kwargs: Optional arguments that ``createDatabase`` takes.
		:return {dict} {"terminus:status":"terminus:success"} 

	"""
	@staticmethod	
	def directCreateDatabase(dbURL,label,key,**kwargs):
		idParser=IDParser()
		idParser.parseDBURL(dbURL)		
		createDBTemplate=DocumentTemplate.createDBTemplate(idParser.serverURL,idParser.dbID,label,**kwargs);
		DispatchRequest.sendRequestByAction(idParser.dbURL(), const.CREATE_DATABASE, key,createDBTemplate)

	"""
		Delete a TerminusDB
		:param {string} dbID is a terminusDB Id
		:param {key} you need the key if you didn't set before
		:return {dict} {"terminus:status":"terminus:success"} 
	"""

	def deleteDatabase(self, dbID, key=None):
		self.conConfig.setDB(dbID)
		jsonResponse=self.dispatch(self.conConfig.dbURL()+'/', const.DELETE_DATABASE, key)
		self.conCapabilities.removeDB()
		return jsonResponse
	
	"""
		param {string} dbURL  TerminusDB full URL like http://localhost:6363/myDB
		param {key} is the server API key
	"""

	@staticmethod
	def directDeleteDatabase(dbURL,key):
		idParser=IDParser()
		idParser.parseDBURL(dbURL)
		DispatchRequest.sendRequestByAction(idParser.dbURL()+'/', const.DELETE_DATABASE, key)
	

	"""
		Retrieves the schema of the specified database
	 
		param {string} dbId TerminusDB Id or omitted (get last select database)
		param {key} is the server API key
		return {string/dict}
		
		opts.format defines which format is requested, default is turtle(*json / turtle)
	"""

	def getSchema(self, dbID=None, key=None ,options={"terminus:encoding": "terminus:turtle"}):
		if (dbID):
			self.conConfig.setDB(dbID)

		return self.dispatch(self.conConfig.schemaURL(), const.GET_SCHEMA, key, options)


	@staticmethod
	def directGetSchema(dbURL,key,options={"terminus:encoding": "terminus:turtle"}):
		idParser=IDParser()
		idParser.parseDBURL(dbURL)
		DispatchRequest.sendRequestByAction(idParser.schemaURL(), const.GET_SCHEMA, key ,options)


	"""
		Updates the Schema of the specified database
		:param {object} doc is a valid owl ontology in json-ld or turtle format
		:param {string} dbid TerminusDB Id or omitted
		:param {string} key is an API key
		:param {object} opts is an options object
		returns {dict} {"terminus:status":"terminus:success"}

		opts.format is used to specify which format is being used (*json / turtle)
	"""

	def updateSchema(self, docObj , dbID=None, key=None, opts={"terminus:encoding": "terminus:turtle"}):
		if (dbID):
			self.conConfig.setDB(dbID)
		docObj = DocumentTemplate.formatDocument(docObj, self.conConfig.schemaURL(), opts);
		return self.dispatch(self.conConfig.schemaURL(),const.UPDATE_SCHEMA, key, docObj)



	@staticmethod
	def directUpdateSchema(dbURL, docObj, key,opt={"terminus:encoding": "terminus:turtle"}):
		idParser=IDParser()
		idParser.parseDBURL(dbURL)
		docObj = DocumentTemplate.formatDocument(docObj, idParser.schemaURL(), opts);
		DispatchRequest.sendRequestByAction(idParser.schemaURL(), const.UPDATE_SCHEMA, key ,docObj)


	"""
		Creates a new document in the specified database
	
		:params {string} documentID is a valid Terminus document id
		:params {string} dbId is a valid TerminusDB id
		:params {dict } docObj  is a valid document in json-ld
		:params key is an optional API key
	""" 
	def createDocument(self, docObj, documentID, dbID=None, key=None):
		if(dbID):
			self.conConfig.setDB(dbID)
		self.conConfig.setDocument(documentID)
		docObj = DocumentTemplate.formatDocument(doc, self.conConfig.schemaURL(),None,self.conConfig.docURL()) 
		return self.dispatch(self.conConfig.docURL(), const.CREATE_DOCUMENT, key, docObj)


	"""
		Creates a new document in the specified database
	
		:params {string} documentID is a valid Terminus document id
		:params {string} dbURL is a valid TerminusDB full URL
		:params {dict } docObj  is a valid document in json-ld
		:params key is an optional API key
	""" 

	@staticmethod	
	def directCreateDocument(docObj, documentID, dbURL, key):
		idParser=IDParser()
		idParser.parseDBURL(dbURL)
		idParser.parseDocumentID(documentID)

		docObj = DocumentTemplate.formatDocument(doc, idParser.schemaURL(),None,idParser.docURL())
		return self.dispatch(idParser.docURL(), const.CREATE_DOCUMENT, key, docObj)


	"""
		Retrieves a document from the specified database
		:params {string} documentID is a valid Terminus document id
		:params {string} dbID is a valid TerminusDB id
		:params key is an optional API key
		opts
	"""

	def getDocument(self, documentID, dbID=None, key=None, opts={"terminus:encoding": "terminus:frame"}):
		if(dbID):
			self.conConfig.setDB(dbID)

		self.conConfig.setDocument(documentID)
		return self.dispatch(self.conConfig.docURL(), const.GET_DOCUMENT, key, opts)


	@staticmethod
	def directGetDocument(documentID, dbURL, key, opts={"terminus:encoding": "terminus:frame"}):
		idParser=IDParser()
		idParser.parseDBURL(dbURL)
		idParser.parseDocumentID(documentID)
		return self.dispatch(idParser.docURL(), const.GET_DOCUMENT, key, opts)

	"""
		Updates a document in the specified database with a new version
	 
	"""
	
	def updateDocument(self, documentID, docObj, dbID=None, key=None):
		if(dbID):
			self.conConfig.setDB(dbID)

		self.conConfig.setDocument(documentID)
		docObj=DocumentTemplate.formatDocument(docObj, self.conConfig.schemaURL(),None,self.conConfig.docURL())
		return self.dispatch(self.conConfig.docURL(), const.UPDATE_DOCUMENT, key, docObj)

	"""
		Deletes a document from the specified database

	"""

	def deleteDocument(self, documentID,  dbID=None, key=None):
		if(dbID):
			self.conConfig.setDB(dbID)

		self.conConfig.setDocument(documentID)

		return self.dispatch(self.conConfig.docURL(), const.DELETE_DOCUMENT, key)

	"""
		Executes a read-only WOQL query on the specified database and returns the results

		:param {string} woqlQuery is a "woql query select statement"    
	"""
	def select(self, woqlQuery, dbID=None, key=None):
		if(dbID):
			self.conConfig.setDB(dbID)

		payload = { 'terminus:query': json.dump(woqlQuery) }
		return self.dispatch(self.conConfig.queryURL(), const.WOQL_SELECT, key, payload)

	"""
		Executes a WOQL query on the specified database which updates the state and returns the results

		The first (qurl) argument can be
		1) a valid URL of a terminus database or
		2) omitted - the current database will be used
		the second argument (woql) is a woql select statement encoded as a string
		the third argument (opts) is an options json - opts.key is an optional API key
	"""
	def update(self, woqlQuery, dbID=None, key=None):
		if(dbID):
			self.conConfig.setDB(dbID)
			#raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Update"))
		payload = { 'terminus:query': json.dump(woqlQuery) }
		return self.dispatch(self.conConfig.queryURL(), const.WOQL_UPDATE, key,  woqlQuery)


	def dispatch(self, url, action, connectionKey, payload={}):
		if connectionKey==None :
			#if the api key is not setted the method raise an APIerror
			connectionKey=self.conCapabilities.getClientKey()
		
		if (action != const.CONNECT
			and self.conConfig.connectedMode
			and self.conCapabilities.serverConnected()==False):
			
			#key = payload.key if isinstance(payload,dict) and key in payload else False
			self.connect(self.conConfig.serverURL, connectionKey)
			print("CONNCT BEFORE ACTION",action)

		#check if we can perform this action or raise an AccessDeniedError error
		self.conCapabilities.capabilitiesPermit(action);        
		return DispatchRequest.sendRequestByAction(url, action, connectionKey,payload)

