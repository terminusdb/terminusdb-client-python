import unittest
import sys
sys.path.append('../../terminus-client-python/src/woqlclient')

from woqlClient import WOQLClient

class test_get_schema:
    def getSchema(self):
        #configurable data
        __serverUrl__ = 'http://195.201.12.87:6363'
        __dbId__ = 'myFirstTerminusDB'
        __dbName__ = 'My First Terminus DB'
        __key__ = 'connectors wanna plans compressed'

        print('Fetching schema of db ' + __dbId__ + ' from ' + __serverUrl__)

        __woqlClient__ = WOQLClient()

        __result__ = __woqlClient__.directGetSchema( __serverUrl__ + '/' + __dbId__,
                                                     __key__,
                                                     options={"terminus:encoding": "terminus:turtle"})

        print("Result on getSchema")
        print(__result__)
        return

if __name__ == "__main__":
    class_name = test_get_schema()
    print(class_name.getSchema())
