#import sys
#sys.path.append('woqlclient')

from  woqlclient import ConnectionConfig
from  woqlclient import ConnectionCapabilities
import pytest
from connectionObj import snapCapabilitiesObj
from serverRecordsFromCap import serverRecordsFromCap
from connectResponseForCapabilities import connect_response

url='http://localhost:6363/'
connectionConfig = ConnectionConfig(server=url)
jsonContext={"doc": "terminus:///terminus/document/",
        "layer": "http://terminusdb.com/schema/layer#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "ref": "http://terminusdb.com/schema/ref#",
        "repo": "http://terminusdb.com/schema/repository#",
        "terminus": "http://terminusdb.com/schema/terminus#",
        "vio": "http://terminusdb.com/schema/vio#",
        "woql": "http://terminusdb.com/schema/woql#",
        "xdd": "http://terminusdb.com/schema/xdd#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "scm": "http://my.old.man/is/a/walrus#"
    }
connection_capabilities = ConnectionCapabilities()
connection_capabilities.set_capabilities(connect_response)

class TestCapabilitiesActions:

    def test_connection_capability_object(self):
        print(connection_capabilities.connection)
        assert connection_capabilities.connection == snapCapabilitiesObj

    def test_form_resource_name(self):
        assert connection_capabilities._form_resource_name('TEST','admin') == "admin|TEST"
        assert connection_capabilities.find_resource_document_id('TEST','admin') == "doc:Database%5fadmin%7CTEST"

    def test_get_server_record(self):
        assert connection_capabilities._get_server_record() == serverRecordsFromCap

    def test_get_json_context(self):
        print(connection_capabilities.get_json_context())
        assert connection_capabilities.get_json_context() == jsonContext
