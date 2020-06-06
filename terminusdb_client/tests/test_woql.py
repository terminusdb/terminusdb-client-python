import pprint

from terminusdb_client.woqlquery.woql_query import WOQLQuery

# expected results
from .woqljson.woqlAndJson import WoqlAndJson
from .woqljson.woqlCastJson import WoqlCastJson
from .woqljson.woqlConcatJson import WoqlConcatJson
from .woqljson.woqlIdgenJson import WoqlIdgen
from .woqljson.woqlInsertJson import WoqlInsert
from .woqljson.woqlJoinSplitJson import WoqlJoin
from .woqljson.woqlJson import WOQL_STAR, WoqlJson
from .woqljson.woqlMathJson import WoqlMath
from .woqljson.woqlOrJson import WoqlOr
from .woqljson.woqlTrimJson import WoqlTrim
from .woqljson.woqlWhenJson import WoqlWhen

pp = pprint.PrettyPrinter(indent=4)


class TestWoqlQueries:
    def test_start_properties_values(self):
        woqlObject = WOQLQuery()
        assert woqlObject._chain_ended == False
        assert woqlObject._contains_update == False
        assert woqlObject._vocab["type"] == "rdf:type"

    def test_limit_method(self):
        woqlObject = WOQLQuery().limit(10)
        limitJson = {}
        assert woqlObject.json() == limitJson

    def test_start_method(self):
        woqlObject = WOQLQuery().limit(10).start(0).star()
        jsonObj = {
            "@type": "woql:Limit",
            "woql:limit": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:nonNegativeInteger", "@value": 10},
            },
            "woql:query": {
                "@type": "woql:Start",
                "woql:query": WOQL_STAR,
                "woql:start": {
                    "@type": "woql:Datatype",
                    "woql:datatype": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                },
            },
        }

        pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_insert_method(self):
        woqlObject = WOQLQuery().insert("v:Bike_URL", "Bicycle")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlInsert["onlyNode"])
        assert woqlObject.json() == WoqlInsert["onlyNode"]

    def test_doctype_method(self):
        # TODO: test in js does not exist
        woqlObject = WOQLQuery().doctype("Station")
        pp.pprint(woqlObject.json())
        jsonObj = {
            "@type": "woql:And",
            "woql:query_list": [
                {
                    "@type": "woql:QueryListElement",
                    "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                    "woql:query": {
                        "@type": "woql:AddQuad",
                        "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                        "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
                        "woql:predicate": {
                            "@type": "woql:Node",
                            "woql:node": "rdf:type",
                        },
                        "woql:subject": {
                            "@type": "woql:Node",
                            "woql:node": "scm:Station",
                        },
                    },
                },
                {
                    "@type": "woql:QueryListElement",
                    "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                    "woql:query": {
                        "@type": "woql:AddQuad",
                        "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                        "woql:object": {
                            "@type": "woql:Node",
                            "woql:node": "terminus:Document",
                        },
                        "woql:predicate": {
                            "@type": "woql:Node",
                            "woql:node": "rdfs:subClassOf",
                        },
                        "woql:subject": {
                            "@type": "woql:Node",
                            "woql:node": "scm:Station",
                        },
                    },
                },
            ],
        }

        assert woqlObject.json() == jsonObj

    def test_woql_not_method(self):
        woqlObject = WOQLQuery().woql_not(WOQLQuery().triple("a", "b", "c"))
        woqlObjectChain = WOQLQuery().woql_not()
        woqlObjectChain.triple("a", "b", "c")
        jsonObj = {
            "@type": "woql:Not",
            "woql:query": {
                "@type": "woql:Triple",
                "woql:subject": {"@type": "woql:Node", "woql:node": "doc:a"},
                "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:b"},
                "woql:object": {
                    "@type": "woql:Datatype",
                    "woql:datatype": {"@type": "xsd:string", "@value": "c"},
                },
            },
        }
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
        # TODO: chcek chaining
        woqlObject = WOQLQuery().when(True, WOQLQuery().add_class("id"))
        woqlObjectChain = WOQLQuery().when(True).add_class("id")
        print("___first try___")
        pp.pprint(woqlObject.json())
        print("___second try___")
        pp.pprint(woqlObjectChain._cursor)
        pp.pprint(woqlObjectChain.json())
        print("___right answer___")
        pp.pprint(WoqlWhen)
        assert woqlObject.json() == WoqlWhen
        assert woqlObjectChain.json() == WoqlWhen

    def test_opt_method(self):
        woqlObject = WOQLQuery().opt(WOQLQuery().star())
        woqlObjectChain = WOQLQuery().opt().star()
        jsonObj = {"@type": "woql:Optional", "woql:query": WOQL_STAR}
        assert woqlObject.json() == jsonObj
        assert woqlObjectChain.json() == jsonObj

    def test_woql_from_method(self):
        woqlObject = WOQLQuery().woql_from("schema/main", WOQLQuery().star())
        woqlObjectChain = WOQLQuery().woql_from("schema/main").star()
        jsonObj = {
            "@type": "woql:From",
            "woql:graph_filter": {"@type": "xsd:string", "@value": "schema/main"},
            "woql:query": WOQL_STAR,
        }
        assert woqlObject.json() == woqlObjectChain.json()
        assert woqlObjectChain.json() == jsonObj

    def test_star_method(self):
        woqlObject = WOQLQuery().star()
        assert woqlObject.json() == WOQL_STAR

    def test_select_method(self):
        # TODO: chain won't work
        woqlObject = WOQLQuery().select("V1", WOQLQuery().star())
        woqlObjectMultiple = WOQLQuery().select("V1", "V2", WOQLQuery().star())
        woqlObjectChain = WOQLQuery().select("V1").star()
        woqlObjectChainMultiple = WOQLQuery().select("V1", "V2").star()

        assert woqlObjectChainMultiple.json() == woqlObjectMultiple.json()
        assert woqlObject.json() == woqlObjectChain.json()

    def test_eq_method(self):
        woqlObject = WOQLQuery().eq("a", "b")
        jsonObj = {
            "@type": "woql:Equals",
            "woql:left": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "a"},
            },
            "woql:right": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "b"},
            },
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
        # TODO: interesting args
        woqlObject = WOQLQuery().minus("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["minusJson"])
        assert woqlObject.json() == WoqlMath["minusJson"]

    def test_plus_method(self):
        # TODO: interesting args
        woqlObject = WOQLQuery().plus("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["plusJson"])
        assert woqlObject.json() == WoqlMath["plusJson"]

    def test_times_method(self):
        # TODO: interesting args
        woqlObject = WOQLQuery().times("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["timesJson"])
        assert woqlObject.json() == WoqlMath["timesJson"]

    def test_divide_method(self):
        # TODO: interesting args
        woqlObject = WOQLQuery().divide("2", "1")
        jsonObj = {"divide": ["2", "1"]}
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["divideJson"])
        assert woqlObject.json() == WoqlMath["divideJson"]

    def test_exp_method(self):
        woqlObject = WOQLQuery().exp("2", "1")
        assert woqlObject.json() == WoqlMath["expJson"]

    def test_div_method(self):
        # TODO: no expected output
        woqlObject = WOQLQuery().div("2", "1")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlMath["divJson"])

        assert woqlObject.json() == WoqlMath["divJson"]

    def test_get_method(self):
        woqlObject = WOQLQuery().get(WOQLQuery().woql_as("a", "b"), "Target")
        jsonObj = {
            "@type": "woql:Get",
            "woql:as_vars": [
                {
                    "@type": "woql:NamedAsVar",
                    "woql:identifier": {"@type": "xsd:string", "@value": "a"},
                    "woql:variable_name": {"@type": "xsd:string", "@value": "b"},
                }
            ],
            "woql:query_resource": "Target",
        }
        pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_woql_as_method(self):
        woqlObject = WOQLQuery().woql_as("Source", "Target")
        woqlObject2 = (
            WOQLQuery().woql_as("Source", "Target").woql_as("Source2", "Target2")
        )
        jsonObj2 = [
            {
                "@type": "woql:NamedAsVar",
                "woql:identifier": {"@type": "xsd:string", "@value": "Source"},
                "woql:variable_name": {"@type": "xsd:string", "@value": "Target"},
            },
            {
                "@type": "woql:NamedAsVar",
                "woql:identifier": {"@type": "xsd:string", "@value": "Source2"},
                "woql:variable_name": {"@type": "xsd:string", "@value": "Target2"},
            },
        ]

        assert woqlObject.json() == [jsonObj2[0]]
        assert woqlObject2.json() == jsonObj2

    def test_remote_method(self):
        woqlObject = WOQLQuery().remote({"url": "http://url"})
        jsonObj = {
            "@type": "woql:RemoteResource",
            "woql:remote_uri": {"@type": "xsd:anyURI", "@value": {"url": "http://url"}},
        }
        assert woqlObject.json() == jsonObj

    def test_post_method(self):
        woqlObject = WOQLQuery().post("my_json_file", {"format": "panda_json"})
        jsonObj = {
            "@type": "woql:PostResource",
            "woql:file": {"@type": "xsd:string", "@value": "my_json_file"},
            "woql:format": {
                "@type": "woql:Format",
                "woql:format_type": {"@value": "panda_json", "@type": "xsd:string"},
            },
        }
        assert woqlObject.json() == jsonObj

    def test_idgen_method(self):
        # TODO: 1 or 2 element? (potential off-by-1 thing)
        woqlObject = WOQLQuery().idgen(
            "doc:Station", ["v:Start_ID"], "v:Start_Station_URL"
        )
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlIdgen)
        assert woqlObject.json() == WoqlIdgen

    def test_typecast_method(self):
        woqlObject = WOQLQuery().typecast(
            "v:Duration", "xsd:integer", "v:Duration_Cast"
        )
        jsonObj = {
            "@type": "woql:Typecast",
            "woql:typecast_value": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Duration", "@type": "xsd:string"},
            },
            "woql:typecast_type": {"@type": "woql:Node", "woql:node": "xsd:integer"},
            "woql:typecast_result": {
                "@type": "woql:Variable",
                "woql:variable_name": {
                    "@value": "Duration_Cast",
                    "@type": "xsd:string",
                },
            },
        }
        pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_cast_method(self):
        woqlObject = WOQLQuery().cast("v:Duration", "xsd:integer", "v:Duration_Cast")
        pp.pprint(woqlObject.json())
        pp.pprint(WoqlCastJson)
        assert woqlObject.json() == WoqlCastJson

    def test_re_method(self):
        # TODO: orig is Nontype again, in _copy_json
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
        woqlObject = WOQLQuery().join(["v:A_obj", "v:B_obj"], ", ", "v:output")
        assert woqlObject.json() == WoqlJoin["joinJson"]

    def test_split_method(self):
        # TODO: orig is Nontype again, in _copy_json
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
        woqlObject = WOQLQuery().member("v:member", "v:list_obj")
        jsonObj = {
            "@type": "woql:Member",
            "woql:member": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "member", "@type": "xsd:string",},
            },
            "woql:member_list": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "list_obj", "@type": "xsd:string",},
            },
        }
        assert woqlObject.json() == jsonObj

    def test_concat_method(self):
        woqlObject = WOQLQuery().concat("v:Duration yo v:Duration_Cast", "x")
        assert woqlObject.json() == WoqlConcatJson

    def test_group_by_method(self):
        woqlObject = (
            WOQLQuery()
            .group_by(["v:A", "v:B"], ["v:C"], "v:New")
            .triple("v:A", "v:B", "v:C")
        )
        pp.pprint(woqlObject.json())
        print("---------")
        pp.pprint(WoqlJson["groupbyJson"])
        assert woqlObject.json() == WoqlJson["groupbyJson"]

    def test_order_by_method_asc(self):
        woqlObject = WOQLQuery().order_by("v:A", "v:B asc", "v:C asc").star()
        pp.pprint(woqlObject.json())
        print("____xxxx___")
        pp.pprint(WoqlJson["orderbyJson"])
        assert woqlObject.json() == WoqlJson["orderbyJson"]


