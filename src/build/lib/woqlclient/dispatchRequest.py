#from .woqlClient import (errorMessage)
import errorMessage
import const
import requests

class DispatchRequest:

	def __init__(self):
		pass
		#header= {'user-agent': 'my-app/0.0.1'}
#json.dumps
	def getCall(self,payload,url):
		params={}
		if(payload):
			params={params:payload}
		return requests.get(url,params)

	def postCall(self,options,payload,url):
		headers = {'content-type': 'application/json'}
		return requests.post(url,json=payload,headers=headers);

	def deleteCall(self,url):
		return requests.delete(url);


	def sendRequestByAction(self, url, action, payload):
		try:
			requestResponse=None
			if (action == constants.CONNECT 
				or action==constants.GET_SCHEMA 
				or action==constants.CLASS_FRAME 
				or action==constants.WOQL_SELECT 
				or action==constants.GET_DOCUMENT):
				requestResponse= self.getCall(url,payload)
			
			elif(action==constants.DELETE_DATABASE or
				action==constants.DELETE_DOCUMENT):
				requestResponse= self.deleteCall(url)

			elif(action==constants.CREATE_DATABASE or
				action==constants.UPDATE_SCHEMA or
				action==constants.CREATE_DOCUMENT or
				action==constants.WOQL_UPDATE):
				requestResponse=self.postCall(url,payload)

			if(requestResponse.status_code==200):
				return requestResponse.json() #if not a json not it raises an error
			#requestCall.raise_for_status()
		except requests.exceptions.RequestException as err:
			print ("OOps: Something Else",err)
		except requests.exceptions.HTTPError as errh:
			print ("Http Error:",errh)
		except requests.exceptions.ConnectionError as errc:
			print ("Error Connecting:",errc)
		except requests.exceptions.Timeout as errt:
			print ("Timeout Error:",errt)     