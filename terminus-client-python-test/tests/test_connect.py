import unittest
import sys
sys.path.append('../../terminus-client-python/src/woqlclient')

from woqlClient import WOQLClient

class test_connect:
    def connect(self):

        #configurable data
        __serverUrl__ = 'http://localhost:8080'
        __key__ = 'root'

        print('Connecting to ' + __serverUrl__)

        __woqlClient__ = WOQLClient()
        __result__ = __woqlClient__.connect(__serverUrl__,
                                            __key__)

        print("Result on connect")
        print(__result__)

        return

if __name__ == "__main__":
    class_name = test_connect()
    print(class_name.connect())
