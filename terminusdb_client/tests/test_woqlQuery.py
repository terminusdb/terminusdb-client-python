import pprint
import json
import pytest
import requests

import unittest.mock as mock

from terminusdb_client.woqlquery.woql_query import WOQLQuery
from terminusdb_client.woqlclient.woqlClient import WOQLClient

# expected results
from .woqljson.woqlAndJson import WOQL_AND_JSON
from .woqljson.woqlCastJson import WOQL_CAST_JSON
from .woqljson.woqlConcatJson import WOQL_CONCAT_JSON
from .woqljson.woqlDeleteJson import WOQL_DELETE_JSON
from .woqljson.woqlIdgenJson import WOQL_IDGEN_JSON
from .woqljson.woqlInsertJson import WOQL_INSERT_JSON
from .woqljson.woqlJoinSplitJson import WOQL_JOIN_SPLIT_JSON
from .woqljson.woqlJson import WOQL_JSON, WOQL_STAR
from .woqljson.woqlMathJson import WOQL_MATH_JSON
from .woqljson.woqlOrJson import WOQL_OR_JSON
from .woqljson.woqlTrimJson import WOQL_TRIM_JSON
from .woqljson.woqlWhenJson import WOQL_WHEN_JSON

from .mockResponse import mocked_requests

pp = pprint.PrettyPrinter(indent=4)


class TestWoqlQueries:
    def test_start_properties_values(self):
        woql_object = WOQLQuery()
        assert woql_object._chain_ended == False
        assert woql_object._contains_update == False
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

        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == json_obj

    def test_insert_method(self):
        woql_object = WOQLQuery().insert("v:Bike_URL", "Bicycle")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_INSERT_JSON["onlyNode"])
        assert woql_object.to_dict() == WOQL_INSERT_JSON["onlyNode"]

    def test_doctype_method(self):
        # TODO: test in js does not exist
        woql_object = WOQLQuery().doctype("Station")
        pp.pprint(woql_object.to_dict())
        json_obj = {
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

        assert woql_object.to_dict() == json_obj

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

        assert woql_object.to_dict() == WOQL_AND_JSON

    def test_woql_or_method(self):
        woql_object = WOQLQuery().woql_or(
            WOQLQuery().triple("a", "b", "c"), WOQLQuery().triple("1", "2", "3")
        )
        assert woql_object.to_dict() == WOQL_OR_JSON

    def test_when_method(self):
        # TODO: chcek chaining
        woql_object = WOQLQuery().when(True, WOQLQuery().add_class("id"))
        woql_object_chain = WOQLQuery().when(True).add_class("id")
        print("___first try___")
        pp.pprint(woql_object.to_dict())
        print("___second try___")
        pp.pprint(woql_object_chain._cursor)
        pp.pprint(woql_object_chain.to_dict())
        print("___right answer___")
        pp.pprint(WOQL_WHEN_JSON)
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
        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == json_obj

    def test_trim_method(self):
        woql_object = WOQLQuery().trim("a", "b")
        assert woql_object.to_dict() == WOQL_TRIM_JSON

    def test_eval_method(self):
        woql_object = WOQLQuery().eval("1+2", "b")
        assert woql_object.to_dict() == WOQL_MATH_JSON["evalJson"]

    def test_minus_method(self):
        # TODO: interesting args
        woql_object = WOQLQuery().minus("2", "1")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_MATH_JSON["minusJson"])
        assert woql_object.to_dict() == WOQL_MATH_JSON["minusJson"]

    def test_plus_method(self):
        # TODO: interesting args
        woql_object = WOQLQuery().plus("2", "1")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_MATH_JSON["plusJson"])
        assert woql_object.to_dict() == WOQL_MATH_JSON["plusJson"]

    def test_times_method(self):
        # TODO: interesting args
        woql_object = WOQLQuery().times("2", "1")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_MATH_JSON["timesJson"])
        assert woql_object.to_dict() == WOQL_MATH_JSON["timesJson"]

    def test_divide_method(self):
        # TODO: interesting args
        woql_object = WOQLQuery().divide("2", "1")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_MATH_JSON["divideJson"])
        assert woql_object.to_dict() == WOQL_MATH_JSON["divideJson"]

    def test_exp_method(self):
        woql_object = WOQLQuery().exp("2", "1")
        assert woql_object.to_dict() == WOQL_MATH_JSON["expJson"]

    def test_div_method(self):
        # TODO: no expected output
        woql_object = WOQLQuery().div("2", "1")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_MATH_JSON["divJson"])
        assert woql_object.to_dict() == WOQL_MATH_JSON["divJson"]

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
        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == json_obj

    def test_woql_as_method(self):
        woql_object = WOQLQuery().woql_as("Source", "Target")
        woql_object2 = (
            WOQLQuery().woql_as("Source", "Target").woql_as("Source2", "Target2")
        )
        json_obj2 = [
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

        assert woql_object.to_dict() == [json_obj2[0]]
        assert woql_object2.to_dict() == json_obj2

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
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_IDGEN_JSON)
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
        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == json_obj

    def test_cast_method(self):
        woql_object = WOQLQuery().cast("v:Duration", "xsd:integer", "v:Duration_Cast")
        pp.pprint(woql_object.to_dict())
        pp.pprint(WOQL_CAST_JSON)
        assert woql_object.to_dict() == WOQL_CAST_JSON

    def test_re_method(self):
        woql_object = WOQLQuery().re("!\\w+(.*)test$", "v:string", "v:formated")
        json_obj = {
            '@type': 'woql:Regexp',
            'woql:pattern': {
                '@type': 'woql:Datatype',
                'woql:datatype': {
                    '@type': 'xsd:string',
                    '@value': '!\\w+(.*)test$'
                }
            },
            'woql:regexp_list': {
                '@type': 'woql:Variable',
                'woql:variable_name': {
                    '@type': 'xsd:string',
                    '@value': 'formated'
                }
            },
            'woql:regexp_string': {
                '@type': 'woql:Variable',
                'woql:variable_name': {
                    '@type': 'xsd:string',
                    '@value': 'string'}
                }
            }

        pp.pprint(woql_object.to_dict())
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
                "woql:variable_name": {"@value": "member", "@type": "xsd:string",},
            },
            "woql:member_list": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "list_obj", "@type": "xsd:string",},
            },
        }
        assert woql_object.to_dict() == json_obj

    def test_concat_method(self):
        woql_object = WOQLQuery().concat("v:Duration yo v:Duration_Cast", "v:x")
        pp.pprint(woql_object.to_dict())
        print("___json____")
        pp.pprint(WOQL_CONCAT_JSON)
        assert woql_object.to_dict() == WOQL_CONCAT_JSON

    def test_group_by_method(self):
        woql_object = (
            WOQLQuery()
            .group_by(["v:A", "v:B"], ["v:C"], "v:New")
            .triple("v:A", "v:B", "v:C")
        )
        pp.pprint(woql_object.to_dict())
        print("---------")
        pp.pprint(WOQL_JSON["groupbyJson"])
        assert woql_object.to_dict() == WOQL_JSON["groupbyJson"]

    def test_order_by_method_asc(self):
        woql_object = WOQLQuery().order_by("v:A", "v:B asc", "v:C asc").star()
        pp.pprint(woql_object.to_dict())
        print("____xxxx___")
        pp.pprint(WOQL_JSON["orderbyJson"])
        assert woql_object.to_dict() == WOQL_JSON["orderbyJson"]


