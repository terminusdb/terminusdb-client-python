import pytest
import pprint
import json
from ..woqlquery.woql_query import WOQLQuery
from .woqljson.woqlJson import WoqlJson

class TestTripleBuilder:
    """
    def test_node(self):
        woqlObject = WOQLQuery().node("some_node", "add_quad")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(woqlObject)
        jsonStr = json.dumps(woqlObject)
        assert False
    """

    """
    def test_graph(self):
        woqlObject=WOQLQuery().node("a", "AddQuad").graph("schema/main");
        woqlObject2=WOQLQuery().node("doc:x", "add_quad").graph("schema/main").label("my label", "en");

        jsonObj={};
        assert woqlObject2 == WoqlJson.graphMethodJson
    """

    def test_node_and_label(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").label("my label", "en")
        woqlObject2 = WOQLQuery().node("doc:x", "add_quad").label("v:label")
        assert woqlObject.json() == WoqlJson.labelMethodJson
        assert woqlObject2.json() == WoqlJson.labelMethodJson2
