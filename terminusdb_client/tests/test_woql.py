from terminusdb_client.woqlquery.woql_query import WOQLQuery
# expected results
from .woqljson.woqlAndJson import WoqlAndJson
from .woqljson.woqlCastJson import WoqlCastJson
from .woqljson.woqlConcatJson import WoqlConcatJson
from .woqljson.woqlDeleteJson import WoqlDeleteJson
from .woqljson.woqlDoctypeJson import WoqlDoctype
from .woqljson.woqlExtraJson import WoqlExtra
from .woqljson.woqlIdgenJson import WoqlIdgen
from .woqljson.woqlInsertJson import WoqlInsert
from .woqljson.woqlJoinSplitJson import WoqlJoin
from .woqljson.woqlJson import WoqlJson
from .woqljson.woqlLimitStar import WoqlLimitStart
from .woqljson.woqlMathJson import WoqlMath
from .woqljson.woqlOptJson import WoqlOpt
from .woqljson.woqlOrJson import WoqlOr
from .woqljson.woqlReJson import WoqlRe
from .woqljson.woqlSelectJson import WoqlSelect
from .woqljson.woqlStarJson import WoqlStar
from .woqljson.woqlTrimJson import WoqlTrim
from .woqljson.woqlWhenJson import WoqlWhen

import pprint
pp = pprint.PrettyPrinter(indent=4)

