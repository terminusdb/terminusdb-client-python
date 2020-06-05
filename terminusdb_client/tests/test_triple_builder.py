import pytest
import pprint
import json
from terminusdb_client.woqlquery.woql_query import WOQLQuery, TripleBuilder
from .woqljson.woqlJson import WoqlJson

pp = pprint.PrettyPrinter(indent=4)

class TestTripleBuilder:

    def test_node_method(self):
        woqlObject = WOQLQuery().node("some_node", "add_quad")
        pp.pprint(woqlObject)
        assert woqlObject.json() == {}

    def test_graph_method(self):
        woqlObject=WOQLQuery().node("a", "AddQuad").graph("schema/main");
        woqlObject2=WOQLQuery().node("doc:x", "add_quad").graph("schema/main").label("my label", "en");

        assert woqlObject.json() == {}
        assert woqlObject2.json() == WoqlJson["graphMethodJson"]

    def test_node_and_label_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").label("my label", "en")
        woqlObject2 = WOQLQuery().node("doc:x", "add_quad").label("v:label")
        assert woqlObject.json() == WoqlJson["labelMethodJson"]
        assert woqlObject2.json() == WoqlJson["labelMethodJson2"]

    def test_add_class_and_description_method(self):
        woqlObject=WOQLQuery().add_class("NewClass").description("A new class object.")
        #pp.pprint(woqlObject._cursor)
        #print("-------")
        #pp.pprint(woqlObject.json())
        #print("-----")
        #pp.pprint(WoqlJson["addClassDescJson"])
        assert False
        #assert woqlObject.json() == WoqlJson["addClassDescJson"]
