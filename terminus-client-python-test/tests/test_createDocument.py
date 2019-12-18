import unittest
import sys
sys.path.append('../../terminus-client-python/src/woqlclient')

from woqlClient import WOQLClient

class test_create_document:
    def createDocument(self):
        #configurable data
        __serverUrl__ = 'http://195.201.12.87:6363'
        __dbId__ = 'myFirstTerminusDB'
        __dbName__ = 'My First Terminus DB'
        __docId__ = 'Nose'
        __key__ = 'connectors wanna plans compressed'

        print('Creating document ' + __docId__ + ' in db ' + __dbId__ + ' from ' + __serverUrl__)

        __woqlClient__ = WOQLClient()

        __docObj__ = {
                   
                      "rdfs:label":[
                         {
                            "@value":"Kevin",
                            "@type":"xsd:string"
                         }
                      ],
                      "rdfs:comment":[
                         {
                            "@value":"Kevin is a person",
                            "@type":"xsd:string"
                         }
                      ],
                      "tcs:identity":[
                         {
                            "tcs:website":[
                               {
                                  "@value":"www.kevinMaster.com",
                                  "@type":"xdd:url"
                               }
                            ],
                            "@type":"tcs:Identifier",
                            "@id":"_:f89plh1570198207869"
                         }
                      ],
                      "@type":"http://terminusdb.com/schema/tcs#Group"
                  }

        #def directCreateDocument(docObj, documentID, dbURL, key):

        __result__ = __woqlClient__.directCreateDocument(__docObj__,
                                                      __docId__,
                                                      __serverUrl__ + '/' + __dbId__,
                                                      __key__)

        print("Result on getDocument")
        print(__result__)
        return

if __name__ == "__main__":
    class_name = test_create_document()
    print(class_name.createDocument())
