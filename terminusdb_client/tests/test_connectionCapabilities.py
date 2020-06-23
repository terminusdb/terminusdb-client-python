import pytest
from terminusdb_client.woqlclient.connectionCapabilities import ConnectionCapabilities

from .AllServerRecords import AllServerRecords
from .connectCapabilitiesResponse import ConnectResponse
from .connectionObjDump import ConnectionDump
from .DBRecord import db_record_obj
from .serverRecordsFromCap import server_records_from_cap

url = "http://localhost:6363/"
json_context = {
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
}

dbrec = {
    "db": "aaaaaa",
    "account": "admin",
    "title": "admin|aaaaaa",
    "description": "dasdasdds",
}

dbrecs = [
    {"db": "5534534", "account": "admin", "title": "3453", "description": "345345"},
    {
        "db": "adsasasddsa",
        "account": "admin",
        "title": "admin|adsasasddsa",
        "description": "asdsadsda",
    },
    {"db": "blah", "account": "admin", "title": "admin|blah", "description": "adfadf"},
    {
        "db": "daassd",
        "account": "admin",
        "title": "admin|daassd",
        "description": "asdasdsd",
    },
    {
        "db": "dassadds",
        "account": "admin",
        "title": "admin|dassadds",
        "description": "asdsdsad",
    },
    {"db": "ddd", "account": "admin", "title": "admin|ddd", "description": "ddds"},
    {"db": "ffff", "account": "admin", "title": "admin|ffff", "description": "fffff"},
    {
        "db": "fffffff",
        "account": "admin",
        "title": "admin|fffffff",
        "description": "fff",
    },
    {
        "db": "ggggggggg",
        "account": "admin",
        "title": "admin|ggggggggg",
        "description": "gg",
    },
    {
        "db": "twretwert",
        "account": "admin",
        "title": "admin|twretwert",
        "description": "adfadf",
    },
    {
        "db": "terminus",
        "account": "",
        "title": "Master Database",
        "description": "The master database contains the meta-data about databases, users and roles",
    },
]

connection_capabilities = ConnectionCapabilities()
connection_capabilities.set_capabilities(ConnectResponse)


class TestCapabilitiesActions:
    def test_connection_capability_object(self):
        assert connection_capabilities.connection == ConnectionDump

    def test_form_resource_name(self):
        assert (
            connection_capabilities._form_resource_name("aaaaaa", "admin")
            == "admin|aaaaaa"
        )
        assert (
            connection_capabilities.find_resource_document_id("aaaaaa", "admin")
            == "doc:Database%5fadmin%7Caaaaaa"
        )

    def test_get_server_record(self):
        x = connection_capabilities._get_server_record()
        assert x == server_records_from_cap

    def test_get_json_context(self):
        assert connection_capabilities.get_json_context() == json_context

    def test_capabilities_permit(self):
        assert connection_capabilities.capabilities_permit(
            "create_database", "aaaaaa", "admin"
        )
        with pytest.raises(Exception):
            assert connection_capabilities.capabilities_permit(
                "delete_database", "nonexistant", "admin"
            )

    def test_get_db_record(self):
        assert (
            connection_capabilities._get_db_record("aaaaaa", "admin") == db_record_obj
        )

    def test_extract_metadata(self):
        assert connection_capabilities._extract_metadata(db_record_obj) == dbrec

    def test_get_db_metadata(self):
        assert connection_capabilities._get_db_metadata("aaaaaa", "admin") == dbrec

    def test_remove_db(self):
        connection_capabilities.remove_db("aaaaaa", "admin")
        with pytest.raises(Exception):
            assert connection_capabilities._get_db_metadata("aaaaaa", "admin")

    def test_get_server_db_records(self):
        x = connection_capabilities.get_server_db_records()
        assert x == AllServerRecords

    def test_get_server_db_metadata(self):
        x = connection_capabilities.get_server_db_metadata()
        assert x == dbrecs
