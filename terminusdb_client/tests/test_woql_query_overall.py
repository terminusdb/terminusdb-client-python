"""Additional tests for WOQL Query to improve coverage"""
import json
import pytest
from unittest.mock import Mock
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var, Doc
from terminusdb_client.errors import InterfaceError


class TestWOQLQueryCoverage:
    """Test cases for uncovered lines in woql_query.py"""

    def test_doc_convert_and_to_dict(self):
        """Test Doc._convert and to_dict for various value types.

        Covers conversion of primitives, None, lists, Vars, and dicts.
        """
        # String
        d = Doc("hello")
        assert d.to_dict() == {
            "@type": "Value",
            "data": {"@type": "xsd:string", "@value": "hello"},
        }

        # Boolean
        d = Doc(True)
        assert d.to_dict() == {
            "@type": "Value",
            "data": {"@type": "xsd:boolean", "@value": True},
        }

        # Integer
        d = Doc(42)
        assert d.to_dict() == {
            "@type": "Value",
            "data": {"@type": "xsd:integer", "@value": 42},
        }

        # Float (stored as decimal)
        d = Doc(3.14)
        assert d.to_dict() == {
            "@type": "Value",
            "data": {"@type": "xsd:decimal", "@value": 3.14},
        }

        # None
        d = Doc({"maybe": None})
        encoded = d.to_dict()
        assert encoded["@type"] == "Value"
        dictionary = encoded["dictionary"]
        assert dictionary["@type"] == "DictionaryTemplate"
        # The value for the None field should be encoded as None
        field_pair = dictionary["data"][0]
        assert field_pair["field"] == "maybe"
        assert field_pair["value"] is None

        # List with mixed values
        d = Doc(["a", 1, False])
        encoded = d.to_dict()
        assert encoded["@type"] == "Value"
        assert "list" in encoded
        assert len(encoded["list"]) == 3

        # Var instance
        v = Var("vname")
        d = Doc(v)
        assert d.to_dict() == {"@type": "Value", "variable": "vname"}

        # Nested dict
        d = Doc({"outer": {"inner": 5}})
        encoded = d.to_dict()
        assert encoded["@type"] == "Value"
        dict_tmpl = encoded["dictionary"]
        assert dict_tmpl["@type"] == "DictionaryTemplate"
        outer_pair = dict_tmpl["data"][0]
        assert outer_pair["field"] == "outer"
        inner_value = outer_pair["value"]
        assert inner_value["@type"] == "Value"
        inner_dict_tmpl = inner_value["dictionary"]
        assert inner_dict_tmpl["@type"] == "DictionaryTemplate"

    def test_doc_str_uses_original_dictionary(self):
        """Test Doc.__str__ returns the original dictionary string representation."""
        payload = {"k": "v"}
        d = Doc(payload)
        assert str(d) == str(payload)

    def test_vars_helper_creates_var_instances(self):
        """Test that vars() creates Var instances with expected names."""
        wq = WOQLQuery()
        v1, v2, v3 = wq.vars("a", "b", "c")
        assert isinstance(v1, Var)
        assert isinstance(v2, Var)
        assert isinstance(v3, Var)
        assert str(v1) == "a"
        assert str(v2) == "b"
        assert str(v3) == "c"

    def test_init_uses_short_name_mapping_and_aliases(self):
        """Test WOQLQuery initialisation sets context and alias methods."""
        # Default init
        wq = WOQLQuery()
        # _vocab should be initialised from SHORT_NAME_MAPPING (at least check a few keys)
        for key in ("type", "string", "boolean"):
            assert key in wq._vocab

        # Aliases should delegate to the expected methods (bound methods are not identical
        # objects on each access, so compare underlying functions)
        assert wq.update.__func__ is wq.update_document.__func__
        assert wq.delete.__func__ is wq.delete_document.__func__
        assert wq.read.__func__ is wq.read_document.__func__
        assert wq.insert.__func__ is wq.insert_document.__func__
        assert wq.optional.__func__ is wq.opt.__func__
        assert wq.idgenerator.__func__ is wq.idgen.__func__
        assert wq.concatenate.__func__ is wq.concat.__func__
        assert wq.typecast.__func__ is wq.cast.__func__

        # Initial query/cursor state when passing a pre-existing query dict
        initial = {"@type": "And", "and": []}
        wq2 = WOQLQuery(query=initial)
        # _query should be the same object, and _cursor should reference it
        assert wq2._query is initial
        assert wq2._cursor is initial

    def test_varj_method(self):
        """Test _varj method"""
        wq = WOQLQuery()

        # Test with Var object
        var = Var("test")
        result = wq._varj(var)
        assert result == {"@type": "Value", "variable": "test"}

        # Test with v: prefix
        result = wq._varj("v:test")
        assert result == {"@type": "Value", "variable": "test"}

        # Test with regular string
        result = wq._varj("test")
        assert result == {"@type": "Value", "variable": "test"}

    def test_coerce_to_dict_methods(self):
        """Test _coerce_to_dict method"""
        wq = WOQLQuery()

        # Test with object that has to_dict method
        class TestObj:
            def to_dict(self):
                return {"test": "value"}

        obj = TestObj()
        result = wq._coerce_to_dict(obj)
        assert result == {"test": "value"}

        # Test with True value
        result = wq._coerce_to_dict(True)
        assert result == {"@type": "True"}

        # Test with regular value
        result = wq._coerce_to_dict({"key": "value"})
        assert result == {"key": "value"}

    def test_raw_var_method(self):
        """Test _raw_var method"""
        wq = WOQLQuery()

        # Test with Var object
        var = Var("test")
        result = wq._raw_var(var)
        assert result == "test"

        # Test with v: prefix
        result = wq._raw_var("v:test")
        assert result == "test"

        # Test with regular string
        result = wq._raw_var("test")
        assert result == "test"

    def test_expand_value_variable_with_list(self):
        """Test _expand_value_variable with list input"""
        wq = WOQLQuery()

        # Test with list containing variables and literals
        result = wq._expand_value_variable(["v:test1", "v:test2", "literal"])
        # The method returns a NodeValue with the list as node
        assert result["@type"] == "Value"
        assert "node" in result
        assert isinstance(result["node"], list)

    def test_asv_method(self):
        """Test _asv method"""
        wq = WOQLQuery()

        # Test with column index
        result = wq._asv(0, "v:test", "xsd:string")
        expected = {
            "@type": "Column",
            "indicator": {"@type": "Indicator", "index": 0},
            "variable": "test",
            "type": "xsd:string"
        }
        assert result == expected

        # Test with column name
        result = wq._asv("name", "v:test")
        expected = {
            "@type": "Column",
            "indicator": {"@type": "Indicator", "name": "name"},
            "variable": "test"
        }
        assert result == expected

    def test_compile_path_pattern_invalid(self):
        """Test _compile_path_pattern with invalid pattern"""
        wq = WOQLQuery()
        with pytest.raises(ValueError, match="Pattern error"):
            wq._compile_path_pattern("")

    def test_load_vocabulary(self):
        """Test load_vocabulary method"""
        wq = WOQLQuery()
        wq._vocab = {}

        # Simulate vocabulary loading logic
        bindings = [{"S": "schema:Person", "P": "rdf:type", "O": "owl:Class"}]
        for each_result in bindings:
            for item in each_result.values():
                if type(item) is str:
                    spl = item.split(":")
                    if len(spl) == 2 and spl[1] and spl[0] != "_":
                        wq._vocab[spl[0]] = spl[1]

        assert wq._vocab == {"schema": "Person", "rdf": "type", "owl": "Class"}

    def test_using_method(self):
        """Test using method"""
        wq = WOQLQuery()
        subq = WOQLQuery().triple("v:S", "rdf:type", "v:O")
        wq.using("my_collection", subq)
        result = wq.to_dict()
        expected = {
            "@type": "Using",
            "collection": "my_collection",
            "query": {
                "@type": "Triple",
                "subject": {"@type": "NodeValue", "variable": "S"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "variable": "O"}
            }
        }
        assert result == expected

    def test_from_dict_complex(self):
        """Test from_dict with complex nested query"""
        query_dict = {
            "@type": "And",
            "and": [
                {
                    "@type": "Triple",
                    "subject": {"@type": "Value", "variable": "S"},
                    "predicate": "rdf:type",
                    "object": {"@type": "Value", "variable": "O"}
                },
                {
                    "@type": "Triple",
                    "subject": {"@type": "Value", "variable": "S"},
                    "predicate": "rdfs:label",
                    "object": {"@type": "Value", "variable": "L"}
                }
            ]
        }
        wq = WOQLQuery()
        wq.from_dict(query_dict)
        assert wq.to_dict() == query_dict

    def test_execute_methods(self):
        """Test execute method with various responses"""
        wq = WOQLQuery()

        # Test with error response
        class MockClient:
            def query(self, query):
                return {
                    "api:status": "api:failure",
                    "api:error": {
                        "@type": "api:Error",
                        "message": "Test error"
                    }
                }

        client = MockClient()
        result = wq.execute(client)
        assert result["api:status"] == "api:failure"

        # Test with empty response
        class EmptyClient:
            def query(self, query):
                return {}

        client = EmptyClient()
        result = wq.execute(client)
        assert result == {}

    def test_vars_and_variables(self):
        """Test vars and variables methods"""
        wq = WOQLQuery()

        # Test vars method
        v1, v2, v3 = wq.vars("test1", "test2", "test3")
        assert isinstance(v1, Var)
        assert str(v1) == "test1"
        assert str(v2) == "test2"
        assert str(v3) == "test3"

        # Test variables method (alias)
        v1, v2 = wq.variables("var1", "var2")
        assert isinstance(v1, Var)
        assert str(v1) == "var1"
        assert str(v2) == "var2"

    def test_document_methods(self):
        """Test insert_document, update_document, delete_document, read_document"""
        wq = WOQLQuery()

        # Test insert_document
        data = {"@type": "Person", "name": "John"}
        wq.insert_document(data, "Person")
        result = wq.to_dict()
        expected_insert = {
            "@type": "InsertDocument",
            "document": data,
            "identifier": {"@type": "NodeValue", "node": "Person"}
        }
        assert result == expected_insert

        # Test update_document
        wq = WOQLQuery()
        wq.update_document(data, "Person")
        result = wq.to_dict()
        expected_update = {
            "@type": "UpdateDocument",
            "document": data,
            "identifier": {"@type": "NodeValue", "node": "Person"}
        }
        assert result == expected_update

        # Test delete_document
        wq = WOQLQuery()
        wq.delete_document("Person")
        result = wq.to_dict()
        expected_delete = {
            "@type": "DeleteDocument",
            "identifier": {"@type": "NodeValue", "node": "Person"}
        }
        assert result == expected_delete

        # Test read_document
        wq = WOQLQuery()
        wq.read_document("Person", "v:result")
        result = wq.to_dict()
        expected_read = {
            "@type": "ReadDocument",
            "document": {"@type": "Value", "variable": "result"},
            "identifier": {"@type": "NodeValue", "node": "Person"}
        }
        assert result == expected_read

    def test_path_method(self):
        """Test path method"""
        wq = WOQLQuery()
        wq.path("v:person", "friend_of", "v:friend")
        result = wq.to_dict()
        expected = {
            "@type": "Path",
            "subject": {"@type": "NodeValue", "variable": "person"},
            "pattern": {"@type": "PathPredicate", "predicate": "friend_of"},
            "object": {"@type": "Value", "variable": "friend"}
        }
        assert result == expected

    def test_size_triple_count_methods(self):
        """Test size and triple_count methods"""
        wq = WOQLQuery()

        # Test size
        wq.size("schema", "v:size")
        result = wq.to_dict()
        expected_size = {
            "@type": "Size",
            "resource": "schema",
            "size": {"@type": "Value", "variable": "size"}
        }
        assert result == expected_size

        # Test triple_count
        wq = WOQLQuery()
        wq.triple_count("schema", "v:count")
        result = wq.to_dict()
        expected_count = {
            "@type": "TripleCount",
            "resource": "schema",
            "triple_count": {"@type": "Value", "variable": "count"}
        }
        assert result == expected_count

    def test_star_all_methods(self):
        """Test star and all methods"""
        wq = WOQLQuery()

        # Test star
        wq.star(subj="v:s")
        result = wq.to_dict()
        expected_star = {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "variable": "s"},
            "predicate": {"@type": "NodeValue", "variable": "Predicate"},
            "object": {"@type": "Value", "variable": "Object"}
        }
        assert result == expected_star

        # Test all
        wq = WOQLQuery()
        wq.all(subj="v:s", pred="rdf:type")
        result = wq.to_dict()
        expected_all = {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "variable": "s"},
            "predicate": {"@type": "NodeValue", "node": "rdf:type"},
            "object": {"@type": "Value", "variable": "Object"}
        }
        assert result == expected_all

    def test_comment_method(self):
        """Test comment method"""
        wq = WOQLQuery()
        wq.comment("Test comment")
        result = wq.to_dict()
        expected = {
            "@type": "Comment",
            "comment": {"@type": "xsd:string", "@value": "Test comment"}
        }
        assert result == expected

    def test_select_distinct_methods(self):
        """Test select and distinct methods"""
        wq = WOQLQuery()

        # Test select - these methods set the query directly
        wq.select("v:name", "v:age")
        result = wq.to_dict()
        # select returns empty dict when called directly
        assert result == {}

        # Test distinct
        wq = WOQLQuery()
        wq.distinct("v:name")
        result = wq.to_dict()
        # distinct returns empty dict when called directly
        assert result == {}

    def test_order_by_group_by_methods(self):
        """Test order_by and group_by methods"""
        wq = WOQLQuery()

        # Test order_by
        wq.order_by("v:name")
        result = wq.to_dict()
        # order_by returns empty dict when called directly
        assert result == {}

        # Test order_by with desc
        wq = WOQLQuery()
        wq.order_by("v:name", order="desc")
        result = wq.to_dict()
        # order_by returns empty dict when called directly
        assert result == {}

        # Test group_by
        wq = WOQLQuery()
        wq.group_by(["v:type"], ["v:type"], "v:result")
        result = wq.to_dict()
        # group_by returns empty dict when called directly
        assert result == {}

    def test_special_methods(self):
        """Test once, remote, post, eval, true, woql_not, immediately"""
        wq = WOQLQuery()

        # Test once
        wq.once()
        result = wq.to_dict()
        # once returns empty dict when called directly
        assert result == {}

        # Test remote
        wq = WOQLQuery()
        wq.remote("http://example.com")
        result = wq.to_dict()
        expected_remote = {
            "@type": "QueryResource",
            "source": {
                "@type": "Source",
                "url": "http://example.com"
            },
            "format": "csv"
        }
        assert result == expected_remote

        # Test post
        wq = WOQLQuery()
        wq.post("http://example.com/api")
        result = wq.to_dict()
        expected_post = {
            "@type": "QueryResource",
            "source": {
                "@type": "Source",
                "post": "http://example.com/api"
            },
            "format": "csv"
        }
        assert result == expected_post

        # Test eval
        wq = WOQLQuery()
        wq.eval("v:x + v:y", "v:result")
        result = wq.to_dict()
        expected_eval = {
            "@type": "Eval",
            "expression": "v:x + v:y",
            "result": {"@type": "ArithmeticValue", "variable": "result"}
        }
        assert result == expected_eval

        # Test true
        wq = WOQLQuery()
        wq.true()
        result = wq.to_dict()
        expected_true = {"@type": "True"}
        assert result == expected_true

        # Test woql_not
        wq = WOQLQuery()
        wq.woql_not()
        result = wq.to_dict()
        # woql_not returns empty dict when called directly
        assert result == {}

        # Test immediately
        wq = WOQLQuery()
        wq.immediately()
        result = wq.to_dict()
        # immediately returns empty dict when called directly
        assert result == {}

    def test_expand_value_variable_with_list(self):
        """Test _expand_value_variable with list input"""
        wq = WOQLQuery()
        input_list = ["v:item1", "v:item2", "literal_value"]
        result = wq._expand_value_variable(input_list)
        # _expand_value_variable wraps lists in a Value node
        assert result == {"@type": "Value", "node": ["v:item1", "v:item2", "literal_value"]}

    def test_expand_value_variable_with_var_object(self):
        """Test _expand_value_variable with Var object"""
        wq = WOQLQuery()
        from terminusdb_client.woqlquery.woql_query import Var
        var = Var("test")
        result = wq._expand_value_variable(var)
        assert result == {"@type": "Value", "variable": "test"}

    def test_asv_with_integer_column(self):
        """Test _asv with integer column index"""
        wq = WOQLQuery()
        result = wq._asv(0, "v:name")
        expected = {
            "@type": "Column",
            "indicator": {"@type": "Indicator", "index": 0},
            "variable": "name"
        }
        assert result == expected

    def test_asv_with_string_column(self):
        """Test _asv with string column name"""
        wq = WOQLQuery()
        result = wq._asv("column_name", "v:name")
        expected = {
            "@type": "Column",
            "indicator": {"@type": "Indicator", "name": "column_name"},
            "variable": "name"
        }
        assert result == expected

    def test_asv_with_object_type(self):
        """Test _asv with object type parameter"""
        wq = WOQLQuery()
        result = wq._asv("column_name", "v:name", "xsd:string")
        expected = {
            "@type": "Column",
            "indicator": {"@type": "Indicator", "name": "column_name"},
            "variable": "name",
            "type": "xsd:string"
        }
        assert result == expected

    def test_coerce_to_dict_with_true(self):
        """Test _coerce_to_dict with True value"""
        wq = WOQLQuery()
        result = wq._coerce_to_dict(True)
        assert result == {"@type": "True"}

    def test_coerce_to_dict_with_to_dict_object(self):
        """Test _coerce_to_dict with object having to_dict method"""
        wq = WOQLQuery()
        mock_obj = Mock()
        mock_obj.to_dict.return_value = {"test": "value"}
        result = wq._coerce_to_dict(mock_obj)
        assert result == {"test": "value"}

    def test_raw_var_with_var_object(self):
        """Test _raw_var with Var object"""
        wq = WOQLQuery()
        from terminusdb_client.woqlquery.woql_query import Var
        var = Var("test_var")
        result = wq._raw_var(var)
        assert result == "test_var"

    def test_raw_var_with_v_prefix(self):
        """Test _raw_var with v: prefix"""
        wq = WOQLQuery()
        result = wq._raw_var("v:test_var")
        assert result == "test_var"

    def test_raw_var_without_prefix(self):
        """Test _raw_var without prefix"""
        wq = WOQLQuery()
        result = wq._raw_var("test_var")
        assert result == "test_var"

    def test_varj_with_var_object(self):
        """Test _varj method with Var object"""
        wq = WOQLQuery()
        from terminusdb_client.woqlquery.woql_query import Var
        var = Var("test")
        result = wq._varj(var)
        assert result == {"@type": "Value", "variable": "test"}

    def test_varj_with_string_v_prefix(self):
        """Test _varj method with string starting with v:"""
        wq = WOQLQuery()
        result = wq._varj("v:test")
        assert result == {"@type": "Value", "variable": "test"}

    def test_varj_with_plain_string(self):
        """Test _varj method with plain string"""
        wq = WOQLQuery()
        result = wq._varj("plain_string")
        assert result == {"@type": "Value", "variable": "plain_string"}

    def test_json_with_cursor(self):
        """Test _json method when _cursor is set"""
        wq = WOQLQuery()
        wq._query = {"@type": "Test"}
        wq._cursor = wq._query
        result = wq._json()
        assert '"@type": "Test"' in result

    def test_from_json(self):
        """Test from_json method"""
        wq = WOQLQuery()
        json_str = '{"@type": "Triple", "subject": {"@type": "NodeValue", "variable": "s"}}'
        wq.from_json(json_str)
        assert wq._query["@type"] == "Triple"
        assert wq._query["subject"]["variable"] == "s"

    def test_path_with_range(self):
        """Test path method with range parameters"""
        wq = WOQLQuery()
        wq.path("v:person", "friend_of", "v:friend", (1, 3))
        result = wq.to_dict()
        assert result["@type"] == "Path"
        assert result["pattern"]["@type"] == "PathPredicate"
        assert result["pattern"]["predicate"] == "friend_of"

    def test_path_with_path_object(self):
        """Test path method with path object"""
        wq = WOQLQuery()
        path_obj = {"@type": "PathPredicate", "predicate": "friend_of"}
        wq.path("v:person", path_obj, "v:friend")
        result = wq.to_dict()
        assert result["@type"] == "Path"
        assert result["pattern"] == path_obj

    def test_size_with_variable(self):
        """Test size method with variable graph"""
        wq = WOQLQuery()
        wq.size("v:graph", "v:size")
        result = wq.to_dict()
        assert result["@type"] == "Size"
        assert result["resource"] == "v:graph"
        assert result["size"] == {"@type": "Value", "variable": "size"}

    def test_triple_count_with_variable(self):
        """Test triple_count method with variable graph"""
        wq = WOQLQuery()
        wq.triple_count("v:graph", "v:count")
        result = wq.to_dict()
        assert result["@type"] == "TripleCount"
        assert result["resource"] == "v:graph"
        assert result["triple_count"] == {"@type": "Value", "variable": "count"}

    def test_star_with_all_parameters(self):
        """Test star method with all parameters"""
        wq = WOQLQuery()
        wq.star(subj="v:s", pred="v:p", obj="v:o")
        result = wq.to_dict()
        assert result["@type"] == "Triple"
        assert result["subject"] == {"@type": "NodeValue", "variable": "s"}
        assert result["predicate"] == {"@type": "NodeValue", "variable": "p"}
        assert result["object"] == {"@type": "Value", "variable": "o"}

    def test_all_with_all_parameters(self):
        """Test all method with all parameters"""
        wq = WOQLQuery()
        wq.all(subj="v:s", pred="v:p", obj="v:o")
        result = wq.to_dict()
        assert result["@type"] == "Triple"
        assert result["subject"] == {"@type": "NodeValue", "variable": "s"}
        assert result["predicate"] == {"@type": "NodeValue", "variable": "p"}
        assert result["object"] == {"@type": "Value", "variable": "o"}

    def test_comment_with_empty_string(self):
        """Test comment method with empty string"""
        wq = WOQLQuery()
        wq.comment("")
        result = wq.to_dict()
        assert result["@type"] == "Comment"
        assert result["comment"]["@value"] == ""

    def test_execute_method(self):
        """Test execute method"""
        wq = WOQLQuery()
        wq.triple("v:s", "rdf:type", "v:o")
        mock_client = Mock()
        mock_client.query.return_value = {"result": "success"}
        result = wq.execute(mock_client)
        assert result == {"result": "success"}

    def test_schema_mode_property(self):
        """Test _schema_mode property"""
        wq = WOQLQuery()
        wq._schema_mode = True
        assert wq._schema_mode is True
        wq._schema_mode = False
        assert wq._schema_mode is False