class TestTripleBuilder:
    def test_triple_method(self):
        woql_object = WOQLQuery().triple("a", "b", "c")
        assert woql_object.to_dict() == WOQL_JSON["tripleJson"]

    def test_quad_method(self):
        woql_object = WOQLQuery().quad("a", "b", "c", "d")
        assert woql_object.to_dict() == WOQL_JSON["quadJson"]

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
        json_obj = {
            "@type": "woql:DeleteObject",
            "woql:document_uri": "doc:x"
        }
        pp.pprint(woql_object.to_dict())
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
        pp.pprint(woql_object)
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
        assert woql_object.to_dict() == WOQL_JSON["labelMethodJson"]
        assert woql_object2.to_dict() == WOQL_JSON["labelMethodJson2"]

    def test_add_class_and_description_method(self):
        woql_object = (
            WOQLQuery().add_class("NewClass").description("A new class object.")
        )
        pp.pprint(woql_object._cursor)
        print("-------")
        pp.pprint(woql_object._query)
        print("-------")
        pp.pprint(woql_object.to_dict())
        print("-----")
        pp.pprint(WOQL_JSON["addClassDescJson"])
        # assert False
        assert woql_object.to_dict() == WOQL_JSON["addClassDescJson"]

    def test_comment_method(self):
        woql_object = WOQLQuery().comment("my comment")
        json_obj = {
            "@type": "woql:Comment",
            "woql:comment": {"@type": "xsd:string", "@value": "my comment"},
        }
        pp.pprint(woql_object.to_dict())
        assert woql_object.to_dict() == json_obj

    def test_abstract_method(self):
        woql_object = WOQLQuery().node("doc:x", "add_quad").abstract()
        assert woql_object.to_dict() == WOQL_JSON["nodeAbstractJson"]

    def test_chained_doctype_method(self):
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
        assert woql_object.to_dict() == WOQL_JSON["chainDoctypeJson"]

    def test_chained_insert_method(self):
        woql_object = (
            WOQLQuery()
            .insert("v:Node_ID", "v:Type")
            .label("v:Label")
            .description("v:Description")
            .property("prop", "v:Prop")
            .property("prop", "v:Prop2")
            .parent("myParentClass")
        )
        assert woql_object.to_dict() == WOQL_JSON["chainInsertJson"]

    def test_cardinality_method(self):
        woql_object = WOQLQuery().add_property("P", "string").cardinality(3)
        assert woql_object.to_dict() == WOQL_JSON["propCardinalityJson"]

    def test_property_min_method(self):
        woql_object = WOQLQuery().add_property("P", "string").min(2)
        assert woql_object.to_dict() == WOQL_JSON["propMinJson"]

    def test_max_method(self):
        woql_object = WOQLQuery().add_property("P", "string").max(4)
        assert woql_object.to_dict() == WOQL_JSON["propertyMaxJson"]

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

    @mock.patch("requests.post", side_effect=mocked_requests)
    @mock.patch("requests.get", side_effect=mocked_requests)
    def test_execute_mehtod(self, mocked_requests, mocked_requests2):
        woql_client = WOQLClient("http://localhost:6363")
        woql_client.connect(user="admin", account="admin", key="root", db="myDBName")
        woql_object = WOQLQuery().star()
        woql_object.execute(woql_client)

        requests.post.assert_called_once_with(
            "http://localhost:6363/woql/admin/myDBName/local/branch/master",
            headers={
                "Authorization": "Basic YWRtaW46cm9vdA==",
                "content-type": "application/json",
            },
            json={
                "commit_info": {"author": "admin", "message": "Automatically Added Commit"},
                "query": json.dumps(WOQL_STAR, sort_keys=True),
            },
        )
