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
            "query": {"@type": "Start", "query": WOQL_STAR, "start": 0},
        }
        assert woql_object.to_dict() == json_obj

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
                    "node": "c",
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
            "graph": "schema",
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
            "right": {"@type": "Value", "node": "b"},
        }
        assert woql_object.to_dict() == json_obj

    def test_trim_method(self):
        woql_object = WOQLQuery().trim("a", "b")
        assert woql_object.to_dict() == WOQL_TRIM_JSON

    def test_eval_method(self):
        woql_object = WOQLQuery().eval(WOQLQuery().plus(1, 2), "v:x")
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
            "format": "csv",
            "source": {"@type": "Source", "url": "http://url"},
        }
        assert woql_object.to_dict() == json_obj

    def test_post_method(self):
        woql_object = WOQLQuery().post({"file": "my_json_file", "format": "csv"})
        json_obj = {
            "@type": "QueryResource",
            "source": {"file": "my_json_file", "format": "csv", "@type": "Source"},
            "format": "csv",
        }
        assert woql_object.to_dict() == json_obj

    def test_unique_method(self):
        woql_object = WOQLQuery().unique("Station", "v:Start_ID", "v:Start_Station_URL")
        assert woql_object.to_dict() == WOQL_UNIQUE_JSON

    def test_idgen_method(self):
        woql_object = WOQLQuery().idgen("Station", "v:Start_ID", "v:Start_Station_URL")
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
            "value": {
                "@type": "Value",
                "variable": "Duration",
            },
            "type": {"@type": "NodeValue", "node": "xsd:integer"},
            "result": {"@type": "Value", "variable": "Duration_Cast"},
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
        woql_object3 = WOQLQuery().cast("my_int", "xsd:integer", "v:Duration_Cast")
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
            "result": {
                "@type": "DataValue",
                "variable": "formated",
            },
            "string": {
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
        woql_object = WOQLQuery().concat(
            ["v:Duration", " yo ", "v:Duration_Cast"], "v:x"
        )
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
                "@type": "NodeValue",
                "variable": "X",
            },
            "pattern": {
                "@type": "PathPredicate",
                "predicate": "hop",
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

    def test_plus_directed_path_query(self):
        woql_object = WOQLQuery().path("v:X", "<hop+", "v:Y", "v:Path")
        json_object = {
            "@type": "Path",
            "subject": {
                "@type": "NodeValue",
                "variable": "X",
            },
            "pattern": {
                "@type": "PathPlus",
                "plus": {
                    "@type": "InversePathPredicate",
                    "predicate": "hop",
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
                "plus": {
                    "@type": "PathSequence",
                    "sequence": [
                        {
                            "@type": "InversePathPredicate",
                            "predicate": "hop",
                        },
                        {
                            "@type": "PathPredicate",
                            "predicate": "hop",
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
                "@type": "NodeValue",
                "variable": "X",
            },
            "pattern": {
                "@type": "PathPlus",
                "plus": {
                    "@type": "PathOr",
                    "or": [
                        {
                            "@type": "PathSequence",
                            "sequence": [
                                {"@type": "InversePathPredicate", "predicate": "hop"},
                                {
                                    "@type": "PathPredicate",
                                    "predicate": "hop",
                                },
                            ],
                        },
                        {
                            "@type": "PathSequence",
                            "sequence": [
                                {
                                    "@type": "InversePathPredicate",
                                    "predicate": "hop2",
                                },
                                {
                                    "@type": "PathPredicate",
                                    "predicate": "hop2",
                                },
                            ],
                        },
                    ],
                },
            },
            "object": {
                "@type": "Value",
                "variable": "Y",
            },
            "path": {"@type": "Value", "variable": "Path"},
        }
        assert woql_object.to_dict() == json_object


class TestTripleBuilder:
    def test_triple_method(self, triple_opt):
        woql_object = WOQLQuery().triple("a", "b", "c")
        woql_object_opt = WOQLQuery().triple(
            "a", "b", WOQLQuery().string("c"), opt=True
        )
        assert woql_object.to_dict() == WOQL_JSON["tripleJson"]
        assert woql_object_opt.to_dict() == triple_opt

    def test_quad_method(self, quad_opt):
        woql_object = WOQLQuery().quad("a", "b", "c", "d")
        woql_object_opt = WOQLQuery().quad(
            "a", "b", WOQLQuery().string("c"), "d", opt=True
        )
        assert woql_object.to_dict() == WOQL_JSON["quadJson"]
        assert woql_object_opt.to_dict() == quad_opt

    def test_sub_method(self):
        woql_object = WOQLQuery().sub("ClassA", "ClassB")
        assert woql_object.to_dict() == WOQL_JSON["subsumptionJson"]

    def test_isa_method(self):
        woql_object = WOQLQuery().isa("instance", "Class")
        assert woql_object.to_dict() == WOQL_JSON["isAJson"]

    def test_delete_method(self):
        woql_object = WOQLQuery().delete_object("x")
        json_obj = {
            "@type": "DeleteObject",
            "document_uri": {"@type": "NodeValue", "node": "x"},
        }
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


class TestTripleBuilderChainer:
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