class TestTripleBuilder:
    def test_triple_method(self):
        woqlObject = WOQLQuery().triple("a", "b", "c")
        assert woqlObject.json() == WoqlJson["trypleJson"]

    def test_quad_method(self):
        woqlObject = WOQLQuery().quad("a", "b", "c", "d")
        jsonObj = {
            "quad": ["doc:a", "scm:b", {"@language": "en", "@value": "c"}, "db:d"]
        }
        assert woqlObject.json() == WoqlJson["quadJson"]

    def test_add_class_method(self):
        woqlObject = WOQLQuery().add_class("id")
        assert woqlObject.json() == WoqlJson["addClassJson"]

    def test_delete_class_method(self):
        woqlObject = WOQLQuery().delete_class("id")
        assert woqlObject.json() == WoqlDeleteJson

    def test_sub_method(self):
        woqlObject = WOQLQuery().sub("ClassA", "ClassB")
        assert woqlObject.json() == WoqlJson["subsumptionJson"]

    def test_isa_method(self):
        woqlObject = WOQLQuery().isa("instance", "Class")
        jsonObj = {"isa": ["scm:instance", "owl:Class"]}
        assert woqlObject.json() == WoqlJson["isAJson"]

    def test_delete_method(self):
        # TODO: no js tests
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
        assert woqlObject.json() == WoqlJson["deleteTripleJson"]

    def test_delete_quad_method(self):
        woqlObject = WOQLQuery().delete_quad("a", "b", "c", "d")
        assert woqlObject.json() == WoqlJson["deleteQuadJson"]

    def test_add_triple_method(self):
        woqlObject = WOQLQuery().add_triple("a", "b", "c")
        assert woqlObject.json() == WoqlJson["addTripleJson"]

    def test_add_quad_method(self):
        woqlObject = WOQLQuery().add_quad("a", "b", "c", "d")
        assert woqlObject.json() == WoqlJson["addQuadJson"]

    def test_add_property_method(self):
        woqlObject = WOQLQuery().add_property("some_property", "string")
        assert woqlObject.json() == WoqlJson["addPropertyJson"]

    def test_delete_property_method(self):
        woqlObject = WOQLQuery().delete_property("some_property", "string")
        assert woqlObject.json() == WoqlJson["deletePropertyJson"]


