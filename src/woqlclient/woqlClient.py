# woqlClient.py

import errorMessage
import connectionCapabilities
import connectionConfig
import dispatchRequest
import const
from .errors import (InvalidURIError)

	# WOQL client object
	#license Apache Version 2
	#summary Python module for accessing the Terminus DB API

class WOQLClient:

	def __init__(self,params):
	#current connection context variables
		self.dispatchRequest=dispatchRequest();
		key = params.key if params else None
		self.connectionConfig = ConnectionConfig(params);
		self.connection = ConnectionCapabilities(self.connectionConfig, key)

	"""
		Connect to a Terminus server at the given URI with an API key
	 	Stores the terminus:ServerCapability document returned
	 	in the connection register which stores, the url, key, capabilities,
	 	and database meta-data for the connected server
	 
	 	If the curl argument is false or null,
	 	this.connectionConfig.serverURL will be used if present,
	 	or it raises an error.

	  	@param  {string} curl Terminus server URI
	  	@param  {string} API  key
	 	@return dict or raise an InvalidURIError
	 	@public
	"""
	def connect(self,serverURL, key=None):	
		if (serverURL and self.connectionConfig.setServer(serverURL)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(serverURL, "Connect"))

		serverURL = self.connectionConfig.serverURL()
		if(serverURL):
			if (key):
				self.connection.setClientKey(serverURL, key)
			
			jsonObj=self.dispatch(serverURL, constants.CONNECT);
			self.connection.addConnection(serverURL, jsonObj);
			return jsonObj;
		else:
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage('Server Url Undefined', "Connect"))

	"""
	Create a Terminus Database by posting
	a terminus:Database document to the Terminus API

	The dburl argument can be
	 1) a valid URL of a terminus database or
	 2) a valid Terminus database id or
	 3) can be omitted
	 in case 2) the current server will be used,
	 in case 3) the database id will be set from the @id field of the terminuse:Database document.

	The second (details) argument contains a terminus:Database document
	with a mandatory rdfs:label field and an optional rdfs:comment field.
	The third (key) argument contains an optional API key

	@param {string} dburl Terminus server URI or a TerminusID
	@param {dict} details
	@param {string} key
	@return {???} 
	@public //{"terminus:status":"terminus:success"}
 	"""
	def createDatabase(self,dburl, details, key):
		if (dburl and self.connectionConfig.setDB(dburl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(dburl, "Create Database"))
		
		if (details and '@id'in details and
			self.connectionConfig.setDB(details['@id'], details['@context'])):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(details['@id'], "Create Database"))

		details = self.makeDocumentConsistentWithURL(details, self.connectionConfig.dbURL())
		opts = {}
		if (key):
			opts.key = key

		doc = self.addOptionsToDocument(details, opts)
		return self.dispatch(self.connectionConfig.dbURL('create'), CONST.CREATE_DATABASE, doc)

	"""
	 	Delete a Database
	 	@param {string} dburl it is a terminusDB Url or a terminusDB Id
	 	@param {dict} opts no options are currently supported for this function
	 	@return {??}
	 
	   if dburl is omitted, the current server and database will be used
	"""
	def deleteDatabase(self, dburl, opts):
		if(dburl and self.connectionConfig.setDB(dburl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(dburl, "Delete Database"))
		
		jsonResponse=self.dispatch(self.connectionConfig.dbURL()+'/', CONST.DELETE_DATABASE, opts)
		
		self.connection.removeDB()
		return jsonResponse

	"""
		Retrieves the schema of the specified database
	 
		@param {string} schurl TerminusDB server URL or a valid TerminusDB Id or omitted
		@param {dict} opts is an options object
		@return {??}
		
		opts.format is optional and defines which format is requested (*json / turtle)
		opts.key is an optional API key
	"""
	def getSchema(self,schurl, opts):
		if (schurl and self.connectionConfig.setSchemaURL(schurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(schurl, "Get Schema"))
		return self.dispatch(self.connectionConfig.schemaURL(), CONST.GET_SCHEMA, opts)

	"""
 		Updates the Schema of the specified database
 		@param {string} schurl TerminusDB server URL or a valid TerminusDB Id or omitted
 		@param {object} doc is a valid owl ontology in json-ld or turtle format
 		@param {object} opts is an options object
 		returns {??}

 		if omitted the current server and database will be used
		opts.format is used to specify which format is being used (*json / turtle)
 		opts.key is an optional API key
 	"""
	def updateSchema(self,schurl, doc, opts):
		if (schurl and self.connectionConfig.setSchemaURL(schurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(schurl, "Update schema"))
	
		doc = this.addOptionsToDocument(doc, opts);
		return this.dispatch(this.connectionConfig.schemaURL(),constants.woql_update, doc)

	"""
		Creates a new document in the specified database
	
		The first (docurl) argument can be
		1) a valid URL of a terminus database (an id will be randomly assigned) or
		2) a valid URL or of a terminus document (the document will be given the passed URL) or
		3) a valid terminus document id (the current server and database will be used)
		4) can be omitted (the URL will be taken from the document if present)
		The second argument (doc) is a valid document in json-ld
		the third argument (opts) is an options json - opts.key is an optional API key
	""" 
	def createDocument(self,docurl, doc, opts):
		self.__checkDocumentURI("Create Document",docurl,doc);
		doc = self.addOptionsToDocument(self.makeDocumentConsistentWithURL(docurl, doc),opts)
		return self.dispatch(self.connectionConfig.docURL(), constants.CREATE_DOCUMENT, doc);




	def __checkDocumentURI(self, msg, docurl, doc=None):
		if (docurl and self.connectionConfig.setDocument(docurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, msg))
		if (doc and '@id' in doc and 
			self.connectionConfig.setDocument(doc['@id'], doc['@context'])==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, msg))

	"""
		Retrieves a document from the specified database
		
		The first (docurl) argument can be
		1) a valid URL of a terminus document or
		2) a valid ID of a terminus document in the current database
		the second argument (opts) is an options json -
	  		opts.key is an optional API key
	  		opts.shape is frame | *document
	"""

	def getDocument(self, docurl, opts):
		self.__checkDocumentURI("Get Document",docurl);
		return self.dispatch(self.connectionConfig.docURL(), constants.GET_DOCUMENT, opts)

	"""
	 	Updates a document in the specified database with a new version
	 
	 	The first (docurl) argument can be
	 	1) a valid URL of a terminus document or
	 	2) a valid ID of a terminus document in the current database or
	 	3) omitted in which case the id will be taken from the document @id field
	 	the second argument (doc) is a document in json-ld format
	 	the third argument (opts) is an options json - opts.key is an optional API key
	"""

	def updateDocument(self,docurl, doc, opts):
		self.__checkDocumentURI('Upadate document',docurl,doc);
		doc = self.addOptionsToDocument(self.makeDocumentConsistentWithURL(docurl, doc),opts)
		return self.dispatch(this.connectionConfig.docURL(), 'update_document', doc)

	"""
		Deletes a document from the specified database
		
		The first (docurl) argument can be
		1) a valid URL of a terminus document or
		2) a valid ID of a terminus document in the current database
		3) omitted - the current document will be used
		the second argument (opts) is an options json - opts.key is an optional API key
	"""

	def deleteDocument(self,docurl, opts):
		if (docurl and (self.connectionConfig.setDocument(docurl)==False or 
			self.connectionConfig.docID==False)):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Delete Document"))
		return self.dispatch(self.connectionConfig.docURL(), constants.DELETE_DOCUMENT, opts)

	"""
		Executes a read-only WOQL query on the specified database and returns the results

		@param {string} qurl TerminusDB server URL or omitted (the current DB will be used)
		@param {string} woql is a "woql query select statement" 
		@param {dict} opts it can contents the API key (opts.key)	
	"""
	def select(qurl, woql, opts):
		if (qurl and self.connectionConfig.setQueryURL(qurl)==True):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Select"))
		q = { query: woql }
		q = self.addOptionsToWOQL(q, opts)
		return self.dispatch(self.connectionConfig.queryURL(), CONST.WOQL_SELECT, q)

	"""
		Executes a WOQL query on the specified database which updates the state and returns the results

		The first (qurl) argument can be
		1) a valid URL of a terminus database or
		2) omitted - the current database will be used
		the second argument (woql) is a woql select statement encoded as a string
		the third argument (opts) is an options json - opts.key is an optional API key
	"""
	def update(self,qurl=None, woql=None, opts=None):
		if (qurl and self.connectionConfig.setQueryURL(qurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Update"))

		woql = self.addOptionsToWOQL(woql, opts);
		return self.dispatch(self.connectionConfig.queryURL(), 'woql_update', woql)

	"""
		Retrieves a WOQL query on the specified database which updates the state and returns the results
		
		The first (cfurl) argument can be
		1) a valid URL of a terminus database or
		2) omitted - the current database will be used
		the second argument (cls) is the URL / ID of a document class that exists in the database schema
		the third argument (opts) is an options json - opts.key is an optional API key
	"""

	def getClassFrame(self,cfurl, cls, opts=None):
		if (cfurl and self.connectionConfig.setClassFrameURL(cfurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Get Class Frame"))
	
		if (isinstance(opts,dict)==False): opts = {};
		opts['class'] = cls;
		return self.dispatch(self.connectionConfig.frameURL(), constants.CLASS_FRAME, opts)



 	#Utility functions for adding standard fields to API arguments
	def addOptionsToWOQL(self, woql, options=None):
		if (options and 'key' in options):
			woql.key = options.key
		return woql


	def addOptionsToDocument(self, doc, options=None):
		document = { 'terminus:document': doc }
		document['@context'] = doc['@context']
		document['terminus:document'].pop('@context')
		document['@type'] = 'terminus:APIUpdate'
		if options and 'key' in options :  
			document.key = options.key

		return document

	def addKeyToPayload(self,payload):
		if isinstance(payload,dict)==False:
			payload = {}

		if 'key' in  payload :
			payload['terminus:user_key'] = payload.key
			payload.pop('key')
		elif(self.connection.getClientKey()):
			payload['terminus:user_key'] = self.connection.getClientKey()
	
		return payload

	#raise an error bad document...!!
	def makeDocumentConsistentWithURL(self, doc, dburl):
		if(isinstance(doc,dict)):
			doc['@id'] = dburl
		return doc

	def dispatch(self, url, action, payload):
		if (action != constants.CONNECT
			and self.connectionConfig.connectionMode()
			and self.connection.serverConnected()==False):
			
			key = payload.key if isinstance(payload,dict) and key in payload else False
			self.connect(self.connectionConfig.serverURL, key)

			if (key in payload):payload.pop('key')
			#self.dispatch(url, action, payload);
			#return response;

			#check if we can perform this action or raise an AccessDeniedError error
			self.connection.capabilitiesPermit(action);		

		if (self.connectionConfig.includeKey):
			payload = self.addKeyToPayload(payload)

		return self.dispatchRequest(url, action, payload)

