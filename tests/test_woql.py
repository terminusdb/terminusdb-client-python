import pytest
from woqlclient import WOQLQuery

class TestWoqlQueries:

    def test_start_properties_values(self):
        woqlObject = WOQLQuery()
        assert woqlObject.chain_ended == False
        assert woqlObject.contains_update == False
        assert woqlObject.vocab['type'] == 'rdf:type'

    def test_limit_method(self):
        woqlObject = WOQLQuery().limit(10)
        assert woqlObject.json()['limit'][0] == 10
        assert woqlObject.json() == { 'limit': [ 10, {} ] }

    def test_start_method(self):
        woqlObject = WOQLQuery().limit(10).start(0)
        jsonObj = {"limit": [10,{"start": [0,{}]}]}
        assert woqlObject.json() == jsonObj

    def test_insert_method(self):
        woqlObject = WOQLQuery().insert("v:Bike_URL", "Bicycle")
        woqlObjectDB = WOQLQuery().insert("v:Bike_URL", "Bicycle", "myDB")
        jsonObj = { "add_triple": [ 'v:Bike_URL', 'rdf:type', 'scm:Bicycle' ] }
        jsonObjDB={ "add_quad": [ 'v:Bike_URL', 'rdf:type', 'scm:Bicycle', 'db:myDB' ] }
        assert woqlObject.json() == jsonObj
        assert woqlObjectDB.json() == jsonObjDB

    def test_doctype_method(self):
        woqlObject = WOQLQuery().doctype("Station")
        jsonObj = { "and": [
                    { "add_quad": ["scm:Station",
                    "rdf:type",
                    "owl:Class",
                    "db:schema"] },
                    { "add_quad": ["scm:Station",
                    "rdfs:subClassOf",
                    "tcs:Document",
                    "db:schema"] }
                   ] }
        assert woqlObject.json() == jsonObj

    def test_woql_not_method(self):
        woqlObject = WOQLQuery().woql_not(WOQLQuery().triple("a", "b", "c"))
        woqlObjectChain = WOQLQuery().woql_not().triple("a", "b", "c")
        jsonObj={ 'not': [ { 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] } ] }

        print(woqlObject.json())

        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_woql_and_method(self):
        woqlObject=WOQLQuery().woql_and(WOQLQuery().triple("a", "b", "c"),
                                    WOQLQuery().triple("1", "2", "3"))
        jsonObj={ 'and': [ { 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] }, { 'triple': [ "doc:1", "scm:2", { "@language": "en", "@value": "3" } ] } ] }

        assert woqlObject.json() == jsonObj

    def test_woql_or_method(self):
        woqlObject=WOQLQuery().woql_or(WOQLQuery().triple("a", "b", "c"),
                                    WOQLQuery().triple("1", "2", "3"))
        jsonObj={ 'or': [ { 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] }, { 'triple': [ "doc:1", "scm:2", { "@language": "en", "@value": "3" } ] } ] }

        assert woqlObject.json() == jsonObj

    def test_when_method(self):

        woqlObject=WOQLQuery().when(True, WOQLQuery().add_class("id"))
        woqlObjectChain=WOQLQuery().when(True).add_class("id")
        jsonObj={'when': [
                        {"true":[]},
                        {'add_quad': [ 'scm:id', 'rdf:type', 'owl:Class', 'db:schema' ]}
                      ] }

        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_opt_method(self):

        woqlObject=WOQLQuery().opt(WOQLQuery().triple("a", "b", "c"))
        woqlObjectChain=WOQLQuery().opt().triple("a", "b", "c")

        jsonObj={ 'opt': [ { 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] } ] }

        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_woql_from_method(self):
        woql_original=WOQLQuery().limit(10)
        woqlObject=WOQLQuery().woql_from("http://dburl", woql_original)
        woqlObjectChain=WOQLQuery().woql_from("http://dburl").limit(10)

        jsonObj={ 'from': [ 'http://dburl', { 'limit': [ 10, {} ] } ] }

        #assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_star_method(self):
        woqlObject=WOQLQuery().limit(10).star()
        jsonObj={ 'limit': [ 10, { "triple": [
                      "v:Subject",
                      "v:Predicate",
                      "v:Object"
                    ] } ] }
        assert woqlObject.json() == jsonObj

    def test_select_method(self):
        woqlObject=WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"));
        woqlObjectMultiple=WOQLQuery().select("V1", "V2", WOQLQuery().triple("a", "b", "c"));
        woqlObjectChain=WOQLQuery().select("V1").triple("a", "b", "c");
        woqlObjectChainMultiple=WOQLQuery().select("V1","V2").triple("a", "b", "c");

        jsonObj={ 'select': [ 'V1', { 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] } ] }
        jsonObjMultiple={ 'select': [ 'V1', 'V2', { 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] } ] }

        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj
        assert woqlObjectMultiple.json() == jsonObjMultiple
        assert woqlObjectChainMultiple.json() == jsonObjMultiple

    def test_eq_method(self):
        woqlObject=WOQLQuery().eq("a","b")
        jsonObj={ 'eq': [ { "@language": "en", "@value": "a" },
                        { "@language": "en", "@value": "b" } ] }
        assert woqlObject.json() == jsonObj

    def test_trim_method(self):
        woqlObject=WOQLQuery().trim("a","b")
        jsonObj={ 'trim': [ "a", "b" ] }
        assert woqlObject.json() == jsonObj

    def test_eval_method(self):
        woqlObject=WOQLQuery().eval("1+2","b")
        jsonObj={ 'eval': [ '1+2', 'b' ] }
        assert woqlObject.json() == jsonObj

    def test_minus_method(self):
        woqlObject=WOQLQuery().minus("2","1")
        jsonObj={ 'minus': [ '2', '1' ] }
        assert woqlObject.json() == jsonObj

    def test_plus_method(self):
        woqlObject=WOQLQuery().plus("2","1")
        jsonObj={ 'plus': [ '2', '1' ] }
        assert woqlObject.json() == jsonObj

    def test_times_method(self):
        woqlObject=WOQLQuery().times("2","1")
        jsonObj={ 'times': [ '2', '1' ] }
        assert woqlObject.json() == jsonObj

    def test_divide_method(self):
        woqlObject=WOQLQuery().divide("2","1")
        jsonObj={ 'divide': [ '2', '1' ] }
        assert woqlObject.json() == jsonObj

    def test_exp_method(self):
        woqlObject=WOQLQuery().exp("2","1")
        jsonObj={ 'exp': [ '2', '1' ] }
        assert woqlObject.json() == jsonObj

    def test_div_method(self):
        woqlObject=WOQLQuery().div("2","1")
        jsonObj={ 'div': [ '2', '1' ] }
        assert woqlObject.json() == jsonObj

    def test_get_method(self):
        woqlObject=WOQLQuery().get("Map", "Target")
        jsonObj={ 'get': [[], {}] }
        assert woqlObject.json() == jsonObj

    def test_woql_as_method(self):
        woqlObject=WOQLQuery().woql_as("Source", "Target")
        woqlObject2=WOQLQuery().woql_as("Source", "Target").woql_as("Source2", "Target2")
        jsonObj=[{ 'as': [ { '@value': 'Source' }, 'v:Target' ] }]
        jsonObj2 =[{ 'as': [ { '@value': 'Source' }, 'v:Target' ] },
                   { 'as': [ { '@value': 'Source2' }, 'v:Target2' ] }]

        assert woqlObject.json() == jsonObj
        assert woqlObject2.json() == jsonObj2

    def test_remote_method(self):
        woqlObject=WOQLQuery().remote({'url': "http://url"})
        jsonObj={ 'remote': [ { 'url': 'http://url' } ] }
        assert woqlObject.json() == jsonObj

    def test_post_method(self):
        woqlObject=WOQLQuery().post("my_json_file",{'type': "panda_json"})
        jsonObj={"post":["my_json_file",  {"type":"panda_json"} ]}
        assert woqlObject.json() == jsonObj

    def test_idgen_method(self):
        woqlObject=WOQLQuery().idgen("doc:Station",["v:Start_ID"],"v:Start_Station_URL")
        jsonObj={ "idgen": [ 'doc:Station', { "list": ["v:Start_ID"] }, 'v:Start_Station_URL' ] }
        assert woqlObject.json() == jsonObj

    def test_typecast_method(self):
        woqlObject=WOQLQuery().typecast("v:Duration", "xsd:integer", "v:Duration_Cast")
        jsonObj={ "typecast": [ "v:Duration", "xsd:integer", "v:Duration_Cast" ] }
        assert woqlObject.json() == jsonObj

    def test_cast_method(self):
        woqlObject=WOQLQuery().cast("v:Duration", "xsd:integer", "v:Duration_Cast")
        jsonObj={ "typecast": [ "v:Duration", "xsd:integer", "v:Duration_Cast" ] }
        assert woqlObject.json() == jsonObj

    def test_re_method(self):
        woqlObject=WOQLQuery().re(".*", "v:string", "v:formated")
        jsonObj={
                're': [
                  { '@value': '.*', '@type': 'xsd:string' },
                  'v:string',
                  { 'list': ["v:formated"] }
                ]
              }
        assert woqlObject.json() == jsonObj

    def test_join_method(self):
        woqlObject=WOQLQuery().join(["v:A_obj", "v:B_obj"], ", ", "v:output")
        jsonObj={'join': [
                  [ 'v:A_obj', 'v:B_obj' ],
                  { '@value': ', ', '@type': 'xsd:string' },
                  'v:output'
                  ]
                }
        assert woqlObject.json() == jsonObj

    def test_split_method(self):
        woqlObject=WOQLQuery().split("A, B, C", ", ", "v:list_obj")
        jsonObj={'split': [
                    { '@value': 'A, B, C', '@type': 'xsd:string' },
                    {"@type": "xsd:string", "@value": ", "},
                    "v:list_obj"
                    ]
                }
        assert woqlObject.json() == jsonObj

    def test_member_method(self):
        woqlObject=WOQLQuery().member("v:member", "v:list_obj")
        jsonObj={ 'member': [ 'v:member', 'v:list_obj' ] }
        assert woqlObject.json() == jsonObj

    def test_concat_method(self):
        woqlObject=WOQLQuery().concat("v:Duration yo v:Duration_Cast", "x")
        jsonObj={ "concat": [ { "list": ["v:Duration", {"@value": " yo ", "@type": "xsd:string"}, "v:Duration_Cast" ]}, "v:x"] }
        assert woqlObject.json() == jsonObj

    def test_list_method(self):
        woqlObject=WOQLQuery().list(["V1","V2"])
        jsonObj={ 'list': [ [ 'V1', 'V2' ] ] }
        assert woqlObject.json() == jsonObj

    def test_group_by_method(self):
        woqlObject=WOQLQuery().group_by(["v:A", "v:B"],["v:C"],"v:New")
        jsonObj={ "group_by": [ {"list": ['v:A', "v:B"]}, {"list": ["v:C"]}, {},  "v:New"] }
        assert woqlObject.json() == jsonObj

    def test_order_by_method(self):
        woqlObject=WOQLQuery().order_by([WOQLQuery().asc("v:B")])
        jsonObj={ "order_by": [ [{"asc": ['v:B']}], {} ] }
        assert woqlObject.json() == jsonObj

    def test_order_by_method_desc(self):
        desc=[WOQLQuery().desc("v:C"), WOQLQuery().desc("v:A")]
        woqlObject=WOQLQuery().order_by(desc)
        jsonObj={ "order_by": [ [ {"desc": ['v:C']}, {"desc" : ["v:A"]} ], {} ] }
        assert woqlObject.json() == jsonObj


