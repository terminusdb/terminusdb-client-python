# idParser.py

#  Helper class for parsing and decomposing Terminus URLs /
#  dealing with prefixed URLs
# package_dir={'src': 'woqlclient'},
import re

class IDParser:
	"""Implements a socket stream."""
	def __init__(self,context=None):
		self._context=context
		self._server_url=False
		self._db=False
		self._doc=False

	@property
	def serverURL(self):
		return self._server_url

	@property
	def dbID(self):
		return self._db

	@property
	def docID(self):
		return self._doc

	def validURL(self,strURL):
		if(isinstance(strURL,str)==False):
			return False
		regex = re.compile(
	    r'^(?:http)s?://' # http:// or https://
	    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
	    r'localhost|' # localhost...
	    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
	    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
	    r'(?::\d+)?' # optional port
	    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

		if re.match(regex, strURL) is not None:
			return True
		return False

	def parseServerURL(self,strURL):
		self._server_url=False;

		if (self.validURL(strURL)):
			self._server_url = strURL
		elif (self._context and self.__validPrefixedURL(strURL, self._context)):
			self._server_url = self.__expandPrefixed(strURL, self._context)
	
		if (self._server_url and self._server_url.rfind('/') != (len(self._server_url) - 1)):
			self._server_url= self._server_url + '/'

		print('IDParser'+self._server_url)
		return self._server_url;


    # @param {string} str Terminus server URI or a TerminusID or None
	def parseDBID(self, strDBID):
		self._db=False
		if (self._context and self.__validPrefixedURL(strDBID, self._context)):
			strDBID = self.__expandPrefixed(strDBID, self._context)

		if (self.validURL(strDBID)):
			if (strDBID.find('/') == (len(strDBID)- 1)):
				strDBID = strDBID[0:(len(strDBID) - 1)] # trim trailing slash
				
			serverUrl = strDBID[0:strDBID.rfind('/')]
			dbid = strDBID[(strDBID.rfind('/') + 1):];
			if (self.parseServerURL(serverUrl)):
				self._db = dbid
		
		elif (self.__validIDString(strDBID)):
			self._db = strDBID;

		return self._db

	# @param {string} docName Terminus Document URL or Terminus Document ID
	def parseDocumentURL(self,docName):
		self._doc=False;
		if (self._context and self.__validPrefixedURL(docName, self._context)):
			docName = self.__expandPrefixed(docName, self._context)

		if (self.validURL(docName)):
			docPos=docName.rfind('/document/')
			if (docPos != -1):				
				docURL = docName[0: docPos]
				docName = docName[docPos+10:]
				if(self.parseDBID(docURL)==False):return False

		if (self.__validIDString(docName)):
			self._doc = docName

		return self._doc


	def parseSchemaURL(self,schemaURL):
		if (self._context and self.__validPrefixedURL(schemaURL, self._context)):
			schemaURL = self.__expandPrefixed(schemaURL, self._context)
	
		if (self.validURL(schemaURL)):
			schemaURL = self.__stripOptionalPath(schemaURL, 'schema')
	
		return self.parseDBID(schemaURL)


	def parseQueryURL(self,queryURL):
		if (self._context and self.__validPrefixedURL(queryURL, self._context)):
			queryURL = self.__expandPrefixed(queryURL, self._context)

		if (self.validURL(queryURL)):
			queryURL = self.__stripOptionalPath(queryURL, 'woql')
			queryURL = self.__stripOptionalPath(queryURL, 'query')

		return self.parseDBID(queryURL)


	def parseClassFrameURL(self,frameURL):
		if(self._context and self.__validPrefixedURL(frameURL, self._context)):
			frameURL = self.__expandPrefixed(frameURL, self._context)
		
		if (self.validURL(frameURL)):
			frameURL = self.__stripOptionalPath(frameURL, 'schema')

		return self.parseDBID(frameURL)


	def __stripOptionalPath(self, strOp, bit):
		if (strOp.find(bit) != -1): 
			strOp = strOp[0:strOp.find(bit)];
		return strOp;

	def __validPrefixedURL(self,preURL,context=None):
		if(isinstance(preURL,preURL)==False):return False
		parts = preURL.split(':')
		if (len(parts)!= 2): return False
		if (len(parts[0]) < 1 or len(parts[1]) < 1): return False
		if (context and context[parts[0]] and self.__validIDString(parts[1])): return True
		return False

	def __validIDString(self,strID): 
		if (strID.find(' ') != -1 or strID.find('/') != -1): return False
		return True

	def __expandPrefixed(self, strPre, context):
		parts = strPre.split(':')
		return context[parts[0]] + parts[1]



