# connectionCapabilities.py

#const UTILS = require('./utils.js');
from errorMessage import ErrorMessage
import const
from errors import (AccessDeniedError,InvalidURIError)
from connectionConfig import ConnectionConfig

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
		self.setClientKey(key)

	"""
		Utility functions for changing the state of connections with Terminus servers
	"""
	def setClientKey(self, key):
		curl=self.connectionConfig.serverURL;
		if(curl and (isinstance(key,str) and key.strip())):
			if (curl not in self.connection): 
				self.connection[curl] = {}
			self.connection[curl]['key'] = key.strip()


	def getClientKey(self,serverURL=None):
		if(serverURL==None): serverURL=self.connectionConfig.serverURL
		if((serverURL in self.connection) and ('key' in  self.connection[serverURL])): 
			return self.connection[serverURL]['key']
		return False
	

	def __actionToArray(self,actions):
		if(isinstance(actions,list)==False): return []
		actionList=[];
		for item in actions:
			actionList.append(item['@id']);
		
		return actionList;
	
	"""
		@params {string} curl a valid terminusDB server URL
		@params {object} capabilities it is the connect call response
	"""
	def addConnection(self,capabilities):
		if(self.connectionConfig.serverURL!=False):
			curl=self.connectionConfig.serverURL;
			
			if (curl not in self.connection): 
				self.connection[curl] = {}

			if(isinstance(capabilities,dict)):
				for key, value in capabilities.items():
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
		else:
			raise InvalidURIError(ErrorMessage.getInvalidURIMessage('Undefined', "Add Connection"))
		#print(self.connection)
	    

	def serverConnected(self):
		if(self.connectionConfig.serverURL!=False):
			return self.connectionConfig.serverURL in self.connection
		return False


	def capabilitiesPermit(self, action, dbid=None, server=None):
		if (self.connectionConfig.connectedMode == False
			or self.connectionConfig.checkCapabilities == False
			or action == const.CONNECT): return True

		server = server if server else self.connectionConfig.serverURL
		dbid = dbid if dbid else self.connectionConfig.dbID

		rec=None
		if (action == const.CREATE_DATABASE):
			rec = self.__getServerRecord(server)
		else:
			rec = self.__getDBRecord(dbid,server)
		
		if (rec): 
			auths = rec.get('terminus:authority')
			terminusActionName='terminus:'+action
			if (auths and terminusActionName in auths): 
				return True

		raise AccessDeniedError(ErrorMessage.getAccessDeniedMessage(action, dbid, server))


	def __getServerRecord(self,serverURL):
		if (serverURL in self.connection):
			connectionObj=self.connection[serverURL]

			if isinstance(connectionObj,dict)==False:
				return None
			
			for oid in connectionObj.values():
				if (isinstance(oid,dict) and oid.get("@type") == 'terminus:Server'):
					return oid
		return None;


	def __getDBRecord(self,dbid, url):
		if isinstance(self.connection.get(url),dict)==False:
			return None

		if dbid in self.connection[url]:
			return self.connection[url][dbid]

		dbidCap = self.__dbCapabilityID(dbid);

		if dbidCap in self.connection[url]:
			return self.connection[url][dbidCap]

		return None;

	"""
	  removes a database record from the connection registry (after deletion, for example)
	""" 
	def removeDB(self, dbid=None, srvr=None):
		dbid = dbid if dbid else self.connectionConfig.dbID
		self.connectionConfig.deletedbID(dbid)
		url = srvr if srvr else self.connectionConfig.serverURL
		dbidCap = self.__dbCapabilityID(dbid)
		if(url in self.connection):self.connection[url].pop(dbidCap)


	def __dbCapabilityID(self,dbid):
		return 'doc:'+dbid

	