class TestTripleBuilder:

    def test_triple_method(self):
        woqlObject=WOQLQuery().triple("a", "b", "c")
        jsonObj={ 'triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] }
        assert woqlObject.json() == jsonObj

    def test_quad_method(self):
        woqlObject=WOQLQuery().quad("a", "b", "c", "d")
        jsonObj={ 'quad': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" }, "db:d" ] }
        assert woqlObject.json() == jsonObj

    def test_add_class_method(self):
        woqlObject=WOQLQuery().add_class("id")
        jsonObj={ 'add_quad': [ 'scm:id', 'rdf:type', 'owl:Class', 'db:schema' ] }
        assert woqlObject.json() == jsonObj

    def test_delete_class_method(self):
        woqlObject=WOQLQuery().delete_class("id")
        jsonObj= { 'and': [
          { 'delete_quad': [ 'scm:id', 'v:All', 'v:Al2', 'db:schema' ] },
          { 'opt': [ { 'delete_quad': [ 'v:Al3', 'v:Al4', 'scm:id', 'db:schema' ] } ] }
          ] }
        assert woqlObject.json() == jsonObj

    def test_sub_method(self):
        woqlObject=WOQLQuery().sub("ClassA","ClassB")
        jsonObj={ 'sub': [ "scm:ClassA", "scm:ClassB" ] }
        assert woqlObject.json() == jsonObj

    def test_isa_methos(self):
        woqlObject=WOQLQuery().isa("instance","Class")
        jsonObj={ 'isa': [ "scm:instance", "owl:Class" ] }
        assert woqlObject.json() == jsonObj

    def test_delete_method(self):
        woqlObject=WOQLQuery().delete({ 'triple': [ "doc:a",
                                                    "scm:b",
                                                    { "@language": "en", "@value": "c" } ] })
        jsonObj={ 'delete': [ { 'triple': [ "doc:a",
                                            "scm:b",
                                            { "@language": "en", "@value": "c" } ] } ] }
        assert woqlObject.json() == jsonObj

    def test_delete_triple_method(self):
        woqlObject=WOQLQuery().delete_triple("a", "b", "c")
        jsonObj={ 'delete_triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] }
        assert woqlObject.json() == jsonObj

    def test_delete_quad_method(self):
        woqlObject=WOQLQuery().delete_quad("a", "b", "c", "d")
        jsonObj={ 'delete_quad': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" }, "db:d" ] }
        assert woqlObject.json() == jsonObj

    def test_add_triple_method(self):
        woqlObject=WOQLQuery().add_triple("a", "b", "c")
        jsonObj={ 'add_triple': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" } ] }
        assert woqlObject.json() == jsonObj

    def test_add_quad_method(self):
        woqlObject=WOQLQuery().add_quad("a", "b", "c", "d")
        jsonObj={ 'add_quad': [ "doc:a", "scm:b", { "@language": "en", "@value": "c" }, "db:d" ] }
        assert woqlObject.json() == jsonObj

    def test_add_property_methof(self):
        woqlObject=WOQLQuery().add_property("some_property", "string")
        jsonObj={ 'and': [ { 'add_quad': [ 'scm:some_property', 'rdf:type', 'owl:DatatypeProperty', 'db:schema' ] }, { 'add_quad': [ 'scm:some_property', 'rdfs:range', 'xsd:string', 'db:schema' ] } ] }
        print(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_delete_property_method(self):
        woqlObject=WOQLQuery().delete_property("some_property", "string")
        jsonObj={ 'and': [ { 'delete_quad': [ 'scm:some_property', 'v:All', 'v:Al2', 'xsd:string' ] }, { 'delete_quad': [ 'v:Al3', 'v:Al4', 'scm:some_property', 'xsd:string' ] } ] }
        assert woqlObject.json() == jsonObj


class TestTripleBuilderChainer:

    def test_node_method(self):
        woqlObject=WOQLQuery().node("some_node")
        jsonObj={}
        assert woqlObject.json() == jsonObj

    def test_graph_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").graph("db:schema")
        woqlObject2=WOQLQuery().node("doc:x", "add_quad").graph("db:mySchema").label("my label", "en")
        jsonObj={}
        jsonObj2={ 'add_quad': ['doc:x', 'rdfs:label', { '@value': 'my label', '@language': 'en' }, 'db:mySchema'] }

        assert woqlObject.json() == jsonObj
        assert woqlObject2.json() == jsonObj2

    def test_label_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").label("my label", "en")
        woqlObject2=WOQLQuery().node("doc:x", "add_quad").label("v:label")
        jsonObj={ 'add_quad': ['doc:x', 'rdfs:label', { '@value': 'my label', '@language': 'en' }, 'db:schema'] }
        jsonObj2={ 'add_quad': ['doc:x', 'rdfs:label', "v:label", 'db:schema'] }
        assert woqlObject.json() == jsonObj
        assert woqlObject2.json() == jsonObj2

    def test_again_add_class_method(self):
        woqlObject=WOQLQuery().add_class("NewClass").description("A new class object.").entity()
        jsonObj={ "and": [{"add_quad": ['scm:NewClass', 'rdf:type', "owl:Class", 'db:schema']},
                      {"add_quad": ['scm:NewClass', 'rdfs:comment', { '@value': "A new class object.", '@language': 'en' }, 'db:schema']},
                      {"add_quad": ['scm:NewClass', 'rdfs:subClassOf', "tcs:Entity", 'db:schema']}
                ]}
        print(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_comment_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").comment("my comment")
        jsonObj={ "comment": [
                {"@language": "en",
                  "@value": "my comment"},
                {}
                ] }
        assert woqlObject.json() == jsonObj

    def test_property_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").property("myprop", "value")
        jsonObj={ 'add_quad': ['doc:x',
                              'scm:myprop',
                              { '@value': 'value', '@language': 'en' },
                              'db:schema'] }
        assert woqlObject.json() == jsonObj

    def test_entity_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").entity()
        jsonObj={ 'add_quad': [ 'doc:x', 'rdfs:subClassOf', 'tcs:Entity', 'db:schema' ] }
        assert woqlObject.json() == jsonObj

    def test_parent_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").parent("Z")
        jsonObj={ 'add_quad': [ 'doc:x', 'rdfs:subClassOf', 'scm:Z', 'db:schema' ] }
        assert woqlObject.json() == jsonObj

    def test_abstract_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").abstract()
        jsonObj={ 'add_quad': [ 'doc:x', 'tcs:tag', 'tcs:abstract', 'db:schema' ] }
        assert woqlObject.json() == jsonObj

    def test_relationship_method(self):
        woqlObject=WOQLQuery().node("doc:x", "add_quad").relationship()
        jsonObj={ 'add_quad': [ 'doc:x', 'rdfs:subClassOf', 'tcs:Entity', 'db:schema' ] }
        assert woqlObject.json() == jsonObj

    def test_max_method(self):
        woqlObject=WOQLQuery().add_property("P", "string").max(4)
        jsonObj={ "and": [ { "add_quad": ["scm:P",
                                            "rdf:type",
                                            "owl:DatatypeProperty",
                                            "db:schema"] },
                               { "add_quad": ["scm:P",
                                            "rdfs:range",
                                            "xsd:string",
                                            "db:schema"] },
                               { "add_quad": ["scm:P_max",
                                            "rdf:type",
                                            "owl:Restriction",
                                            "db:schema"] },
                               { "add_quad": [ "scm:P_max",
                                            "owl:onProperty",
                                            "scm:P",
                                            "db:schema"] },
                               { "add_quad": [ "scm:P_max",
                                            "owl:maxCardinality",
                                            { "@value": 4, "@type": "xsd:nonNegativeInteger" },
                                            "db:schema"] } ] }
        assert woqlObject.json() == jsonObj

    def test_min_method(self):
        woqlObject=WOQLQuery().add_property("P", "string").min(2)
        jsonObj={ "and": [ { "add_quad": ["scm:P",
                                            "rdf:type",
                                            "owl:DatatypeProperty",
                                            "db:schema"] },
                                 { "add_quad": ["scm:P",
                                            "rdfs:range",
                                            "xsd:string",
                                            "db:schema"] },
                                 { "add_quad": ["scm:P_min",
                                            "rdf:type",
                                            "owl:Restriction",
                                            "db:schema"] },
                                 { "add_quad": [ "scm:P_min",
                                            "owl:onProperty",
                                            "scm:P",
                                            "db:schema"] },
                                 { "add_quad": [ "scm:P_min",
                                            "owl:minCardinality",
                                            { "@value": 2, "@type": "xsd:nonNegativeInteger" },
                                            "db:schema"] } ] }
        assert woqlObject.json() == jsonObj

    def test_cardinality_method(self):
        woqlObject=WOQLQuery().add_property("P", "string").cardinality(3)
        jsonObj={ "and": [ { "add_quad": ["scm:P",
                                              "rdf:type",
                                              "owl:DatatypeProperty",
                                              "db:schema"] },
                                 { "add_quad": ["scm:P",
                                              "rdfs:range",
                                              "xsd:string",
                                              "db:schema"] },
                                 { "add_quad": ["scm:P_cardinality",
                                              "rdf:type",
                                              "owl:Restriction",
                                              "db:schema"] },
                                 { "add_quad": [ "scm:P_cardinality",
                                              "owl:onProperty",
                                              "scm:P",
                                              "db:schema"] },
                                 { "add_quad": [ "scm:P_cardinality",
                                              "owl:cardinality",
                                              { "@value": 3, "@type": "xsd:nonNegativeInteger" },
                                              "db:schema"] } ] }
        assert woqlObject.json() == jsonObj

    def test_chained_insert_method(self):
        woqlObject = WOQLQuery().insert("v:Node_ID", "v:Type").\
                    label("v:Label").\
                    description("v:Description").\
                    property("prop", "v:Prop").\
                    property("prop", "v:Prop2").\
                    entity().parent("hello")
        jsonObj={ 'and': [
             { 'add_triple': ["v:Node_ID", "rdf:type", "v:Type"] },
             { 'add_triple': ["v:Node_ID", "rdfs:label", "v:Label"] },
             { 'add_triple': ["v:Node_ID", "rdfs:comment", "v:Description"] },
             { 'add_triple': ["v:Node_ID", "scm:prop", "v:Prop"] },
             { 'add_triple': ["v:Node_ID", "scm:prop", "v:Prop2"] },
             { 'add_triple': ["v:Node_ID", "rdfs:subClassOf", "tcs:Entity"] },
             { 'add_triple': ["v:Node_ID", "rdfs:subClassOf", "scm:hello"] }
        ]}
        assert woqlObject.json() == jsonObj

    def test_chained_doctype_method(self):
        woqlObject = WOQLQuery().doctype("MyDoc").\
                    label("abc").description("abcd").\
                    property("prop", "dateTime").label("aaa").\
                    property("prop2", "integer").label("abe")
        jsonObj={ 'and': [
        { 'add_quad': ["scm:prop2", "rdf:type", "owl:DatatypeProperty", "db:schema"] },
        { 'add_quad': ["scm:prop2", "rdfs:range", "xsd:integer", "db:schema"] },
        { 'add_quad': ["scm:prop2", "rdfs:domain", "scm:MyDoc", "db:schema"] },
        { 'and': [
            { 'add_quad': ["scm:prop", "rdf:type", "owl:DatatypeProperty", "db:schema"] },
            { 'add_quad': ["scm:prop", "rdfs:range", "xsd:dateTime", "db:schema"] },
            { 'add_quad': ["scm:prop", "rdfs:domain", "scm:MyDoc", "db:schema"] },

            { 'and': [
            { 'add_quad': ["scm:MyDoc", "rdf:type", "owl:Class", "db:schema"] },
            { 'add_quad': ["scm:MyDoc", "rdfs:subClassOf", "tcs:Document", "db:schema"] },
            { "add_quad": ["scm:MyDoc", "rdfs:label", {"@value": "abc", "@language": "en"}, "db:schema"] },
            { "add_quad": ["scm:MyDoc", "rdfs:comment", {"@value": "abcd", "@language": "en"}, "db:schema"] }
        ]},
        { "add_quad": ["scm:prop", "rdfs:label", {"@value": "aaa", "@language": "en"}, "db:schema"] }
        ]},
        { "add_quad": ["scm:prop2", "rdfs:label", {"@value": "abe", "@language": "en"}, "db:schema"] }
        ]}
        assert woqlObject.json() == jsonObj

    def test_chained_property_method(self):
        woqlObject = WOQLQuery().doctype("Journey")
        woqlObject = woqlObject.property(
        "start_station", "Station").label("Start Station")

        woqlObject2 = WOQLQuery().doctype("Journey")
        woqlObject2.property(
        "start_station", "Station").label("Start Station")

        assert woqlObject.json() == woqlObject2.json()
