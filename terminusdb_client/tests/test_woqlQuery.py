import pprint

from terminusdb_client.woqlquery.woql_query import WOQLQuery

from .ans_cardinality import *  # noqa
from .ans_doctype import *  # noqa
from .ans_insert import *  # noqa
from .ans_property import *  # noqa
from .ans_triple_quad import *  # noqa

# expected results
from .woqljson.woqlAndJson import WOQL_AND_JSON
from .woqljson.woqlCastJson import WOQL_CAST_JSON
from .woqljson.woqlConcatJson import WOQL_CONCAT_JSON
from .woqljson.woqlDeleteJson import WOQL_DELETE_JSON
from .woqljson.woqlIdgenJson import WOQL_IDGEN_JSON
from .woqljson.woqlJoinSplitJson import WOQL_JOIN_SPLIT_JSON
from .woqljson.woqlJson import WOQL_JSON, WOQL_STAR
from .woqljson.woqlMathJson import WOQL_MATH_JSON
from .woqljson.woqlOrJson import WOQL_OR_JSON
from .woqljson.woqlTrimJson import WOQL_TRIM_JSON
from .woqljson.woqlWhenJson import WOQL_WHEN_JSON

# import pprint


pp = pprint.PrettyPrinter(indent=4)


class TestWoqlQueries:
    def test_start_properties_values(self):
        woql_object = WOQLQuery()
        assert not woql_object._chain_ended
        assert not woql_object._contains_update
        assert woql_object._vocab["type"] == "rdf:type"

    def test_limit_method(self):
        woql_object = WOQLQuery().limit(10)
        limit_json = {}
        assert woql_object.to_dict() == limit_json

    def test_start_method(self):
        woql_object = WOQLQuery().limit(10).start(0).star()
        json_obj = {
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
        assert woql_object.to_dict() == json_obj

    def test_insert_method(self, insert_without, insert_with_des):
        woql_object = WOQLQuery().insert("v:Bike_URL", "Bicycle")
        woql_object_des = WOQLQuery().insert(
            "v:Bike_URL", "Bicycle", label="v:Bike_Label", description="v:Bike_Des"
        )
        assert woql_object.to_dict() == insert_without
        assert woql_object_des.to_dict() == insert_with_des

    def test_doctype_method(
        self, doctype_without, doctype_with_label, doctype_with_des
    ):
        woql_object = WOQLQuery().doctype("Station")
        woql_object_label = WOQLQuery().doctype("Station", label="Station Object")
        woql_object_des = WOQLQuery().doctype(
            "Station", label="Station Object", description="A bike station object."
        )
        assert woql_object.to_dict() == doctype_without
        assert woql_object_label.to_dict() == doctype_with_label
        assert woql_object_des.to_dict() == doctype_with_des

    def test_doctype_property_method(self, property_without, property_with_des):
        woql_object = WOQLQuery().doctype("Journey").property("Duration", "dateTime")
        woql_object_des = (
            WOQLQuery()
            .doctype("Journey")
            .property(
                "Duration",
                "dateTime",
                label="Journey Duration",
                description="Journey duration in minutes.",
            )
        )
        assert woql_object.to_dict() == property_without
        assert woql_object_des.to_dict() == property_with_des

    def test_woql_not_method(self):
        woql_object = WOQLQuery().woql_not(WOQLQuery().triple("a", "b", "c"))
        woql_object_chain = WOQLQuery().woql_not()
        woql_object_chain.triple("a", "b", "c")
        json_obj = {
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
        assert woql_object.to_dict() == json_obj
        assert woql_object_chain.to_dict() == json_obj

    def test_woql_and_method(self):
        woql_object = WOQLQuery().woql_and(
            WOQLQuery().triple("a", "b", "c"), WOQLQuery().triple("1", "2", "3")
        )
        woql_object2 = WOQLQuery().triple("a", "b", "c") + WOQLQuery().triple(
            "1", "2", "3"
        )

        assert woql_object.to_dict() == WOQL_AND_JSON
        assert woql_object2.to_dict() == WOQL_AND_JSON

    def test_woql_or_method(self):
        woql_object = WOQLQuery().woql_or(
            WOQLQuery().triple("a", "b", "c"), WOQLQuery().triple("1", "2", "3")
        )
        assert woql_object.to_dict() == WOQL_OR_JSON

    def test_when_method(self):

        woql_object = WOQLQuery().when(True, WOQLQuery().add_class("id"))
        woql_object_chain = WOQLQuery().when(True).add_class("id")
        assert woql_object.to_dict() == WOQL_WHEN_JSON
        assert woql_object_chain.to_dict() == WOQL_WHEN_JSON

    def test_opt_method(self):
        woql_object = WOQLQuery().opt(WOQLQuery().star())
        woql_object_chain = WOQLQuery().opt().star()
        json_obj = {"@type": "woql:Optional", "woql:query": WOQL_STAR}
        assert woql_object.to_dict() == json_obj
        assert woql_object_chain.to_dict() == json_obj

    def test_woql_from_method(self):
        woql_object = WOQLQuery().woql_from("schema/main", WOQLQuery().star())
        woql_object_chain = WOQLQuery().woql_from("schema/main").star()
        json_obj = {
            "@type": "woql:From",
            "woql:graph_filter": {"@type": "xsd:string", "@value": "schema/main"},
            "woql:query": WOQL_STAR,
        }
        assert woql_object.to_dict() == woql_object_chain.to_dict()
        assert woql_object_chain.to_dict() == json_obj

    def test_star_method(self):
        woql_object = WOQLQuery().star()
        assert woql_object.to_dict() == WOQL_STAR

    def test_select_method(self):
        # TODO: chain won't work
        woql_object = WOQLQuery().select("V1", WOQLQuery().star())
        woql_object_multiple = WOQLQuery().select("V1", "V2", WOQLQuery().star())
        woql_object_chain = WOQLQuery().select("V1").star()
        woql_object_chain_multiple = WOQLQuery().select("V1", "V2").star()

        assert woql_object_chain_multiple.to_dict() == woql_object_multiple.to_dict()
        assert woql_object.to_dict() == woql_object_chain.to_dict()

    def test_eq_method(self):
        woql_object = WOQLQuery().eq("a", "b")
        json_obj = {
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
        assert woql_object.to_dict() == json_obj

    def test_trim_method(self):
        woql_object = WOQLQuery().trim("a", "b")
        assert woql_object.to_dict() == WOQL_TRIM_JSON

    def test_eval_method(self):
        woql_object = WOQLQuery().eval("1+2", "b")
        assert woql_object.to_dict() == WOQL_MATH_JSON["evalJson"]

    def test_minus_method(self):

        woql_object = WOQLQuery().minus("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["minusJson"]

    def test_plus_method(self):
        woql_object = WOQLQuery().plus("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["plusJson"]

    def test_times_method(self):
        woql_object = WOQLQuery().times("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["timesJson"]

    def test_divide_method(self):
        woql_object = WOQLQuery().divide("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["divideJson"]

    def test_exp_method(self):
        woql_object = WOQLQuery().exp("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["expJson"]

    def test_div_method(self):
        woql_object = WOQLQuery().div("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["divJson"]

    def test_floor_method(self):
        woql_object = WOQLQuery().floor("2.5")
        assert woql_object.to_dict() == WOQL_MATH_JSON["floorJson"]

    def test_get_method(self):
        woql_object = WOQLQuery().get(WOQLQuery().woql_as("a", "b"), "Target")
        json_obj = {
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
        assert woql_object.to_dict() == json_obj

    def test_remote_method(self):
        woql_object = WOQLQuery().remote({"url": "http://url"})
        json_obj = {
            "@type": "woql:RemoteResource",
            "woql:remote_uri": {"@type": "xsd:anyURI", "@value": {"url": "http://url"}},
        }
        assert woql_object.to_dict() == json_obj

    def test_post_method(self):
        woql_object = WOQLQuery().post("my_json_file", {"format": "panda_json"})
        json_obj = {
            "@type": "woql:PostResource",
            "woql:file": {"@type": "xsd:string", "@value": "my_json_file"},
            "woql:format": {
                "@type": "woql:Format",
                "woql:format_type": {"@value": "panda_json", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_obj

    def test_idgen_method(self):
        woql_object = WOQLQuery().idgen(
            "doc:Station", "v:Start_ID", "v:Start_Station_URL"
        )
        assert woql_object.to_dict() == WOQL_IDGEN_JSON

    def test_typecast_method(self):
        woql_object = WOQLQuery().typecast(
            "v:Duration", "xsd:integer", "v:Duration_Cast"
        )
        json_obj = {
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
        assert woql_object.to_dict() == json_obj

    def test_cast_method(self):
        woql_object = WOQLQuery().cast("v:Duration", "xsd:integer", "v:Duration_Cast")
        assert woql_object.to_dict() == WOQL_CAST_JSON

    def test_re_method(self):
        woql_object = WOQLQuery().re("!\\w+(.*)test$", "v:string", "v:formated")
        json_obj = {
            "@type": "woql:Regexp",
            "woql:pattern": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "!\\w+(.*)test$"},
            },
            "woql:regexp_list": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@type": "xsd:string", "@value": "formated"},
            },
            "woql:regexp_string": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@type": "xsd:string", "@value": "string"},
            },
        }
        assert woql_object.to_dict() == json_obj

    def test_join_method(self):
        woql_object = WOQLQuery().join(["v:A_obj", "v:B_obj"], ", ", "v:output")
        assert woql_object.to_dict() == WOQL_JOIN_SPLIT_JSON["joinJson"]

    def test_split_method(self):
        woql_object = WOQLQuery().split("A, B, C", ", ", "v:list_obj")
        assert woql_object.to_dict() == WOQL_JOIN_SPLIT_JSON["splitJson"]

    def test_member_method(self):
        woql_object = WOQLQuery().member("v:member", "v:list_obj")
        json_obj = {
            "@type": "woql:Member",
            "woql:member": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "member", "@type": "xsd:string"},
            },
            "woql:member_list": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "list_obj", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_obj

    def test_concat_method(self):
        woql_object = WOQLQuery().concat("v:Duration yo v:Duration_Cast", "v:x")
        assert woql_object.to_dict() == WOQL_CONCAT_JSON

    def test_group_by_method(self):
        woql_object = (
            WOQLQuery()
            .group_by(["v:A", "v:B"], ["v:C"], "v:New")
            .triple("v:A", "v:B", "v:C")
        )
        assert woql_object.to_dict() == WOQL_JSON["groupbyJson"]

    def test_order_by_method_asc(self):
        woql_object = (
            WOQLQuery()
            .order_by("v:A", "v:B", "v:C", order=["asc", "desc", "asc"])
            .star()
        )
        assert woql_object.to_dict() == WOQL_JSON["orderbyJson"]

    def test_simple_path_query(self):
        woql_object = WOQLQuery().path("v:X", "scm:hop", "v:Y", "v:Path")
        json_object = {
            "@type": "woql:Path",
            "woql:subject": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "X", "@type": "xsd:string"},
            },
            "woql:path_pattern": {
                "@type": "woql:PathPredicate",
                "woql:path_predicate": {"@id": "scm:hop"},
            },
            "woql:object": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Y", "@type": "xsd:string"},
            },
            "woql:path": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Path", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_object

    def test_plus_directed_path_query(self):
        woql_object = WOQLQuery().path("v:X", "<scm:hop+", "v:Y", "v:Path")
        json_object = {
            "@type": "woql:Path",
            "woql:subject": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "X", "@type": "xsd:string"},
            },
            "woql:path_pattern": {
                "@type": "woql:PathPlus",
                "woql:path_pattern": {
                    "@type": "woql:InvertedPathPredicate",
                    "woql:path_predicate": {"@id": "scm:hop"},
                },
            },
            "woql:object": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Y", "@type": "xsd:string"},
            },
            "woql:path": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Path", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_object

    def test_grouped_path_query(self):
        woql_object = WOQLQuery().path("v:X", "(<scm:hop,scm:hop>)+", "v:Y", "v:Path")
        json_object = {
            "@type": "woql:Path",
            "woql:subject": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "X", "@type": "xsd:string"},
            },
            "woql:path_pattern": {
                "@type": "woql:PathPlus",
                "woql:path_pattern": {
                    "@type": "woql:PathSequence",
                    "woql:path_first": {
                        "@type": "woql:InvertedPathPredicate",
                        "woql:path_predicate": {"@id": "scm:hop"},
                    },
                    "woql:path_second": {
                        "@type": "woql:PathPredicate",
                        "woql:path_predicate": {"@id": "scm:hop"},
                    },
                },
            },
            "woql:object": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Y", "@type": "xsd:string"},
            },
            "woql:path": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Path", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_object

    def test_double_grouped_path_query(self):
        woql_object = WOQLQuery().path(
            "v:X", "((<scm:hop,scm:hop>)|(<scm:hop2,scm:hop2>))+", "v:Y", "v:Path"
        )
        json_object = {
            "@type": "woql:Path",
            "woql:subject": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "X", "@type": "xsd:string"},
            },
            "woql:path_pattern": {
                "@type": "woql:PathPlus",
                "woql:path_pattern": {
                    "@type": "woql:PathOr",
                    "woql:path_left": {
                        "@type": "woql:PathSequence",
                        "woql:path_first": {
                            "@type": "woql:InvertedPathPredicate",
                            "woql:path_predicate": {"@id": "scm:hop"},
                        },
                        "woql:path_second": {
                            "@type": "woql:PathPredicate",
                            "woql:path_predicate": {"@id": "scm:hop"},
                        },
                    },
                    "woql:path_right": {
                        "@type": "woql:PathSequence",
                        "woql:path_first": {
                            "@type": "woql:InvertedPathPredicate",
                            "woql:path_predicate": {"@id": "scm:hop2"},
                        },
                        "woql:path_second": {
                            "@type": "woql:PathPredicate",
                            "woql:path_predicate": {"@id": "scm:hop2"},
                        },
                    },
                },
            },
            "woql:object": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Y", "@type": "xsd:string"},
            },
            "woql:path": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "Path", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_object


class TestTripleBuilder:
    def test_triple_method(self, triple_opt):
        woql_object = WOQLQuery().triple("a", "b", "c")
        woql_object_opt = WOQLQuery().triple("a", "b", "c", opt=True)
        assert woql_object.to_dict() == WOQL_JSON["tripleJson"]
        assert woql_object_opt.to_dict() == triple_opt

    def test_quad_method(self, quad_opt):
        woql_object = WOQLQuery().quad("a", "b", "c", "d")
        woql_object_opt = WOQLQuery().quad("a", "b", "c", "d", opt=True)
        assert woql_object.to_dict() == WOQL_JSON["quadJson"]
        assert woql_object_opt.to_dict() == quad_opt

    def test_add_class_method(self):
        woql_object = WOQLQuery().add_class("id")
        assert woql_object.to_dict() == WOQL_JSON["addClassJson"]

    def test_delete_class_method(self):
        woql_object = WOQLQuery().delete_class("id")
        assert woql_object.to_dict() == WOQL_DELETE_JSON

    def test_sub_method(self):
        woql_object = WOQLQuery().sub("ClassA", "ClassB")
        assert woql_object.to_dict() == WOQL_JSON["subsumptionJson"]

    def test_isa_method(self):
        woql_object = WOQLQuery().isa("instance", "Class")
        assert woql_object.to_dict() == WOQL_JSON["isAJson"]

    def test_delete_method(self):
        woql_object = WOQLQuery().delete_object("doc:x")
        json_obj = {"@type": "woql:DeleteObject", "woql:document_uri": "doc:x"}
        assert woql_object.to_dict() == json_obj

    def test_delete_triple_method(self):
        woql_object = WOQLQuery().delete_triple("a", "b", "c")
        assert woql_object.to_dict() == WOQL_JSON["deleteTripleJson"]

    def test_delete_quad_method(self):
        woql_object = WOQLQuery().delete_quad("a", "b", "c", "d")
        assert woql_object.to_dict() == WOQL_JSON["deleteQuadJson"]

    def test_add_triple_method(self):
        woql_object = WOQLQuery().add_triple("a", "b", "c")
        assert woql_object.to_dict() == WOQL_JSON["addTripleJson"]

    def test_add_quad_method(self):
        woql_object = WOQLQuery().add_quad("a", "b", "c", "d")
        assert woql_object.to_dict() == WOQL_JSON["addQuadJson"]

    def test_add_property_method(self):
        woql_object = WOQLQuery().add_property("some_property", "string")
        assert woql_object.to_dict() == WOQL_JSON["addPropertyJson"]

    def test_delete_property_method(self):
        woql_object = WOQLQuery().delete_property("some_property", "string")
        assert woql_object.to_dict() == WOQL_JSON["deletePropertyJson"]


class TestTripleBuilderChainer:
    def test_node_method(self):
        woql_object = WOQLQuery().node("some_node", "add_quad")
        assert woql_object.to_dict() == {}

    def test_graph_method(self):
        woql_object = WOQLQuery().node("a", "AddQuad").graph("schema/main")
        woql_object2 = (
            WOQLQuery()
            .node("doc:x", "add_quad")
            .graph("schema/main")
            .label("my label", "en")
        )

        assert woql_object.to_dict() == {}
        assert woql_object2.to_dict() == WOQL_JSON["graphMethodJson"]

    def test_node_and_label_method(self):
        woql_object = WOQLQuery().node("doc:x", "add_quad").label("my label", "en")
        woql_object2 = WOQLQuery().node("doc:x", "add_quad").label("v:label")
        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == WOQL_JSON["labelMethodJson"]
        assert woql_object2.to_dict() == WOQL_JSON["labelMethodJson2"]

    def test_add_class_and_description_method(self):
        woql_object = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        assert woql_object.to_dict() == WOQL_JSON["addClassDescJson"]

    def test_comment_method(self):
        woql_object = WOQLQuery().comment("my comment")
        json_obj = {
            "@type": "woql:Comment",
            "woql:comment": {"@type": "xsd:string", "@value": "my comment"},
        }
        assert woql_object.to_dict() == json_obj

    def test_abstract_method(self):
        woql_object = WOQLQuery().node("doc:x", "add_quad").abstract()
        assert woql_object.to_dict() == WOQL_JSON["nodeAbstractJson"]

    def test_node_property_method(self):
        woql_object = (
            WOQLQuery().node("doc:x", "add_triple").property("myprop", "value")
        )
        assert woql_object.to_dict() == WOQL_JSON["addNodePropJson"]

    def test_node_parent_method(self):
        woql_object = WOQLQuery().node("doc:x", "add_quad").parent("classParentName")
        assert woql_object.to_dict() == WOQL_JSON["nodeParentJson"]

    def test_class_description_method(self):
        woql_object = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        assert woql_object.to_dict() == WOQL_JSON["addClassDescJson"]

    def test_max(self, property_max):
        woql_object = WOQLQuery().add_property("P", "string").domain("A").max(4)
        assert woql_object.to_dict() == property_max

    def test_min(self, property_min):
        woql_object = WOQLQuery().add_property("P", "string").domain("A").min(2)
        assert woql_object.to_dict() == property_min

    def test_card(self, property_cardinalty):
        woql_object = WOQLQuery().add_property("P", "string").domain("A").cardinality(3)
        assert woql_object.to_dict() == property_cardinalty

    def test_chain1(self, chain_insert):
        woql_object = (
            WOQLQuery()
            .insert("v:Node_ID", "v:Type")
            .label("v:Label")
            .description("v:Description")
            .property("prop", "v:Prop")
            .property("prop", "v:Prop2")
            .parent("myParentClass")
        )
        assert woql_object.to_dict() == chain_insert

    def test_chain2(self, chain_doctype):
        woql_object = (
            WOQLQuery()
            .doctype("MyDoc")
            .label("abc")
            .description("abcd")
            .property("prop", "dateTime")
            .label("aaa")
            .property("prop2", "integer")
            .label("abe")
        )
        assert woql_object.to_dict() == chain_doctype

    def test_dot_chain(self):
        woql_object = WOQLQuery().triple("A", "B", "C").triple("D", "E", "F")
        v2 = WOQLQuery().woql_and(
            WOQLQuery().triple("A", "B", "C"), WOQLQuery().triple("D", "E", "F")
        )
        v3 = WOQLQuery().triple("A", "B", "C").woql_and().triple("D", "E", "F")
        assert woql_object.to_dict() == v2.to_dict()
        assert woql_object.to_dict() == v3.to_dict()

    def test_vars(self):
        single_vars = WOQLQuery().vars("a")
        vars1, vars2, vars3 = WOQLQuery().vars("a", "b", "c")
        assert single_vars == "v:a"
        assert (vars1, vars2, vars3) == ("v:a", "v:b", "v:c")

    def test_woql_as_method(self):
        [x, y, z] = WOQLQuery().vars("x", "y", "z")
        query = WOQLQuery().woql_as(x).woql_as(y).woql_as(z)
        assert query.to_dict() == [
            {
                "@type": "woql:IndexedAsVar",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:variable_name": {"@type": "xsd:string", "@value": "x"},
            },
            {
                "@type": "woql:IndexedAsVar",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:variable_name": {"@type": "xsd:string", "@value": "y"},
            },
            {
                "@type": "woql:IndexedAsVar",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:variable_name": {"@type": "xsd:string", "@value": "z"},
            },
        ]
