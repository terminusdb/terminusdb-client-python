# errorMessage.py

class ErrorMessage:

	def __init__(self):
		pass

	@staticmethod	
	def getErrorAsMessage(url, api, err):
		print('getErrorAsMessage')
		message = 'Code: '+ str(err['status'])
		if('body' in err): message += ', Message: '+ err['body']
		if('action' in err): message += ', Action: '+ err['action']
		if('type' in err): message += ', Type: '+ err['type']
		if(url): message += ', url: '+url
		if(api and "method" in api): message += ', method: '+api['method'];
		return message;

	@staticmethod	
	def accessDeniedErrObj(action, db, server):
		err = {}
		err['status'] = 403
		err['url'] = (server or '') + (db or '')
		err['type'] = 'client'
		err['action'] = action
		err['body'] = err['action']+ ' not permitted for'+ err['url']
		return err


	@classmethod
	def getAPIErrorMessage(cls,url, api, err):
		return 'API Error'+ cls.getErrorAsMessage(url, api, err)

	@classmethod	
	def getAccessDeniedMessage(cls,action, dbid, server):
		errorObj= cls.accessDeniedErrObj(action, dbid, server)
		return 'Access Denied' + cls.getErrorAsMessage(None, None, errorObj)
    
	@staticmethod	
	def getInvalidKeyMessage(extraMessage=''):
		message = "The Api KEY in Undefined "+extraMessage
		return message

	@staticmethod	
	def getInvalidURIMessage(url, call):
		message = ('Invalid argument to '+
			call+' '+
			url+
			' is not a valid Terminus DB API endpoint')
		return message

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
		
			err['body'] = msg;
			#elif (data in response.data) err.body = response.data;
		err['url'] = response.url;
		err['headers'] = response.headers;
		err['redirected'] = response.redirected;
		return err
