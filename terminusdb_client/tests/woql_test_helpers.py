"""Helper utilities for testing WOQL query generation.

This module provides standardized mocks and assertion helpers to verify
that WOQLQuery methods generate correct JSON-LD structures.
"""

from unittest.mock import Mock


class WOQLTestHelpers:
    """Helper class for systematic WOQL testing."""

    @staticmethod
    def create_mock_client():
        """Create a mock client for testing execute() method."""
        client = Mock()
        client.query = Mock(return_value={"@type": "api:WoqlResponse"})
        return client

    @staticmethod
    def assert_query_type(query, expected_type):
        """Assert that query has the expected @type."""
        assert (
            query._query.get("@type") == expected_type
        ), f"Expected @type={expected_type}, got {query._query.get('@type')}"

    @staticmethod
    def assert_has_key(query, key):
        """Assert that query has a specific key."""
        assert (
            key in query._query
        ), f"Expected key '{key}' in query, got keys: {list(query._query.keys())}"

    @staticmethod
    def assert_key_value(query, key, expected_value):
        """Assert that query has a key with expected value."""
        actual = query._query.get(key)
        assert (
            actual == expected_value
        ), f"Expected {key}={expected_value}, got {actual}"

    @staticmethod
    def assert_is_variable(obj, expected_name=None):
        """Assert that an object is a variable structure."""
        assert isinstance(obj, dict), f"Expected dict, got {type(obj)}"
        assert obj.get("@type") in [
            "Value",
            "NodeValue",
            "DataValue",
            "ArithmeticValue",
        ], f"Expected variable type, got {obj.get('@type')}"
        assert "variable" in obj, f"Expected 'variable' key in {obj}"
        if expected_name:
            assert (
                obj["variable"] == expected_name
            ), f"Expected variable name '{expected_name}', got '{obj['variable']}'"

    @staticmethod
    def assert_is_node(obj, expected_node=None):
        """Assert that an object is a node structure."""
        assert isinstance(obj, dict), f"Expected dict, got {type(obj)}"
        assert "node" in obj or obj.get("@type") in [
            "Value",
            "NodeValue",
        ], f"Expected node structure, got {obj}"
        if expected_node and "node" in obj:
            assert (
                obj["node"] == expected_node
            ), f"Expected node '{expected_node}', got '{obj['node']}'"

    @staticmethod
    def assert_is_data_value(obj, expected_type=None, expected_value=None):
        """Assert that an object is a typed data value."""
        assert isinstance(obj, dict), f"Expected dict, got {type(obj)}"
        assert "data" in obj, f"Expected 'data' key in {obj}"
        data = obj["data"]
        assert "@type" in data, f"Expected '@type' in data: {data}"
        assert "@value" in data, f"Expected '@value' in data: {data}"
        if expected_type:
            assert (
                data["@type"] == expected_type
            ), f"Expected type '{expected_type}', got '{data['@type']}'"
        if expected_value is not None:
            assert (
                data["@value"] == expected_value
            ), f"Expected value '{expected_value}', got '{data['@value']}'"

    @staticmethod
    def get_query_dict(query):
        """Get the internal query dictionary."""
        return query._query

    @staticmethod
    def assert_triple_structure(
        query, check_subject=True, check_predicate=True, check_object=True
    ):
        """Assert that query has proper triple structure."""
        WOQLTestHelpers.assert_query_type(query, "Triple")
        if check_subject:
            WOQLTestHelpers.assert_has_key(query, "subject")
        if check_predicate:
            WOQLTestHelpers.assert_has_key(query, "predicate")
        if check_object:
            WOQLTestHelpers.assert_has_key(query, "object")

    @staticmethod
    def assert_quad_structure(query):
        """Assert that query has proper quad structure."""
        WOQLTestHelpers.assert_query_type(query, "AddQuad")
        WOQLTestHelpers.assert_has_key(query, "subject")
        WOQLTestHelpers.assert_has_key(query, "predicate")
        WOQLTestHelpers.assert_has_key(query, "object")
        WOQLTestHelpers.assert_has_key(query, "graph")

    @staticmethod
    def assert_and_structure(query, expected_count=None):
        """Assert that query has proper And structure."""
        WOQLTestHelpers.assert_query_type(query, "And")
        WOQLTestHelpers.assert_has_key(query, "and")
        and_list = query._query["and"]
        assert isinstance(
            and_list, list
        ), f"Expected 'and' to be list, got {type(and_list)}"
        if expected_count is not None:
            assert (
                len(and_list) == expected_count
            ), f"Expected {expected_count} items in 'and', got {len(and_list)}"

    @staticmethod
    def assert_or_structure(query, expected_count=None):
        """Assert that query has proper Or structure."""
        WOQLTestHelpers.assert_query_type(query, "Or")
        WOQLTestHelpers.assert_has_key(query, "or")
        or_list = query._query["or"]
        assert isinstance(
            or_list, list
        ), f"Expected 'or' to be list, got {type(or_list)}"
        if expected_count is not None:
            assert (
                len(or_list) == expected_count
            ), f"Expected {expected_count} items in 'or', got {len(or_list)}"

    @staticmethod
    def assert_select_structure(query):
        """Assert that query has proper Select structure."""
        WOQLTestHelpers.assert_query_type(query, "Select")
        WOQLTestHelpers.assert_has_key(query, "variables")
        WOQLTestHelpers.assert_has_key(query, "query")

    @staticmethod
    def assert_not_structure(query):
        """Assert that query has proper Not structure."""
        WOQLTestHelpers.assert_query_type(query, "Not")
        WOQLTestHelpers.assert_has_key(query, "query")

    @staticmethod
    def assert_optional_structure(query):
        """Assert that query has proper Optional structure."""
        WOQLTestHelpers.assert_query_type(query, "Optional")
        WOQLTestHelpers.assert_has_key(query, "query")

    @staticmethod
    def print_query_structure(query, indent=0):
        """Print query structure for debugging (helper method)."""
        q = query._query
        print(" " * indent + f"Query type: {q.get('@type', 'Unknown')}")
        for key, value in q.items():
            if key != "@type":
                if isinstance(value, dict):
                    print(" " * indent + f"{key}:")
                    if "@type" in value:
                        print(" " * (indent + 2) + f"@type: {value['@type']}")
                elif isinstance(value, list):
                    print(" " * indent + f"{key}: [{len(value)} items]")
                else:
                    print(" " * indent + f"{key}: {value}")


# Convenience function for quick access
def helpers():
    """Quick access to WOQLTestHelpers."""
    return WOQLTestHelpers
