import unittest
import sys
sys.path.append('../../terminus-client-python/src/woqlclient')

from woqlClient import WOQLClient

class test_create:
    def createDatabase(self):
        #configurable data
        __serverUrl__ = 'http://localhost:6363'
        __dbId__ = 'test05'
        __dbName__ = 'Test 05'
        __dbDescr__ = 'Testing create db using python client'
        __key__ = 'root'

        print('Creating database Id ' + __dbId__ + ' at ' + __serverUrl__)

        __woqlClient__ = WOQLClient()
        __result__ = __woqlClient__.directCreateDatabase( __serverUrl__ + '/' + __dbId__,
                                                          __dbName__,
                                                          __key__,
                                                          comment = __dbDescr__)

        print("Result on create")
        print(__result__)
        return

if __name__ == "__main__":
    class_name = test_create()
    print(class_name.createDatabase())