class TestWoqlQueries:
    def test_start_properties_values(self):
        woqlObject = WOQLQuery()
        assert woqlObject._chain_ended == False
        assert woqlObject._contains_update == False
        assert woqlObject._vocab["type"] == "rdf:type"

    def test_limit_method(self):
        woqlObject = WOQLQuery().limit(10)
        limitJson={}
        assert woqlObject.json() == limitJson

    def test_start_method(self):
        #TODO
        woqlObject = WOQLQuery().limit(10).start(0)
        jsonObj = {"@type": "woql:Limit",
                  "woql:limit": {
                      "@type": "woql:Datatype",
                      "woql:datatype": {
                          "@type": "xsd:nonNegativeInteger",
                          "@value": 10
                      }
                  },
                  "woql:query": {
                      "@type": "woql:Start",
                      "woql:start": {
                          "@type": "woql:Datatype",
                          "woql:datatype": {
                              "@type": "xsd:nonNegativeInteger",
                              "@value": 0
                          }
                      },
                      "woql:query": {}
                  }
              }
        #pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_insert_method(self):
        #TODO: please check logic
        woqlObject = WOQLQuery().insert("v:Bike_URL", "Bicycle")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlInsert["onlyNode"])
        assert woqlObject.json() == WoqlInsert["onlyNode"]

    def test_doctype_method(self):
        #TODO: test in js does not exist
        woqlObject = WOQLQuery().doctype("Station")
        jsonObj = {
            "and": [
                {"add_quad": ["scm:Station", "rdf:type", "owl:Class", "db:schema"]},
                {
                    "add_quad": [
                        "scm:Station",
                        "rdfs:subClassOf",
                        "tcs:Document",
                        "db:schema",
                    ]
                },
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_woql_not_method(self):
        #TODO: chining does not work
        woqlObject = WOQLQuery().woql_not(WOQLQuery().triple("a", "b", "c"))
        woqlObjectChain = WOQLQuery().woql_not().triple("a", "b", "c")
        jsonObj = {"@type": "woql:Not",
                  "woql:query": {
                      "@type": "woql:Triple",
                      "woql:subject": {
                          "@type": "woql:Node",
                          "woql:node": "doc:a"
                      },
                      "woql:predicate": {
                          "@type": "woql:Node",
                          "woql:node": "scm:b"
                      },
                      "woql:object": {
                          "@type": "woql:Datatype",
                          "woql:datatype": {
                              "@type": "xsd:string",
                              "@value": "c"
                          }
                      }
                  }
              }

        pp.pprint(woqlObjectChain.json())

        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_woql_and_method(self):
        woqlObject = WOQLQuery().woql_and(
            WOQLQuery().triple("a", "b", "c"), WOQLQuery().triple("1", "2", "3")
        )

        assert woqlObject.json() == WoqlAndJson

    def test_woql_or_method(self):
        woqlObject = WOQLQuery().woql_or(
            WOQLQuery().triple("a", "b", "c"), WOQLQuery().triple("1", "2", "3")
        )
        jsonObj = {
            "or": [
                {"triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]},
                {"triple": ["doc:1", "scm:2", {"@language": "en", "@value": "3"}]},
            ]
        }

        assert woqlObject.json() == WoqlOr

    def test_when_method(self):
        #TODO: how to use add_class now?
        woqlObject = WOQLQuery().when(True, WOQLQuery().add_class("id"))
        woqlObjectChain = WOQLQuery().when(True).add_class("id")
        jsonObj = {
            "when": [
                {"true": []},
                {"add_quad": ["scm:id", "rdf:type", "owl:Class", "db:schema"]},
            ]
        }

        pp.pprint(woqlObjectChain.json())
        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_opt_method(self):
        #TODO: chaining does not work
        woqlObject = WOQLQuery().opt(WOQLQuery().triple("a", "b", "c"))
        woqlObjectChain = WOQLQuery().opt().triple("a", "b", "c")

        jsonObj = {
            "opt": [{"triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]}]
        }

        assert woqlObject.json() == WoqlOpt
        assert woqlObjectChain.json() == WoqlOpt

    def test_woql_from_method(self):
        woql_original = WOQLQuery().limit(10)
        woqlObject = WOQLQuery().woql_from("http://dburl", woql_original)
        woqlObjectChain = WOQLQuery().woql_from("http://dburl").limit(10)

        jsonObj = {"from": ["http://dburl", {"limit": [10, {}]}]}

        # assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_star_method(self):
        woqlObject = WOQLQuery().limit(10).star()
        assert woqlObject.json() == WoqlStar

    def test_select_method(self):
        #TODO: chain won't work
        woqlObject = WOQLQuery().select("V1", WOQLQuery().triple("a", "b", "c"))
        woqlObjectMultiple = WOQLQuery().select(
            "V1", "V2", WOQLQuery().triple("a", "b", "c")
        )
        woqlObjectChain = WOQLQuery().select("V1").triple("a", "b", "c")
        woqlObjectChainMultiple = WOQLQuery().select("V1", "V2").triple("a", "b", "c")

        assert woqlObject.json() == WoqlSelect["jsonObj"]
        #assert woqlObjectChain.json() == WoqlSelect["jsonObj"]
        assert woqlObjectMultiple.json() == WoqlSelect["jsonObjMulti"]
        #assert woqlObjectChainMultiple.json() == WoqlSelect["jsonObjMulti"]

    def test_eq_method(self):
        woqlObject = WOQLQuery().eq("a", "b")
        jsonObj = {"@type": "woql:Equals",
                      "woql:left": {
                          "@type": "woql:Datatype",
                          "woql:datatype": {
                              "@type": "xsd:string",
                              "@value": "a"
                          }
                      },
                      "woql:right": {
                          "@type": "woql:Datatype",
                          "woql:datatype": {
                              "@type": "xsd:string",
                              "@value": "b"
                          }
                      }
                  }
        pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_trim_method(self):
        woqlObject = WOQLQuery().trim("a", "b")
        assert woqlObject.json() == WoqlTrim

    def test_eval_method(self):
        woqlObject = WOQLQuery().eval("1+2", "b")
        assert woqlObject.json() == WoqlMath["evalJson"]

    def test_minus_method(self):
        woqlObject = WOQLQuery().minus("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["minusJson"])
        assert woqlObject.json() == WoqlMath["minusJson"]

    def test_plus_method(self):
        woqlObject = WOQLQuery().plus("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["plusJson"])
        assert woqlObject.json() == WoqlMath["plusJson"]

    def test_times_method(self):
        woqlObject = WOQLQuery().times("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["timesJson"])
        assert woqlObject.json() == WoqlMath["timesJson"]

    def test_divide_method(self):
        woqlObject = WOQLQuery().divide("2", "1")
        jsonObj = {"divide": ["2", "1"]}
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["divideJson"])
        assert woqlObject.json() == WoqlMath["divideJson"]

    def test_exp_method(self):
        woqlObject = WOQLQuery().exp("2", "1")
        jsonObj = {"exp": ["2", "1"]}
        assert woqlObject.json() == WoqlMath["expJson"]

    def test_div_method(self):
        #TODO: no expected output
        woqlObject = WOQLQuery().div("2", "1")
        jsonObj = {"div": ["2", "1"]}
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["divJson"]) #??
        assert woqlObject.json() == WoqlMath["divJson"] #??

    def test_get_method(self):
        #TODO: orig assume to be dict
        woqlObject = WOQLQuery().get("Map", "Target")
        jsonObj = {"get": [[], {}]}
        pp.pprint(woqlObject._query)
        assert woqlObject.json() == jsonObj

    def test_woql_as_method(self):
        #TODO: no js test
        woqlObject = WOQLQuery().woql_as("Source", "Target")
        woqlObject2 = (
            WOQLQuery().woql_as("Source", "Target").woql_as("Source2", "Target2")
        )
        jsonObj = [{"as": [{"@value": "Source"}, "v:Target"]}]
        jsonObj2 = [
            {"as": [{"@value": "Source"}, "v:Target"]},
            {"as": [{"@value": "Source2"}, "v:Target2"]},
        ]

        assert woqlObject.json() == jsonObj
        assert woqlObject2.json() == jsonObj2

    def test_remote_method(self):
        woqlObject = WOQLQuery().remote({"url": "http://url"})
        jsonObj = {"@type": "woql:RemoteResource",
                  "woql:remote_uri": {
                      "@type": "xsd:anyURI",
                      "@value": {
                          "url": "http://url"
                      }
                  }
              }
        assert woqlObject.json() == jsonObj

    def test_post_method(self):
        #TODO
        woqlObject = WOQLQuery().post("my_json_file", {"type": "panda_json"})
        jsonObj = {"post": ["my_json_file", {"type": "panda_json"}]}
        assert woqlObject.json() == jsonObj

    def test_idgen_method(self):
        #TODO: clean stuff not right
        woqlObject = WOQLQuery().idgen(
            "doc:Station", ["v:Start_ID"], "v:Start_Station_URL"
        )
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlIdgen)
        assert woqlObject.json() == WoqlIdgen

    def test_typecast_method(self):
        #TODO: casting var name not right
        woqlObject = WOQLQuery().typecast(
            "v:Duration", "xsd:integer", "v:Duration_Cast"
        )
        jsonObj = {'@type': 'woql:Typecast',
                  'woql:typecast_value': {
                    '@type': 'woql:Variable',
                    'woql:variable_name': { '@value': 'Duration', '@type': 'xsd:string' }
                  },
                  'woql:typecast_type': { '@type': 'woql:Node', 'woql:node': 'xsd:integer' },
                  'woql:typecast_result': {
                    '@type': 'woql:Variable',
                    'woql:variable_name': { '@value': 'Duration_Cast', '@type': 'xsd:string' }
                  }
                }
        pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_cast_method(self):
        #TODO: casting var name not right
        woqlObject = WOQLQuery().cast("v:Duration", "xsd:integer", "v:Duration_Cast")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlCastJson)
        assert woqlObject.json() == WoqlCastJson

    def test_re_method(self):
        #TODO: wlist returns nothing
        woqlObject = WOQLQuery().re(".*", "v:string", "v:formated")
        jsonObj = {
            "re": [
                {"@value": ".*", "@type": "xsd:string"},
                "v:string",
                {"list": ["v:formated"]},
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_join_method(self):
        #TODO: join_list quite broken
        woqlObject = WOQLQuery().join(["v:A_obj", "v:B_obj"], ", ", "v:output")
        pp.pprint(woqlObject.json())
        print("---------")
        pp.pprint(WoqlJoin["joinJson"])
        assert woqlObject.json() == WoqlJoin["joinJson"]

    def test_split_method(self):
        #TODO: orig is Nontype again, in _copy_json
        woqlObject = WOQLQuery().split("A, B, C", ", ", "v:list_obj")
        jsonObj = {
            "split": [
                {"@value": "A, B, C", "@type": "xsd:string"},
                {"@type": "xsd:string", "@value": ", "},
                "v:list_obj",
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_member_method(self):
        #TODO: orig is Nontype again, in _copy_json
        woqlObject = WOQLQuery().member("v:member", "v:list_obj")
        jsonObj = {"member": ["v:member", "v:list_obj"]}
        assert woqlObject.json() == jsonObj

    def test_concat_method(self):
        #TODO: concat list very broken
        woqlObject = WOQLQuery().concat("v:Duration yo v:Duration_Cast", "x")
        pp.pprint(woqlObject.json())
        print("---------")
        pp.pprint(WoqlConcatJson)
        assert woqlObject.json() == WoqlConcatJson

    def test_list_method(self):
        #TODO: no js test
        woqlObject = WOQLQuery().list(["V1", "V2"])
        jsonObj = {"list": [["V1", "V2"]]}
        assert woqlObject.json() == jsonObj

    def test_group_by_method(self):
        #TODO: chain failed
        woqlObject = WOQLQuery().group_by(["v:A", "v:B"], ["v:C"], "v:New").triple("v:A", "v:B", "v:C")
        pp.pprint(woqlObject.json())
        print("---------")
        pp.pprint(WoqlJson["groupbyJson"])
        assert woqlObject.json() == WoqlJson["groupbyJson"]

    def test_order_by_method(self):
        #TODO: bad test case
        woqlObject = WOQLQuery().order_by([WOQLQuery().asc("v:B")])
        jsonObj = {"order_by": [[{"asc": ["v:B"]}], {}]}
        assert woqlObject.json() == jsonObj

    def test_order_by_method_desc(self):
        desc = [WOQLQuery().desc("v:C"), WOQLQuery().desc("v:A")]
        woqlObject = WOQLQuery().order_by(desc)
        jsonObj = {"order_by": [[{"desc": ["v:C"]}, {"desc": ["v:A"]}], {}]}
        assert woqlObject.json() == jsonObj


class TestTripleBuilder:
    def test_triple_method(self):
        woqlObject = WOQLQuery().triple("a", "b", "c")
        jsonObj = {"triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]}
        assert woqlObject.json() == jsonObj

    def test_quad_method(self):
        woqlObject = WOQLQuery().quad("a", "b", "c", "d")
        jsonObj = {
            "quad": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}, "db:d"]
        }
        assert woqlObject.json() == jsonObj

    def test_add_class_method(self):
        woqlObject = WOQLQuery().add_class("id")
        jsonObj = {"add_quad": ["scm:id", "rdf:type", "owl:Class", "db:schema"]}
        assert woqlObject.json() == jsonObj

    def test_delete_class_method(self):
        woqlObject = WOQLQuery().delete_class("id")
        jsonObj = {
            "and": [
                {"delete_quad": ["scm:id", "v:All", "v:Al2", "db:schema"]},
                {"opt": [{"delete_quad": ["v:Al3", "v:Al4", "scm:id", "db:schema"]}]},
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_sub_method(self):
        woqlObject = WOQLQuery().sub("ClassA", "ClassB")
        jsonObj = {"sub": ["scm:ClassA", "scm:ClassB"]}
        assert woqlObject.json() == jsonObj

    def test_isa_methos(self):
        woqlObject = WOQLQuery().isa("instance", "Class")
        jsonObj = {"isa": ["scm:instance", "owl:Class"]}
        assert woqlObject.json() == jsonObj

    def test_delete_method(self):
        woqlObject = WOQLQuery().delete(
            {"triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]}
        )
        jsonObj = {
            "delete": [
                {"triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]}
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_delete_triple_method(self):
        woqlObject = WOQLQuery().delete_triple("a", "b", "c")
        jsonObj = {
            "delete_triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]
        }
        assert woqlObject.json() == jsonObj

    def test_delete_quad_method(self):
        woqlObject = WOQLQuery().delete_quad("a", "b", "c", "d")
        jsonObj = {
            "delete_quad": [
                "doc:a",
                "scm:b",
                {"@language": "en", "@value": "c"},
                "db:d",
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_add_triple_method(self):
        woqlObject = WOQLQuery().add_triple("a", "b", "c")
        jsonObj = {"add_triple": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}]}
        assert woqlObject.json() == jsonObj

    def test_add_quad_method(self):
        woqlObject = WOQLQuery().add_quad("a", "b", "c", "d")
        jsonObj = {
            "add_quad": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}, "db:d"]
        }
        assert woqlObject.json() == jsonObj

    def test_add_property_methof(self):
        woqlObject = WOQLQuery().add_property("some_property", "string")
        jsonObj = {
            "and": [
                {
                    "add_quad": [
                        "scm:some_property",
                        "rdf:type",
                        "owl:DatatypeProperty",
                        "db:schema",
                    ]
                },
                {
                    "add_quad": [
                        "scm:some_property",
                        "rdfs:range",
                        "xsd:string",
                        "db:schema",
                    ]
                },
            ]
        }
        print(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_delete_property_method(self):
        woqlObject = WOQLQuery().delete_property("some_property", "string")
        jsonObj = {
            "and": [
                {"delete_quad": ["scm:some_property", "v:All", "v:Al2", "xsd:string"]},
                {"delete_quad": ["v:Al3", "v:Al4", "scm:some_property", "xsd:string"]},
            ]
        }
        assert woqlObject.json() == jsonObj


class TestTripleBuilderChainer:
    def test_node_method(self):
        woqlObject = WOQLQuery().node("some_node")
        jsonObj = {}
        assert woqlObject.json() == jsonObj

    def test_graph_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").graph("db:schema")
        woqlObject2 = (
            WOQLQuery()
            .node("doc:x", "add_quad")
            .graph("db:mySchema")
            .label("my label", "en")
        )
        jsonObj = {}
        jsonObj2 = {
            "add_quad": [
                "doc:x",
                "rdfs:label",
                {"@value": "my label", "@language": "en"},
                "db:mySchema",
            ]
        }

        assert woqlObject.json() == jsonObj
        assert woqlObject2.json() == jsonObj2

    def test_label_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").label("my label", "en")
        woqlObject2 = WOQLQuery().node("doc:x", "add_quad").label("v:label")
        jsonObj = {
            "add_quad": [
                "doc:x",
                "rdfs:label",
                {"@value": "my label", "@language": "en"},
                "db:schema",
            ]
        }
        jsonObj2 = {"add_quad": ["doc:x", "rdfs:label", "v:label", "db:schema"]}
        assert woqlObject.json() == jsonObj
        assert woqlObject2.json() == jsonObj2

    def test_again_add_class_method(self):
        woqlObject = (
            WOQLQuery()
            .add_class("NewClass")
            .description("A new class object.")
            .entity()
        )
        jsonObj = {
            "and": [
                {"add_quad": ["scm:NewClass", "rdf:type", "owl:Class", "db:schema"]},
                {
                    "add_quad": [
                        "scm:NewClass",
                        "rdfs:comment",
                        {"@value": "A new class object.", "@language": "en"},
                        "db:schema",
                    ]
                },
                {
                    "add_quad": [
                        "scm:NewClass",
                        "rdfs:subClassOf",
                        "tcs:Entity",
                        "db:schema",
                    ]
                },
            ]
        }
        print(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_comment_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").comment("my comment")
        jsonObj = {"comment": [{"@language": "en", "@value": "my comment"}, {}]}
        assert woqlObject.json() == jsonObj

    def test_property_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").property("myprop", "value")
        jsonObj = {
            "add_quad": [
                "doc:x",
                "scm:myprop",
                {"@value": "value", "@language": "en"},
                "db:schema",
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_entity_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").entity()
        jsonObj = {"add_quad": ["doc:x", "rdfs:subClassOf", "tcs:Entity", "db:schema"]}
        assert woqlObject.json() == jsonObj

    def test_parent_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").parent("Z")
        jsonObj = {"add_quad": ["doc:x", "rdfs:subClassOf", "scm:Z", "db:schema"]}
        assert woqlObject.json() == jsonObj

    def test_abstract_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").abstract()
        jsonObj = {"add_quad": ["doc:x", "tcs:tag", "tcs:abstract", "db:schema"]}
        assert woqlObject.json() == jsonObj

    def test_relationship_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").relationship()
        jsonObj = {"add_quad": ["doc:x", "rdfs:subClassOf", "tcs:Entity", "db:schema"]}
        assert woqlObject.json() == jsonObj

    def test_max_method(self):
        woqlObject = WOQLQuery().add_property("P", "string").max(4)
        jsonObj = {
            "and": [
                {
                    "add_quad": [
                        "scm:P",
                        "rdf:type",
                        "owl:DatatypeProperty",
                        "db:schema",
                    ]
                },
                {"add_quad": ["scm:P", "rdfs:range", "xsd:string", "db:schema"]},
                {"add_quad": ["scm:P_max", "rdf:type", "owl:Restriction", "db:schema"]},
                {"add_quad": ["scm:P_max", "owl:onProperty", "scm:P", "db:schema"]},
                {
                    "add_quad": [
                        "scm:P_max",
                        "owl:maxCardinality",
                        {"@value": 4, "@type": "xsd:nonNegativeInteger"},
                        "db:schema",
                    ]
                },
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_min_method(self):
        woqlObject = WOQLQuery().add_property("P", "string").min(2)
        jsonObj = {
            "and": [
                {
                    "add_quad": [
                        "scm:P",
                        "rdf:type",
                        "owl:DatatypeProperty",
                        "db:schema",
                    ]
                },
                {"add_quad": ["scm:P", "rdfs:range", "xsd:string", "db:schema"]},
                {"add_quad": ["scm:P_min", "rdf:type", "owl:Restriction", "db:schema"]},
                {"add_quad": ["scm:P_min", "owl:onProperty", "scm:P", "db:schema"]},
                {
                    "add_quad": [
                        "scm:P_min",
                        "owl:minCardinality",
                        {"@value": 2, "@type": "xsd:nonNegativeInteger"},
                        "db:schema",
                    ]
                },
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_cardinality_method(self):
        woqlObject = WOQLQuery().add_property("P", "string").cardinality(3)
        jsonObj = {
            "and": [
                {
                    "add_quad": [
                        "scm:P",
                        "rdf:type",
                        "owl:DatatypeProperty",
                        "db:schema",
                    ]
                },
                {"add_quad": ["scm:P", "rdfs:range", "xsd:string", "db:schema"]},
                {
                    "add_quad": [
                        "scm:P_cardinality",
                        "rdf:type",
                        "owl:Restriction",
                        "db:schema",
                    ]
                },
                {
                    "add_quad": [
                        "scm:P_cardinality",
                        "owl:onProperty",
                        "scm:P",
                        "db:schema",
                    ]
                },
                {
                    "add_quad": [
                        "scm:P_cardinality",
                        "owl:cardinality",
                        {"@value": 3, "@type": "xsd:nonNegativeInteger"},
                        "db:schema",
                    ]
                },
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_chained_insert_method(self):
        woqlObject = (
            WOQLQuery()
            .insert("v:Node_ID", "v:Type")
            .label("v:Label")
            .description("v:Description")
            .property("prop", "v:Prop")
            .property("prop", "v:Prop2")
            .entity()
            .parent("hello")
        )
        jsonObj = {
            "and": [
                {"add_triple": ["v:Node_ID", "rdf:type", "v:Type"]},
                {"add_triple": ["v:Node_ID", "rdfs:label", "v:Label"]},
                {"add_triple": ["v:Node_ID", "rdfs:comment", "v:Description"]},
                {"add_triple": ["v:Node_ID", "scm:prop", "v:Prop"]},
                {"add_triple": ["v:Node_ID", "scm:prop", "v:Prop2"]},
                {"add_triple": ["v:Node_ID", "rdfs:subClassOf", "tcs:Entity"]},
                {"add_triple": ["v:Node_ID", "rdfs:subClassOf", "scm:hello"]},
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_chained_doctype_method(self):
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
        jsonObj = {
            "and": [
                {
                    "add_quad": [
                        "scm:prop2",
                        "rdf:type",
                        "owl:DatatypeProperty",
                        "db:schema",
                    ]
                },
                {"add_quad": ["scm:prop2", "rdfs:range", "xsd:integer", "db:schema"]},
                {"add_quad": ["scm:prop2", "rdfs:domain", "scm:MyDoc", "db:schema"]},
                {
                    "and": [
                        {
                            "add_quad": [
                                "scm:prop",
                                "rdf:type",
                                "owl:DatatypeProperty",
                                "db:schema",
                            ]
                        },
                        {
                            "add_quad": [
                                "scm:prop",
                                "rdfs:range",
                                "xsd:dateTime",
                                "db:schema",
                            ]
                        },
                        {
                            "add_quad": [
                                "scm:prop",
                                "rdfs:domain",
                                "scm:MyDoc",
                                "db:schema",
                            ]
                        },
                        {
                            "and": [
                                {
                                    "add_quad": [
                                        "scm:MyDoc",
                                        "rdf:type",
                                        "owl:Class",
                                        "db:schema",
                                    ]
                                },
                                {
                                    "add_quad": [
                                        "scm:MyDoc",
                                        "rdfs:subClassOf",
                                        "tcs:Document",
                                        "db:schema",
                                    ]
                                },
                                {
                                    "add_quad": [
                                        "scm:MyDoc",
                                        "rdfs:label",
                                        {"@value": "abc", "@language": "en"},
                                        "db:schema",
                                    ]
                                },
                                {
                                    "add_quad": [
                                        "scm:MyDoc",
                                        "rdfs:comment",
                                        {"@value": "abcd", "@language": "en"},
                                        "db:schema",
                                    ]
                                },
                            ]
                        },
                        {
                            "add_quad": [
                                "scm:prop",
                                "rdfs:label",
                                {"@value": "aaa", "@language": "en"},
                                "db:schema",
                            ]
                        },
                    ]
                },
                {
                    "add_quad": [
                        "scm:prop2",
                        "rdfs:label",
                        {"@value": "abe", "@language": "en"},
                        "db:schema",
                    ]
                },
            ]
        }
        assert woqlObject.json() == jsonObj

    def test_chained_property_method(self):
        woqlObject = WOQLQuery().doctype("Journey")
        woqlObject = woqlObject.property("start_station", "Station").label(
            "Start Station"
        )

        woqlObject2 = WOQLQuery().doctype("Journey")
        woqlObject2.property("start_station", "Station").label("Start Station")

        assert woqlObject.json() == woqlObject2.json()
