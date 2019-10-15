# woqlClient.py
from dispatchRequest import DispatchRequest

import errorMessage
from  connectionConfig import ConnectionConfig
from  connectionCapabilities import ConnectionCapabilities

import const
from errorMessage import ErrorMessage
from errors import (InvalidURIError)

from createDatabaseTemplate import CreateDBTemplate

	# WOQL client object
	#license Apache Version 2
	#summary Python module for accessing the Terminus DB API

class WOQLClient:

	def __init__(self,params={}):
	#current conCapabilities context variables
		self.dispatchRequest=DispatchRequest();
		key = params.get('key')
		self.conConfig = ConnectionConfig(params);
		self.conCapabilities = ConnectionCapabilities(self.conConfig, key)

	"""
		Connect to a Terminus server at the given URI with an API key
	 	Stores the terminus:ServerCapability document returned
	 	in the conCapabilities register which stores, the url, key, capabilities,
	 	and database meta-data for the connected server
	 
	 	If the curl argument is false or null,
	 	this.conConfig.serverURL will be used if present,
	 	or it raises an error.

	  	@param  {string} curl Terminus server URI
	  	@param  {string} API  key
	 	@return dict or raise an InvalidURIError
	 	@public
	"""
	def connect(self,serverURL=None, key=None):	
		if (serverURL and self.conConfig.setServer(serverURL)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(serverURL, "Connect"))

		serverURL = self.conConfig.serverURL
		if(serverURL):
			if (key):
				self.conCapabilities.setClientKey(key)
			
			jsonObj=self.dispatch(serverURL, const.CONNECT,key);
			self.conCapabilities.addConnection(jsonObj);
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
	def createDatabase(self,dbID,label,key=None,**kwargs):
		if(self.conConfig.setDB(dbID)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(dbID, "Create Database"))
		
		createDBTemplate=CreateDBTemplate.getTemplate(self.conConfig.serverURL,self.conConfig.dbID,label,**kwargs);

		return self.dispatch(self.conConfig.dbURL, const.CREATE_DATABASE, key, createDBTemplate)

	"""
	 	Delete a Database
	 	@param {string} dburl it is a terminusDB Url or a terminusDB Id
	 	@param {dict} opts no options are currently supported for this function
	 	@return {??}
	 
	   if dburl is omitted, the current server and database will be used
	"""
	def deleteDatabase(self, dbID, key=None):
		if(self.conConfig.setDB(dbID)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(dbID, "Delete Database"))
		
		jsonResponse=self.dispatch(self.conConfig.dbURL()+'/', const.DELETE_DATABASE, key)
		
		self.conCapabilities.removeDB()
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
		if (schurl and self.conConfig.setSchemaURL(schurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(schurl, "Get Schema"))
		return self.dispatch(self.conConfig.schemaURL(), const.GET_SCHEMA, opts)

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
		if (schurl and self.conConfig.setSchemaURL(schurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(schurl, "Update schema"))
	
		doc = this.addOptionsToDocument(doc, opts);
		return this.dispatch(this.conConfig.schemaURL(),const.woql_update, doc)

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
		return self.dispatch(self.conConfig.docURL(), const.CREATE_DOCUMENT, doc);




	def __checkDocumentURI(self, msg, docurl, doc=None):
		if (docurl and self.conConfig.setDocument(docurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, msg))
		if (doc and '@id' in doc and 
			self.conConfig.setDocument(doc['@id'], doc['@context'])==False):
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
		return self.dispatch(self.conConfig.docURL(), const.GET_DOCUMENT, opts)

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
		return self.dispatch(this.conConfig.docURL(), 'update_document', doc)

	"""
		Deletes a document from the specified database
		
		The first (docurl) argument can be
		1) a valid URL of a terminus document or
		2) a valid ID of a terminus document in the current database
		3) omitted - the current document will be used
		the second argument (opts) is an options json - opts.key is an optional API key
	"""

	def deleteDocument(self,docurl, opts):
		if (docurl and (self.conConfig.setDocument(docurl)==False or 
			self.conConfig.docID==False)):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Delete Document"))
		return self.dispatch(self.conConfig.docURL(), const.DELETE_DOCUMENT, opts)

	"""
		Executes a read-only WOQL query on the specified database and returns the results

		@param {string} qurl TerminusDB server URL or omitted (the current DB will be used)
		@param {string} woql is a "woql query select statement" 
		@param {dict} opts it can contents the API key (opts.key)	
	"""
	def select(qurl, woql, opts):
		if (qurl and self.conConfig.setQueryURL(qurl)==True):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Select"))
		q = { query: woql }
		q = self.addOptionsToWOQL(q, opts)
		return self.dispatch(self.conConfig.queryURL(), const.WOQL_SELECT, q)

	"""
		Executes a WOQL query on the specified database which updates the state and returns the results

		The first (qurl) argument can be
		1) a valid URL of a terminus database or
		2) omitted - the current database will be used
		the second argument (woql) is a woql select statement encoded as a string
		the third argument (opts) is an options json - opts.key is an optional API key
	"""
	def update(self,qurl=None, woql=None, opts=None):
		if (qurl and self.conConfig.setQueryURL(qurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Update"))

		woql = self.addOptionsToWOQL(woql, opts);
		return self.dispatch(self.conConfig.queryURL(), 'woql_update', woql)

	"""
		Retrieves a WOQL query on the specified database which updates the state and returns the results
		
		The first (cfurl) argument can be
		1) a valid URL of a terminus database or
		2) omitted - the current database will be used
		the second argument (cls) is the URL / ID of a document class that exists in the database schema
		the third argument (opts) is an options json - opts.key is an optional API key
		cls "http://terminusdb.com/schema/tcs#Person"
	"""
	
	def getClassFrame(self,cfurl, cls, opts=None):
		if (cfurl and self.conConfig.setClassFrameURL(cfurl)==False):
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage(docurl, "Get Class Frame"))
	
		if (isinstance(opts,dict)==False): opts = {};
		opts['class'] = cls;
		return self.dispatch(self.conConfig.frameURL(), const.CLASS_FRAME, opts)



 	#Utility functions for adding standard fields to API arguments
	def addOptionsToWOQL(self, woql, options=None):
		if (options and 'key' in options):
			woql['key'] = options['key']
		return woql


	def addOptionsToDocument(self, doc, options=None):
		document = { 'terminus:document': doc }
		document['@context'] = doc['@context']
		document['terminus:document'].pop('@context')
		document['@type'] = 'terminus:APIUpdate'
		if options and 'key' in options :  
			document['key'] = options['key']

		return document


	def addOptionsToDocument(self, doc, options=None):
		document = {};
		document['@context'] = doc['@context'];
		if ('@context' in doc) and ('@id' in doc): # add blank node prefix as document base url
			document['@context']['_'] = doc['@id']

		if (options and options.get('terminus:encoding') and options['terminus:encoding'] == 'terminus:turtle'):
			document['terminus:turtle'] = doc
			document['terminus:schema'] = self.conConfig.schemaURL()
			del document['terminus:turtle']['@context']
		else:
			document['terminus:document'] = doc
			del document['terminus:document']['@context']
	
		document['@type'] = 'terminus:APIUpdate'
		if options:
			if 'terminus:user_key' in options: 
				document['terminus:user_key'] = options['terminus:user_key'];
	
			if 'key' in options:
				document['terminus:user_key'] = options['key']
		print(document)
		return document

	#raise an error bad document...!!
	def makeDocumentConsistentWithURL(self, doc, dburl):
		if(isinstance(doc,dict)):
			doc['@id'] = dburl
		return doc


	def dispatch(self, url, action, connectionKey, payload={}):
		if connectionKey==None :
			print('getClientKey',self.conCapabilities.getClientKey())
			connectionKey=self.conCapabilities.getClientKey()
		
		print("connectedModeMMMMMMMMMMMMMMMMMMMM",self.conConfig.connectedMode)
		print("self.conCapabilities.serverConnected()",self.conCapabilities.serverConnected())
		if (action != const.CONNECT
			and self.conConfig.connectedMode
			and self.conCapabilities.serverConnected()==False):
			
			#key = payload.key if isinstance(payload,dict) and key in payload else False
			self.connect(self.conConfig.serverURL, connectionKey)
			print("CONNCT BEFORE ACTION",action)

		#check if we can perform this action or raise an AccessDeniedError error
		self.conCapabilities.capabilitiesPermit(action);		
		print('getClientKey',connectionKey)
		return self.dispatchRequest.sendRequestByAction(url, action, connectionKey,payload)

