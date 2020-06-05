import pprint

from terminusdb_client.woqlquery.woql_query import WOQLQuery

from .woqljson.woqlJson import WoqlJson

pp = pprint.PrettyPrinter(indent=4)


class TestTripleBuilder:
    def test_node_method(self):
        woqlObject = WOQLQuery().node("some_node", "add_quad")
        pp.pprint(woqlObject)
        assert woqlObject.json() == {}

    def test_graph_method(self):
        woqlObject = WOQLQuery().node("a", "AddQuad").graph("schema/main")
        woqlObject2 = (
            WOQLQuery()
            .node("doc:x", "add_quad")
            .graph("schema/main")
            .label("my label", "en")
        )

        assert woqlObject.json() == {}
        assert woqlObject2.json() == WoqlJson["graphMethodJson"]

    def test_node_and_label_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").label("my label", "en")
        woqlObject2 = WOQLQuery().node("doc:x", "add_quad").label("v:label")
        assert woqlObject.json() == WoqlJson["labelMethodJson"]
        assert woqlObject2.json() == WoqlJson["labelMethodJson2"]

    def test_add_class_and_description_method(self):
        WOQLQuery().add_class("NewClass").description("A new class object.")
        # pp.pprint(woqlObject._cursor)
        # print("-------")
        # pp.pprint(woqlObject.json())
        # print("-----")
        # pp.pprint(WoqlJson["addClassDescJson"])
        assert False
        # assert woqlObject.json() == WoqlJson["addClassDescJson"]

    def test_comment(self):
        woqlObject = WOQLQuery().comment("my comment")
        woqlObject01 = WOQLQuery().node("doc:x", "add_quad").comment("my comment")
        jsonObj = {
            "@type": "woql:Comment",
            "woql:comment": {"@type": "xsd:string", "@value": "my comment"},
            "woql:query": {},
        }
        assert woqlObject.json() == jsonObj

    def test_abstract_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").abstract()
        assert woqlObject.json() == WoqlJson["nodeAbstractJson"]

    def test_chained_doctype(self):
        woqlObject = (
            WOQLQuery()
            .doctype("MyDoc")
            .label("abc")
            .description("abcd")
            .property("prop", "dateTime")
            .label("aaa")
            .property("prop2", "integer")
            .label("abe")
        )
        assert woqlObject.json() == WoqlJson["chainDoctypeJson"]

    def test_chained_insert_method(self):
        woqlObject = (
            WOQLQuery()
            .insert("v:Node_ID", "v:Type")
            .label("v:Label")
            .description("v:Description")
            .property("prop", "v:Prop")
            .property("prop", "v:Prop2")
            .parent("myParentClass")
        )
        assert woqlObject.json() == WoqlJson["chainInsertJson"]

    def test_cardinality(self):
        woqlObject = WOQLQuery().add_property("P", "string").cardinality(3)
        assert woqlObject.json() == WoqlJson["propCardinalityJson"]

    def test_property_min(self):
        woqlObject = WOQLQuery().add_property("P", "string").min(2)
        assert woqlObject.json() == WoqlJson["propMinJson"]

    def test_max(self):
        woqlObject = WOQLQuery().add_property("P", "string").max(4)
        assert woqlObject.json() == WoqlJson["propertyMaxJson"]

    def test_node_property(self):
        woqlObject = WOQLQuery().node("doc:x", "add_triple").property("myprop", "value")
        assert woqlObject.json() == WoqlJson["addNodePropJson"]

    def test_node_parent(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").parent("classParentName")
        assert woqlObject.json() == WoqlJson["nodeParentJson"]

    def test_class_description(self):
        woqlObject = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        assert woqlObject.json() == WoqlJson["addClassDescJson"]
