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
from .woqljson.woqlIdgenJson import (
    WOQL_IDGEN_JSON,
    WOQL_RANDOM_IDGEN_JSON,
    WOQL_UNIQUE_JSON,
)
from .woqljson.woqlJoinSplitJson import WOQL_JOIN_SPLIT_JSON
from .woqljson.woqlJson import WOQL_JSON, WOQL_STAR
from .woqljson.woqlMathJson import WOQL_MATH_JSON
from .woqljson.woqlOrJson import WOQL_OR_JSON
from .woqljson.woqlTrimJson import WOQL_TRIM_JSON
from .woqljson.woqlWhenJson import WOQL_WHEN_JSON

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
            "@type": "Limit",
            "limit": 10,
            "query": {
                "@type": "Start",
                "query": WOQL_STAR,
                "start": 0
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
            "@type": "Not",
            "query": {
                "@type": "Triple",
                "subject": {"@type": "NodeValue", "node": "a"},
                "predicate": {"@type": "NodeValue", "node": "b"},
                "object": {
                    "@type": "Value",
                    "data": {"@type": "xsd:string", "@value": "c"},
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
        woql_object3 = WOQLQuery().triple("a", "b", "c") & WOQLQuery().triple(
            "1", "2", "3"
        )

        assert woql_object.to_dict() == WOQL_AND_JSON
        assert woql_object2.to_dict() == WOQL_AND_JSON
        assert woql_object3.to_dict() == WOQL_AND_JSON

    def test_woql_or_method(self):
        woql_object = WOQLQuery().woql_or(
            WOQLQuery().triple("a", "b", "c"), WOQLQuery().triple("1", "2", "3")
        )
        woql_object2 = WOQLQuery().triple("a", "b", "c") | WOQLQuery().triple(
            "1", "2", "3"
        )
        assert woql_object.to_dict() == WOQL_OR_JSON
        assert woql_object2.to_dict() == WOQL_OR_JSON

    def test_when_method(self):

        woql_object = WOQLQuery().when(True, WOQLQuery().add_class("id"))
        woql_object_chain = WOQLQuery().when(True).add_class("id")
        assert woql_object.to_dict() == WOQL_WHEN_JSON
        assert woql_object_chain.to_dict() == WOQL_WHEN_JSON

    def test_opt_method(self):
        woql_object = WOQLQuery().opt(WOQLQuery().star())
        woql_object_chain = WOQLQuery().opt().star()
        json_obj = {"@type": "Optional", "query": WOQL_STAR}
        assert woql_object.to_dict() == json_obj
        assert woql_object_chain.to_dict() == json_obj

    def test_woql_from_method(self):
        woql_object = WOQLQuery().woql_from("schema", WOQLQuery().star())
        woql_object_chain = WOQLQuery().woql_from("schema").star()
        json_obj = {
            "@type": "From",
            "graph_filter": {"@type": "xsd:string", "@value": "schema"},
            "query": WOQL_STAR,
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
            "@type": "Equals",
            "left": {
                "@type": "Value",
                "node": "a",
            },
            "right": {
                "@type": "Value",
                "node": "b"
            },
        }
        assert woql_object.to_dict() == json_obj

    def test_trim_method(self):
        woql_object = WOQLQuery().trim("a", "b")
        assert woql_object.to_dict() == WOQL_TRIM_JSON

    def test_eval_method(self):
        woql_object = WOQLQuery().eval(WOQLQuery().plus(1,2), "v:x")
        assert woql_object.to_dict() == WOQL_MATH_JSON["evalJson"]

    def test_minus_method(self):

        woql_object = WOQLQuery().minus(1, 1)
        assert woql_object.to_dict() == WOQL_MATH_JSON["minusJson"]

    def test_plus_method(self):
        woql_object = WOQLQuery().plus(2, 1)
        assert woql_object.to_dict() == WOQL_MATH_JSON["plusJson"]

    def test_times_method(self):
        woql_object = WOQLQuery().times(2, 1)
        assert woql_object.to_dict() == WOQL_MATH_JSON["timesJson"]

    def test_divide_method(self):
        woql_object = WOQLQuery().divide(2, 1)
        assert woql_object.to_dict() == WOQL_MATH_JSON["divideJson"]

    def test_exp_method(self):
        woql_object = WOQLQuery().exp(2, 1)
        assert woql_object.to_dict() == WOQL_MATH_JSON["expJson"]

    def test_div_method(self):
        woql_object = WOQLQuery().div(2, 1)
        assert woql_object.to_dict() == WOQL_MATH_JSON["divJson"]

    def test_floor_method(self):
        woql_object = WOQLQuery().floor(2.5)
        assert woql_object.to_dict() == WOQL_MATH_JSON["floorJson"]

    def test_get_method(self):
        woql_object = WOQLQuery().get(WOQLQuery().woql_as("a", "b"), "Target")
        json_obj = {
            "@type": "Get",
            "columns": [
                {
                    "@type": "Column",
                    "indicator": {"@type": "Indicator", "name": "a"},
                    "variable": "b",
                }
            ],
            "resource": "Target",
        }
        assert woql_object.to_dict() == json_obj

    def test_remote_method(self):
        woql_object = WOQLQuery().remote({"url": "http://url"})
        json_obj = {
            "@type": "QueryResource",
            "format" : "csv",
            "source": {"@type": "Source", "url": "http://url"},
        }
        assert woql_object.to_dict() == json_obj

    def test_post_method(self):
        woql_object = WOQLQuery().post("my_json_file", {"format": "panda_json"})
        json_obj = {
            "@type": "QueryResource",
            "file": {"@type": "Source", "file": "my_json_file"},
            "format": "panda_json",
        }
        assert woql_object.to_dict() == json_obj

    def test_unique_method(self):
        woql_object = WOQLQuery().unique(
            "Station", "v:Start_ID", "v:Start_Station_URL"
        )
        assert woql_object.to_dict() == WOQL_UNIQUE_JSON

    def test_idgen_method(self):
        woql_object = WOQLQuery().idgen(
            "Station", "v:Start_ID", "v:Start_Station_URL"
        )
        assert woql_object.to_dict() == WOQL_IDGEN_JSON

    def test_random_idgen_method(self):
        woql_object = WOQLQuery().random_idgen(
            "Station", "v:Start_ID", "v:Start_Station_URL"
        )
        assert woql_object.to_dict() == WOQL_RANDOM_IDGEN_JSON

    def test_typecast_method(self):
        woql_object = WOQLQuery().typecast(
            "v:Duration", "xsd:integer", "v:Duration_Cast"
        )
        json_obj = {
            "@type": "Typecast",
            "typecast_value": {
                "@type": "Variable",
                "variable": {"@value": "Duration", "@type": "xsd:string"},
            },
            "typecast_type": {"@type": "NodeValue", "node": "xsd:integer"},
            "typecast_result": {
                "@type": "Variable",
                "variable": {
                    "@value": "Duration_Cast",
                    "@type": "xsd:string",
                },
            },
        }
        assert woql_object.to_dict() == json_obj

    def test_cast_method(self):
        woql_object = WOQLQuery().cast("v:Duration", "xsd:integer", "v:Duration_Cast")
        assert woql_object.to_dict() == WOQL_CAST_JSON

    def test_cast_method_literal(self):
        woql_object1 = WOQLQuery().cast(
            "1", "xsd:integer", "v:Duration_Cast", literal_type="integer"
        )
        woql_object2 = WOQLQuery().cast(
            WOQLQuery().literal("1", "integer"), "xsd:integer", "v:Duration_Cast"
        )
        assert woql_object1.to_dict() == woql_object2.to_dict()

    def test_cast_method_object(self):
        woql_object1 = WOQLQuery().cast(
            "my_int", "xsd:integer", "v:Duration_Cast", literal_type="owl:Thing"
        )
        woql_object2 = WOQLQuery().cast(
            "my_int", "xsd:integer", "v:Duration_Cast", literal_type="node"
        )
        woql_object3 = WOQLQuery().cast(
            WOQLQuery().iri("my_int"), "xsd:integer", "v:Duration_Cast"
        )
        assert woql_object1.to_dict() == woql_object3.to_dict()
        assert woql_object2.to_dict() == woql_object3.to_dict()

    def test_re_method(self):
        woql_object = WOQLQuery().re("!\\w+(.*)test$", "v:string", "v:formated")
        json_obj = {
            "@type": "Regexp",
            "pattern": {
                "@type": "DataValue",
                "data": {"@type": "xsd:string", "@value": "!\\w+(.*)test$"},
            },
            "regexp_list": {
                "@type": "DataValue",
                "variable": "formated",
            },
            "regexp_string": {
                "@type": "DataValue",
                "variable": "string",
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
            "@type": "Member",
            "member": {
                "@type": "Value",
                "variable": "member",
            },
            "list": {
                "@type": "Value",
                "variable": "list_obj",
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
        woql_object = WOQLQuery().path("v:X", "hop", "v:Y", "v:Path")
        json_object = {
            "@type": "Path",
            "subject": {
                "@type": "Variable",
                "variable": {"@value": "X", "@type": "xsd:string"},
            },
            "path_pattern": {
                "@type": "PathPredicate",
                "path_predicate": "hop",
            },
            "object": {
                "@type": "Variable",
                "variable": {"@value": "Y", "@type": "xsd:string"},
            },
            "path": {
                "@type": "Variable",
                "variable": {"@value": "Path", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_object

    def test_plus_directed_path_query(self):
        woql_object = WOQLQuery().path("v:X", "<hop+", "v:Y", "v:Path")
        json_object = {
            "@type": "Path",
            "subject": {
                "@type": "Variable",
                "variable": {"@value": "X", "@type": "xsd:string"},
            },
            "path_pattern": {
                "@type": "PathPlus",
                "path_pattern": {
                    "@type": "InvertedPathPredicate",
                    "path_predicate": "hop",
                },
            },
            "object": {
                "@type": "Variable",
                "variable": {"@value": "Y", "@type": "xsd:string"},
            },
            "path": {
                "@type": "Variable",
                "variable": {"@value": "Path", "@type": "xsd:string"},
            },
        }
        assert woql_object.to_dict() == json_object

    def test_grouped_path_query(self):
        woql_object = WOQLQuery().path("v:X", "(<hop,hop>)+", "v:Y", "v:Path")
        json_object = {
            "@type": "Path",
            "subject": {
                "@type": "NodeValue",
                "variable": "X",
            },
            "pattern": {
                "@type": "PathPlus",
                "pattern": {
                    "@type": "PathSequence",
                    "sequence" : [
                        {
                            "@type": "InversePathPredicate",
                            "predicate": "hop",
                        },
                        {
                            "@type": "PathPredicate",
                            "predicate": "hop",
                        },
                    ]
                },
            },
            "object": {
                "@type": "Value",
                "variable": "Y",
            },
            "path": {
                "@type": "Value",
                "variable": "Path",
            },
        }
        assert woql_object.to_dict() == json_object

    def test_double_grouped_path_query(self):
        woql_object = WOQLQuery().path(
            "v:X", "((<hop,hop>)|(<hop2,hop2>))+", "v:Y", "v:Path"
        )
        json_object = {
            "@type": "Path",
            "subject": {
                "@type": "Variable",
                "variable": {"@value": "X", "@type": "xsd:string"},
            },
            "path_pattern": {
                "@type": "PathPlus",
                "path_pattern": {
                    "@type": "PathOr",
                    "or":[
                        { "@type": "PathSequence",
                          "sequence" : [
                              {
                                  "@type": "InversePathPredicate",
                                  "predicate": "hop"
                              },
                              {
                                  "@type": "PathPredicate",
                                  "predicate": "hop",
                              }
                              ]
                         },
                        {  "@type": "PathSequence",
                           "sequence" : [
                               {
                                   "@type": "InversePathPredicate",
                                   "predicate": "hop2",
                               },
                               {
                                   "@type": "PathPredicate",
                                   "predicate": "hop2",
                               }
                           ]
                         },
                    ],
                },
            },
            "object": {
                "@type": "Value",
                "variable": "Y",
            },
            "path": {
                "@type": "Value",
                "variable": "Path"
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
        woql_object = WOQLQuery().delete_object("x")
        json_obj = {"@type": "DeleteObject", "document_uri": "x"}
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
        woql_object = WOQLQuery().node("a", "AddQuad").graph("schema")
        woql_object2 = (
            WOQLQuery()
            .node("x", "add_quad")
            .graph("schema")
            .label("my label", "en")
        )

        assert woql_object.to_dict() == {}
        assert woql_object2.to_dict() == WOQL_JSON["graphMethodJson"]

    def test_node_and_label_method(self):
        woql_object = WOQLQuery().node("x", "add_quad").label("my label", "en")
        woql_object2 = WOQLQuery().node("x", "add_quad").label("v:label")
        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == WOQL_JSON["labelMethodJson"]
        assert woql_object2.to_dict() == WOQL_JSON["labelMethodJson2"]

    def test_add_class_and_description_method(self):
        woql_object = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        assert woql_object.to_dict() == WOQL_JSON["addClassDescJson"]

    def test_abstract_method(self):
        woql_object = WOQLQuery().node("x", "add_quad").abstract()
        assert woql_object.to_dict() == WOQL_JSON["nodeAbstractJson"]

    def test_node_property_method(self):
        woql_object = (
            WOQLQuery().node("x", "add_triple").property("myprop", "value")
        )
        assert woql_object.to_dict() == WOQL_JSON["addNodePropJson"]

    def test_node_parent_method(self):
        woql_object = WOQLQuery().node("x", "add_quad").parent("classParentName")
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
                "@type": "Column",
                "indicator": {"@type": "Indicator", "index": 0},
                "variable": "x",
            },
            {
                "@type": "Column",
                "indicator": {"@type": "Indicator", "index": 1},
                "variable": "y",
            },
            {
                "@type": "Column",
                "indicator": {"@type": "Indicator", "index": 2},
                "variable": "z",
            },
        ]