class TestTripleBuilderChainer:
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
        woqlObject = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        pp.pprint(woqlObject._cursor)
        print("-------")
        pp.pprint(woqlObject._query)
        print("-------")
        pp.pprint(woqlObject.json())
        print("-----")
        pp.pprint(WoqlJson["addClassDescJson"])
        # assert False
        assert woqlObject.json() == WoqlJson["addClassDescJson"]

    def test_comment_method(self):
        woqlObject = WOQLQuery().comment("my comment")
        woqlObject01 = WOQLQuery().node("doc:x", "add_quad").comment("my comment")
        jsonObj = {
            "@type": "woql:Comment",
            "woql:comment": {"@type": "xsd:string", "@value": "my comment"},
        }
        pp.pprint(woqlObject.json())
        assert woqlObject.json() == jsonObj

    def test_abstract_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").abstract()
        assert woqlObject.json() == WoqlJson["nodeAbstractJson"]

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

    def test_cardinality_method(self):
        woqlObject = WOQLQuery().add_property("P", "string").cardinality(3)
        assert woqlObject.json() == WoqlJson["propCardinalityJson"]

    def test_property_min_method(self):
        woqlObject = WOQLQuery().add_property("P", "string").min(2)
        assert woqlObject.json() == WoqlJson["propMinJson"]

    def test_max_method(self):
        woqlObject = WOQLQuery().add_property("P", "string").max(4)
        assert woqlObject.json() == WoqlJson["propertyMaxJson"]

    def test_node_property_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_triple").property("myprop", "value")
        assert woqlObject.json() == WoqlJson["addNodePropJson"]

    def test_node_parent_method(self):
        woqlObject = WOQLQuery().node("doc:x", "add_quad").parent("classParentName")
        assert woqlObject.json() == WoqlJson["nodeParentJson"]

    def test_class_description_method(self):
        woqlObject = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        assert woqlObject.json() == WoqlJson["addClassDescJson"]
