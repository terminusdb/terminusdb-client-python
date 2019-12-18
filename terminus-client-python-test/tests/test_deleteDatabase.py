import unittest
import sys
sys.path.append('../../terminus-client-python/src/woqlclient')

from woqlClient import WOQLClient

class test_delete:
    def deleteDatabase(self):
        #configurable data
        __serverUrl__ = 'http://localhost:6363'
        __dbId__ = '000T'
        __key__ = 'root'

        print('Deleting database Id ' + __dbId__ + ' at ' + __serverUrl__)

        __woqlClient__ = WOQLClient()
        __result__ = __woqlClient__.directDeleteDatabase( __serverUrl__ + '/' + __dbId__,
                                                          __key__)

        print("Result on delete")
        print(__result__)
        return

if __name__ == "__main__":
    class_name = test_delete()
    print(class_name.deleteDatabase())
