"""Tests for woql_test_helpers"""

import pytest
from terminusdb_client.tests.woql_test_helpers import WOQLTestHelpers, helpers
from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestWOQLTestHelpers:
    """Test all methods in WOQLTestHelpers"""

    def test_helpers_function(self):
        """Test the helpers() convenience function"""
        result = helpers()
        # helpers() returns the class itself, not an instance
        assert result is WOQLTestHelpers
        # Test that we can create an instance from it
        instance = result()
        assert isinstance(instance, WOQLTestHelpers)

    def test_create_mock_client(self):
        """Test create_mock_client method"""
        client = WOQLTestHelpers.create_mock_client()
        assert hasattr(client, "query")
        result = client.query({})
        assert result == {"@type": "api:WoqlResponse"}

    def test_assert_query_type_success(self):
        """Test assert_query_type with correct type"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        # Should not raise
        WOQLTestHelpers.assert_query_type(query, "Triple")

    def test_assert_query_type_failure(self):
        """Test assert_query_type with wrong type"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        with pytest.raises(AssertionError, match="Expected @type=And"):
            WOQLTestHelpers.assert_query_type(query, "And")

    def test_assert_has_key_success(self):
        """Test assert_has_key with existing key"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        # Should not raise
        WOQLTestHelpers.assert_has_key(query, "subject")

    def test_assert_has_key_failure(self):
        """Test assert_has_key with missing key"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        with pytest.raises(AssertionError, match="Expected key 'missing'"):
            WOQLTestHelpers.assert_has_key(query, "missing")

    def test_assert_key_value_success(self):
        """Test assert_key_value with correct value"""
        query = WOQLQuery()
        query._query = {"test": "value"}
        # Should not raise
        WOQLTestHelpers.assert_key_value(query, "test", "value")

    def test_assert_key_value_failure(self):
        """Test assert_key_value with wrong value"""
        query = WOQLQuery()
        query._query = {"test": "actual"}
        with pytest.raises(AssertionError, match="Expected test=expected"):
            WOQLTestHelpers.assert_key_value(query, "test", "expected")

    def test_assert_is_variable_success(self):
        """Test assert_is_variable with valid variable"""
        var = {"@type": "Value", "variable": "test"}
        # Should not raise
        WOQLTestHelpers.assert_is_variable(var)

    def test_assert_is_variable_with_name(self):
        """Test assert_is_variable with expected name"""
        var = {"@type": "Value", "variable": "test"}
        # Should not raise
        WOQLTestHelpers.assert_is_variable(var, "test")

    def test_assert_is_variable_failure_not_dict(self):
        """Test assert_is_variable with non-dict"""
        with pytest.raises(AssertionError, match="Expected dict"):
            WOQLTestHelpers.assert_is_variable("not a dict")

    def test_assert_is_variable_failure_wrong_type(self):
        """Test assert_is_variable with wrong type"""
        var = {"@type": "WrongType", "variable": "test"}
        with pytest.raises(AssertionError, match="Expected variable type"):
            WOQLTestHelpers.assert_is_variable(var)

    def test_assert_is_variable_failure_no_variable(self):
        """Test assert_is_variable without variable key"""
        var = {"@type": "Value"}
        with pytest.raises(AssertionError, match="Expected 'variable' key"):
            WOQLTestHelpers.assert_is_variable(var)

    def test_assert_is_variable_failure_wrong_name(self):
        """Test assert_is_variable with wrong name"""
        var = {"@type": "Value", "variable": "actual"}
        with pytest.raises(AssertionError, match="Expected variable name 'expected'"):
            WOQLTestHelpers.assert_is_variable(var, "expected")

    def test_assert_is_node_success(self):
        """Test assert_is_node with valid node"""
        node = {"node": "test"}
        # Should not raise
        WOQLTestHelpers.assert_is_node(node)

    def test_assert_is_node_with_expected(self):
        """Test assert_is_node with expected node value"""
        node = {"node": "test"}
        # Should not raise
        WOQLTestHelpers.assert_is_node(node, "test")

    def test_assert_is_node_success_node_value(self):
        """Test assert_is_node with NodeValue type"""
        node = {"@type": "NodeValue", "variable": "test"}
        # Should not raise
        WOQLTestHelpers.assert_is_node(node)

    def test_assert_is_node_failure_not_dict(self):
        """Test assert_is_node with non-dict"""
        with pytest.raises(AssertionError, match="Expected dict"):
            WOQLTestHelpers.assert_is_node("not a dict")

    def test_assert_is_node_failure_wrong_structure(self):
        """Test assert_is_node with wrong structure"""
        node = {"wrong": "structure"}
        with pytest.raises(AssertionError, match="Expected node structure"):
            WOQLTestHelpers.assert_is_node(node)

    def test_assert_is_node_failure_wrong_value(self):
        """Test assert_is_node with wrong node value"""
        node = {"node": "actual"}
        with pytest.raises(AssertionError, match="Expected node 'expected'"):
            WOQLTestHelpers.assert_is_node(node, "expected")

    def test_assert_is_data_value_success(self):
        """Test assert_is_data_value with valid data"""
        obj = {"data": {"@type": "xsd:string", "@value": "test"}}
        # Should not raise
        WOQLTestHelpers.assert_is_data_value(obj)

    def test_assert_is_data_value_with_type_and_value(self):
        """Test assert_is_data_value with expected type and value"""
        obj = {"data": {"@type": "xsd:string", "@value": "test"}}
        # Should not raise
        WOQLTestHelpers.assert_is_data_value(obj, "xsd:string", "test")

    def test_assert_is_data_value_failure_not_dict(self):
        """Test assert_is_data_value with non-dict"""
        with pytest.raises(AssertionError, match="Expected dict"):
            WOQLTestHelpers.assert_is_data_value("not a dict")

    def test_assert_is_data_value_failure_no_data(self):
        """Test assert_is_data_value without data key"""
        obj = {"wrong": "structure"}
        with pytest.raises(AssertionError, match="Expected 'data' key"):
            WOQLTestHelpers.assert_is_data_value(obj)

    def test_assert_is_data_value_failure_no_type(self):
        """Test assert_is_data_value without @type in data"""
        obj = {"data": {"@value": "test"}}
        with pytest.raises(AssertionError, match="Expected '@type' in data"):
            WOQLTestHelpers.assert_is_data_value(obj)

    def test_assert_is_data_value_failure_no_value(self):
        """Test assert_is_data_value without @value in data"""
        obj = {"data": {"@type": "xsd:string"}}
        with pytest.raises(AssertionError, match="Expected '@value' in data"):
            WOQLTestHelpers.assert_is_data_value(obj)

    def test_assert_is_data_value_failure_wrong_type(self):
        """Test assert_is_data_value with wrong type"""
        obj = {"data": {"@type": "xsd:integer", "@value": "test"}}
        with pytest.raises(AssertionError, match="Expected type 'xsd:string'"):
            WOQLTestHelpers.assert_is_data_value(obj, "xsd:string")

    def test_assert_is_data_value_failure_wrong_value(self):
        """Test assert_is_data_value with wrong value"""
        obj = {"data": {"@type": "xsd:string", "@value": "actual"}}
        with pytest.raises(AssertionError, match="Expected value 'expected'"):
            WOQLTestHelpers.assert_is_data_value(obj, expected_value="expected")

    def test_get_query_dict(self):
        """Test get_query_dict method"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        result = WOQLTestHelpers.get_query_dict(query)
        assert result == query._query
        assert result["@type"] == "Triple"

    def test_assert_triple_structure(self):
        """Test assert_triple_structure method"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        # Should not raise
        WOQLTestHelpers.assert_triple_structure(query)

    def test_assert_triple_structure_partial_checks(self):
        """Test assert_triple_structure with partial checks"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        # Should not raise
        WOQLTestHelpers.assert_triple_structure(
            query, check_subject=False, check_object=False
        )

    def test_assert_quad_structure(self):
        """Test assert_quad_structure method"""
        query = WOQLQuery()
        query._query = {
            "@type": "AddQuad",
            "subject": {"@type": "NodeValue", "variable": "s"},
            "predicate": {"@type": "NodeValue", "node": "rdf:type"},
            "object": {"@type": "Value", "variable": "o"},
            "graph": "graph",
        }
        # Should not raise
        WOQLTestHelpers.assert_quad_structure(query)

    def test_assert_and_structure(self):
        """Test assert_and_structure method"""
        query = WOQLQuery()
        query.woql_and()
        query.triple("v:s", "rdf:type", "v:o")
        # Should not raise
        WOQLTestHelpers.assert_and_structure(query)

    def test_assert_and_structure_with_count(self):
        """Test assert_and_structure with expected count"""
        query = WOQLQuery()
        query.woql_and()
        query.triple("v:s", "rdf:type", "v:o")
        query.triple("v:s2", "rdf:type", "v:o2")
        # Should not raise
        WOQLTestHelpers.assert_and_structure(query, expected_count=2)

    def test_assert_and_structure_failure_not_list(self):
        """Test assert_and_structure when 'and' is not a list"""
        query = WOQLQuery()
        query._query = {"@type": "And", "and": "not a list"}
        with pytest.raises(AssertionError, match="Expected 'and' to be list"):
            WOQLTestHelpers.assert_and_structure(query)

    def test_assert_and_structure_failure_wrong_count(self):
        """Test assert_and_structure with wrong count"""
        query = WOQLQuery()
        query._query = {
            "@type": "And",
            "and": [
                {
                    "@type": "Triple",
                    "subject": {"@type": "NodeValue", "variable": "s"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {"@type": "Value", "variable": "o"},
                }
            ],
        }
        # The actual count is 1, we expect 2, so it should raise
        with pytest.raises(AssertionError, match="Expected 2 items in 'and'"):
            WOQLTestHelpers.assert_and_structure(query, expected_count=2)

    def test_assert_or_structure(self):
        """Test assert_or_structure method"""
        query = WOQLQuery()
        query._query = {
            "@type": "Or",
            "or": [
                {
                    "@type": "Triple",
                    "subject": {"@type": "NodeValue", "variable": "s"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {"@type": "Value", "variable": "o"},
                }
            ],
        }
        # Should not raise
        WOQLTestHelpers.assert_or_structure(query)

    def test_assert_or_structure_with_count(self):
        """Test assert_or_structure with expected count"""
        query = WOQLQuery()
        query._query = {
            "@type": "Or",
            "or": [
                {
                    "@type": "Triple",
                    "subject": {"@type": "NodeValue", "variable": "s"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {"@type": "Value", "variable": "o"},
                },
                {
                    "@type": "Triple",
                    "subject": {"@type": "NodeValue", "variable": "s2"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {"@type": "Value", "variable": "o2"},
                },
            ],
        }
        # Should not raise
        WOQLTestHelpers.assert_or_structure(query, expected_count=2)

    def test_assert_or_structure_failure_not_list(self):
        """Test assert_or_structure when 'or' is not a list"""
        query = WOQLQuery()
        query._query = {"@type": "Or", "or": "not a list"}
        with pytest.raises(AssertionError, match="Expected 'or' to be list"):
            WOQLTestHelpers.assert_or_structure(query)

    def test_assert_or_structure_failure_wrong_count(self):
        """Test assert_or_structure with wrong count"""
        query = WOQLQuery()
        query._query = {
            "@type": "Or",
            "or": [
                {
                    "@type": "Triple",
                    "subject": {"@type": "NodeValue", "variable": "s"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {"@type": "Value", "variable": "o"},
                }
            ],
        }
        with pytest.raises(AssertionError, match="Expected 2 items in 'or'"):
            WOQLTestHelpers.assert_or_structure(query, expected_count=2)

    def test_assert_select_structure(self):
        """Test assert_select_structure method"""
        query = WOQLQuery()
        query._query = {
            "@type": "Select",
            "variables": [
                {
                    "@type": "Column",
                    "indicator": {"@type": "Indicator", "name": "v:x"},
                    "variable": "x",
                }
            ],
            "query": {
                "@type": "Triple",
                "subject": {"@type": "NodeValue", "variable": "s"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "variable": "o"},
            },
        }
        # Should not raise
        WOQLTestHelpers.assert_select_structure(query)

    def test_assert_not_structure(self):
        """Test assert_not_structure method"""
        query = WOQLQuery()
        query.woql_not()
        query.triple("v:s", "rdf:type", "v:o")
        # Should not raise
        WOQLTestHelpers.assert_not_structure(query)

    def test_assert_optional_structure(self):
        """Test assert_optional_structure method"""
        query = WOQLQuery()
        query._query = {
            "@type": "Optional",
            "query": {
                "@type": "Triple",
                "subject": {"@type": "NodeValue", "variable": "s"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "variable": "o"},
            },
        }
        # Should not raise
        WOQLTestHelpers.assert_optional_structure(query)

    def test_print_query_structure(self, capsys):
        """Test print_query_structure method"""
        query = WOQLQuery()
        query.triple("v:s", "rdf:type", "v:o")
        WOQLTestHelpers.print_query_structure(query)
        captured = capsys.readouterr()
        assert "Query type: Triple" in captured.out
        assert "subject:" in captured.out
        assert "predicate:" in captured.out
        assert "object:" in captured.out

    def test_print_query_structure_with_dict_value(self, capsys):
        """Test print_query_structure with dict value"""
        query = WOQLQuery()
        query._query = {
            "@type": "Test",
            "dict_value": {"@type": "InnerType", "other": "value"},
        }
        WOQLTestHelpers.print_query_structure(query)
        captured = capsys.readouterr()
        assert "Query type: Test" in captured.out
        assert "dict_value:" in captured.out
        assert "@type: InnerType" in captured.out

    def test_print_query_structure_with_list_value(self, capsys):
        """Test print_query_structure with list value"""
        query = WOQLQuery()
        query._query = {"@type": "Test", "list_value": ["item1", "item2", "item3"]}
        WOQLTestHelpers.print_query_structure(query)
        captured = capsys.readouterr()
        assert "Query type: Test" in captured.out
        assert "list_value: [3 items]" in captured.out

    def test_print_query_structure_with_simple_value(self, capsys):
        """Test print_query_structure with simple value"""
        query = WOQLQuery()
        query._query = {"@type": "Test", "simple": "value"}
        WOQLTestHelpers.print_query_structure(query)
        captured = capsys.readouterr()
        assert "Query type: Test" in captured.out
        assert "simple: value" in captured.out

    def test_print_query_structure_with_indent(self, capsys):
        """Test print_query_structure with indentation"""
        query = WOQLQuery()
        query._query = {"@type": "Test"}
        WOQLTestHelpers.print_query_structure(query, indent=4)
        captured = capsys.readouterr()
        assert " Query type: Test" in captured.out
