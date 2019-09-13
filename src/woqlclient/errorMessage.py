class ErrorMessage:

	def __init__(self):
		pass

	@staticmethod	
	def getErrorAsMessage(self,url, api, err):
		print('getErrorAsMessage')
		str = 'Code: '+ err['status']
		if('body' in err): str += ', Message: '+ err['body']
		if('action' in err): str += ', Action: '+ err['action']
		if('type' in err): str += ', Type: '+ err['type']
		if(url): str += ', url: '+url
		if(api and "method" in api): str += ', method: '+api['method'];
		return str;

	@staticmethod	
	def accessDeniedErrObj(self, action, db, server):
		err = {}
		err.status = 403
		err.url = (server or '') + (db or '')
		err.type = 'client'
		err.action = action
		err.body = err['action']+ ' not permitted for'+ err['url']
		return err

	@classmethod
	def getAPIErrorMessage(self,url, api, err):
		return 'API Error'+ self.getErrorAsMessage(url, api, err)

	@classmethod	
	def getAccessDeniedMessage(self,url, action, dbid, server):
		errorObj= self.accessDeniedErrObj(action, dbid, server)
		return 'Access Denied' + self.getErrorAsMessage(url, None, errorObj)

	@staticmethod	
	def getInvalidURIMessage(url, call):
		str = ('Invalid argument to'
				+call+
				+url+
			'is not a valid Terminus DB API endpoint')
		return str

	"""
	Utility functions for generating and retrieving error messages
	and storing error state
	"""
	@staticmethod
	def parseAPIError(response):
		err = {}
		err['status'] = response['status']
		err['type'] = response['type']
		if ('data' in response and  isinstance(response['data'], dict)):
			msg=''
			try:
				msg = response.text;
			except:
				msg = response.json();
				#msg = response.toString()
		
			err.body = msg;
			#elif (data in response.data) err.body = response.data;
		err['url'] = response.url;
		err['headers'] = response.headers;
		err['redirected'] = response.redirected;
		return err
