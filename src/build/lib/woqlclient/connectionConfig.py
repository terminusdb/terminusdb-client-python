# connectionConfig.py

import idParser


class ConnectionConfig:

	def __init__(self,params={}):
		self._server = False
		self._dbid = False
		self._docid = False
		"""
		  client configuration options - connected_mode = true
		  tells the client to first connect to the server before invoking other services
		"""
		self._connected_mode = True
		# include a terminus:user_key API key in the calls
		self._include_key = True
		# client side checking of access control (in addition to server-side access control)
		self.__checks_capabilities=True

		if'server' in params:
			self.setServer(params['server'])
		if'db' in params: 
			self.setDB(params['db'])
		if'doc' in params:
			self.setDocument(params['doc'])
		if 'connected_mode' in params and params['connected_mode'] == False:
			self._connected_mode=True
		if 'include_key' in params and params['include_key'] == False:
			self._include_key = False
		if 'checks_capabilities' in params and params['checks_capabilities'] == False:
			self._checks_capabilities = False


	def deletedbID(self,dbName):
		if self.dbID and self.dbID == dbName:
			self._dbid = False

	@property
	def serverURL(self):
		return self._server

	@property
	def dbID(self):
		return self._dbid

	@property
	def connectedMode(self):
		return self._connected_mode

	@property
	def checkCapabilities(self):
		return self._checks_capabilities

	@property
	def includeKey(self):
		return self._include_key

	def schemaURL(self):
		return self.dbURL()+'/schema'

	def queryURL(self):
		return self.dbURL()+'/woql'

	def frameURL(self):
		return self.dbURL()+'/frame'

	def docURL(self):
		return self.dbURL()+'/document/'+ self._docid if self._docid else ''

	def dbURL(self,call=None):
	# url swizzling to talk to platform using server/dbid/platform/ pattern..
		if (self.platformEndpoint()):
			baseURL=self._server[0:self._server.rfind('/platform/')]
			if(call == None or call != 'create'):
				return baseURL+'/'+self._dbid+'/platform'
			elif( call == 'platform'):
				return baseURL+'/'+self._dbid
		
		return self._server + self._dbid


	def platformEndpoint(self):
		if (self._server.rfind('/platform/') == (len(self._server) - 10)):
			return True;
		
		return False;

	"""
	  Utility functions for setting and parsing urls and determining
	  the current server, database and document
	"""
	def setServer(self, inputStr, context):
		parser = IDParser(context)
		if (parser.parseServerURL(inputStr)):
			self._server = parser.serverURL;
			self._dbid=false
			self._docid = false
			return true
		return false

	"""
	  @param {string} inputStr Terminus server URI or a TerminusID
	"""

	def setDB(self, inputStr, context):
		parser = IDParser(context);
		if (parser.parseDBID(inputStr)):
			if (parser.serverURL): self._server = parser.serverURL
			self._dbid = parser.dbID
			self._docid = false
			return true
		return false

	def setSchemaURL(self,inputStr, context):
		parser = IDParser(context)
		if (parser.parseSchemaURL(inputStr)):
			if (parser.serverURL): self._server = parser.serverURL;
			self._dbid = parser.dbID
			self._docid = False;
			return True
	
		return False

	def setDocument(self,inputStr, context):
		parser = IDParser(context)
		if (parser.parseDocumentURL(inputStr)):
			if (parser.serverURL): self._server = parser.serverURL
			if (parser.dbID): self._dbid = parser.dbID
			if (parser.docID): self._docid = parser.docID
			return True
	
		return False


	def setQueryURL(self,inputStr, context):
		parser = IDParser(context)
		if (parser.parseQueryURL(inputStr)):
			if (parser.serverURL): self._server = parser.serverURL
			self._dbid = parser.dbID;
			self._docid = False;
			return True
	
		return False

	def setClassFrameURL(self,inputStr, context):
		parser = IDParser(context)
		if (parser.parseClassFrameURL(inputStr)):
			if (parser.serverURL): self._server = parser.serverURL
			self._dbid = parser.dbID
			self._docid = False
			return True
	
		return False
