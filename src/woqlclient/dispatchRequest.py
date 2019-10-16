#from .woqlClient import (errorMessage)
import errorMessage
import const
import requests

from utils import Utils

from base64 import b64encode

class DispatchRequest:

	def __init__(self):
		pass
		#header= {'user-agent': 'my-app/0.0.1'}
#json.dumps
	@staticmethod
	def __getCall(url,headers,payload):
		url=Utils.addParamsToUrl(url,payload)

		return requests.get(url,headers=headers)

	@staticmethod
	def __postCall(url,headers,payload):
		headers['content-type']= 'application/json'
		return requests.post(url,json=payload,headers=headers);
	
	@staticmethod
	def __deleteCall(url,headers,payload):
		url=Utils.addParamsToUrl(url,payload)
		return requests.delete(url,headers=headers);

	@staticmethod
	def __autorizationHeader(key):
		headers={}

		#if (payload and ('terminus:user_key' in  payload)):
		headers = { 'Authorization' : 'Basic %s' % b64encode((':' + key).encode('utf-8')).decode('utf-8')}#Utils.encodeURIComponent(payload['terminus:user_key'])}
		#payload.pop('terminus:user_key')
		return headers

	@classmethod
	def sendRequestByAction(cls, url, action, key, payload={}):
		print("sendRequestByAction")
		try:
			requestResponse=None
			headers=cls.__autorizationHeader(key);

			if (action == const.CONNECT 
				or action==const.GET_SCHEMA 
				or action==const.CLASS_FRAME 
				or action==const.WOQL_SELECT 
				or action==const.GET_DOCUMENT):
				requestResponse= cls.__getCall(url,headers,payload)
			
			elif(action==const.DELETE_DATABASE or
				action==const.DELETE_DOCUMENT):
				requestResponse= cls.__deleteCall(url,headers,payload)

			elif(action==const.CREATE_DATABASE or
				action==const.UPDATE_SCHEMA or
				action==const.CREATE_DOCUMENT or
				action==const.WOQL_UPDATE):
				requestResponse=cls.__postCall(url,headers,payload)

			if(requestResponse.status_code==200):
				return requestResponse.json() #if not a json not it raises an error
			#requestCall.raise_for_status()
		except ValueError as err:
			"if the response type is not a json"
			print("Value Error",err)
			return requestResponse.text
		"""
		except requests.exceptions.RequestException as err:
			print ("Request Error",err)
		except requests.exceptions.HTTPError as err:
			print ("Http Error:",err)
		except requests.exceptions.ConnectionError as err:
			print ("Error Connecting:",err)
		except requests.exceptions.Timeout as err:
			print ("Timeout Error:",err)
		"""