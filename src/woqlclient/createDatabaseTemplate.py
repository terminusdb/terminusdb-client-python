import json

class CreateDBTemplate:
	def __init__(self):
		pass

	@staticmethod
	def getTemplate(server,dbID,label,**kwargs):
		dbURL="%s%s" % (server,dbID)
		comment=kwargs.get('comment')
		language=kwargs.get('language', 'en')
		allow_origin=kwargs.get('allow_origin', '*')

		temp= {"@context": {
					"rdfs": "http://www.w3.org/2000/01/rdf-schema#",
					"terminus": "http://terminusdb.com/schema/terminus#",
					"_": dbURL
				  },
				  "terminus:document": {
					"@type": "terminus:Database",
					"rdfs:label": {
					  "@language": language,
					  "@value": label
					},
					"terminus:allow_origin": {
					  "@type": "xsd:string",
					  "@value": allow_origin
					},
					"@id": dbURL
				  },
				  "@type": "terminus:APIUpdate"
				}
		if(comment):
			temp["rdfs:comment"]= { "@language": language, "@value":  comment}
		return temp

