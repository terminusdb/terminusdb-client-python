import unittest
import sys
sys.path.append('../../terminus-client-python/src/woqlclient')

from woqlClient import WOQLClient

class test_get_document:
    def getDocument(self):
        #configurable data
        __serverUrl__ = 'http://195.201.12.87:6363'
        __dbId__ = 'myFirstTerminusDB'
        __dbName__ = 'My First Terminus DB'
        __docId__ = 'Sammy'
        __key__ = 'connectors wanna plans compressed'

        print('Fetching document ' + __docId__ + ' of db ' + __dbId__ + ' from ' + __serverUrl__)

        __woqlClient__ = WOQLClient()

        __result__ = __woqlClient__.directGetDocument(__docId__,
                                                      __serverUrl__ + '/' + __dbId__,
                                                      __key__,
                                                      opts={"terminus:encoding": "terminus:frame"})

        print("Result on getDocument")
        print(__result__)
        return

if __name__ == "__main__":
    class_name = test_get_document()
    print(class_name.getDocument())
