# connectionCapabilities.py

#const UTILS = require('./utils.js');
ErrorMessage = __import__('errorMessage')
import const
from .errors import (AccessDeniedError)

"""
	Creates an entry in the connection registry for the server
	and all the databases that the client has access to
	maps the input authorties to a per-db array for internal storage and easy
	access control checks
	{doc:dbid => {terminus:authority =>
	[terminus:woql_select, terminus:create_document, auth3, ...]}}
"""
class ConnectionCapabilities:

	def __init__(self,connectionConfig,key=None):
		self.connection = {};
		self.connectionConfig = connectionConfig
		if ('server' in self.connectionConfig and key): 
			self.setClientKey(self.connectionConfig['server'], key)


	"""
		Utility functions for changing the state of connections with Terminus servers
	"""
	def setClientKey(self,curl, key):
		if(isinstance(key,str) and key.strip()):
			if (curl not in self.connection): 
				self.connection[curl] = {}
			self.connection[curl][key] = key.strip()


	def getClientKey(self,serverURL=None):
		if(serverURL==None): serverURL=self.connectionConfig.serverURL
		if(serverURL in self.connection): return self.connection[serverURL].key
	

	def __actionToArray(self,actions):
		if(isinstance(actions,list)): return []
		actionList=[];
		for item in actions:
			actionList.append(item['@id']);
		
		return actionList;
	
	"""
		@params {string} curl a valid terminusDB server URL
		@params {object} capabilities it is the connect call response
	"""
	def addConnection(self,curl, capabilities):
		if (curl not in self.connection): 
			self.connection[curl] = {}

		if(isinstance(capabilities,dict)):

			for key, value in thisdict.items():
				if(key == 'terminus:authority'):
					if(isinstance(value,dict)): value=[value]
					for item in value:
						scope=item['terminus:authority_scope']
						actions=item['terminus:action']
						if(isinstance(scope,dict)):
							scope=[scope]

						actionList=self.__actionToArray(actions)

						for scopeItem in scope:
							dbName=scopeItem['@id'];
							if (dbName not in self.connection[curl]):
								self.connection[curl][dbName] = scopeItem

							self.connection[curl][dbName]['terminus:authority'] = actionList
				else:
					self.connection[curl][key] = value

	def serverConnected(self):
		if(self.connectionsConfig.serverURL!=False):
			return self.connectionsConfig.serverURL in self.connection
		return False

	def capabilitiesPermit(self,action, dbid, server):
		if (self.connectionConfig.connectedMode == False
			or self.connectionConfig.checkCapabilities == False
			or action == constants.CONNECT): return True

		server = server if server else self.connectionConfig.serverURL
		dbid = dbid if dbid else self.connectionConfig.dbID

		rec=None
		if (action == constants.CREATE_DATABASE):
			rec = self.getServerRecord(server)
		else:
			rec = self.getDBRecord(dbid)
		
		if (rec): 
			auths = rec['terminus:authority']
			if (auths and auths.find('terminus:'+action) != -1): return True

		raise AccessDeniedError(ErrorMessage.getAccessDeniedMessage(url, action, dbid, server))


	def getServerRecord(self,srvr):
		url = srvr if srvr else self.connectionConfig.serverURL
		connectionObj = self.connection[url] if self.connection[url] else {}
		for oid in connectionObj: 
			if (oid['@type'] == 'terminus:Server'):
				return oid
		return False;

	def getDBRecord(self,dbid, srvr):
		url = srvr if srvr else self.connectionConfig.serverURL
		dbid = dbid if dbid else self.connectionConfig.dbID
		if isinstance(self.connection[url],dict)==False:
			return False

		if dbid in self.connection[url]:
			return self.connection[url][dbid]

		dbidCap = self.dbCapabilityID(dbid);

		if dbidCap in self.connection[url]:
			return self.connection[url][dbidCap]

		return None;


	def getServerDBRecords(self,srvr):
		url = srvr if srvr else self.connectionConfig.serverURL
		dbrecs = {}
		connectionObj = self.connection[url] if self.connection[url] else {}

		for oid in connectionObj:
			if oid['@type'] == 'terminus:Database':
				dbrecs[oid] = oid
	
		return dbrecs;

	"""
	  removes a database record from the connection registry (after deletion, for example)
	""" 
	def removeDB(self, dbid, srvr):
		dbid = dbid if dbid else self.connectionConfig.dbID
		self.connectionConfig.deletedbID(dbid)
		url = srvr if srvr else self.connectionConfig.serverURL
		dbidCap = self.dbCapabilityID(dbid)
		self.connection[url].pop(dbidCap)


	def dbCapabilityID(self,dbid):
		return 'doc:'+dbid

	def getDBRecord(self,dbid, srvr):
		url = srvr if srvr else self.connectionConfig.serverURL
		dbid = dbid if dbid else self.connectionConfig.dbID
		if isinstance(self.connection[url] ,dict):
			return False

		if dbid in self.connection[url]: 
			return self.connection[url][dbid]

		dbidCap = self.dbCapabilityID(dbid);

		if dbidCap in self.connection[url]:
			return self.connection[url][dbidCap]

		return None
