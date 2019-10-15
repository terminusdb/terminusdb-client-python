import json

class createDatabaseTemplate:

	def __init__(self,server,dbID,label,comment:None):
		self.__server=server
		self.__dbID=dbID
		self.__label=label
		self.__comment=comment
		self.__language=language
		self.__language='en'
		self.__allow_origin='*'

    @property
    def language(self):
        return self.__language

    @language.setter(self,value):
    	self.__language=value

    @property
    def allow_origin(self):
        return self.__language

    @allow_origin.setter(self,value):
    	self.__allow_origin=value


	def getTemplate(self):
		temp= {"@context": {
					"rdfs": "http://www.w3.org/2000/01/rdf-schema#",
					"terminus": "http://terminusdb.com/schema/terminus#",
					"_": "%s%s" % (self.__server,self.__dbID)
				  },
				  "terminus:document": {
					"@type": "terminus:Database",
					"rdfs:label": {
					  "@language": self.__language,
					  "@value": self.__label
					},
					"terminus:allow_origin": {
					  "@type": "xsd:string",
					  "@value": self.__allow_origin
					},
					"@id": "%s%s" % (self.__server,self.__dbID)
				  },
				  "@type": "terminus:APIUpdate"
				}
		if(self.__comment):
			temp["rdfs:comment"]= { "@language": self.__language, "@value":  self.__comment}
		return temp

