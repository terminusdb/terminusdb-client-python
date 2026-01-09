"""
Unit tests for WOQL RDFList library operations - verifying JSON structure.
These tests do NOT connect to a database - they only verify the generated WOQL JSON.

These tests align with the JavaScript client's RDFList implementation.
"""

import pytest
from terminusdb_client.woqlquery import (
    WOQLQuery,
    WOQLLibrary,
    _reset_unique_var_counter,
)


class TestWOQLLibraryRDFList:
    """Test suite for WOQLLibrary RDFList operations."""

    def setup_method(self):
        """Reset unique var counter before each test for predictable names."""
        _reset_unique_var_counter(0)

    def test_lib_method_returns_library(self):
        """WOQLQuery().lib() should return a WOQLLibrary instance."""
        lib = WOQLQuery().lib()
        assert isinstance(lib, WOQLLibrary)

    def test_rdflist_peek_structure(self):
        """rdflist_peek should generate correct query structure."""
        query = WOQLQuery().lib().rdflist_peek("v:list_head", "v:first_value")
        result = query.to_dict()

        # Should be an And with eq bindings and Select
        assert result["@type"] == "And"

        # Should contain a Select to scope local variables
        has_select = any(
            item.get("@type") == "Select" for item in result.get("and", [])
        )
        assert has_select

    def test_rdflist_length_structure(self):
        """rdflist_length should generate correct query structure."""
        query = WOQLQuery().lib().rdflist_length("v:list_head", "v:count")
        result = query.to_dict()

        assert result["@type"] == "And"

    def test_rdflist_member_structure(self):
        """rdflist_member should generate correct query structure."""
        query = WOQLQuery().lib().rdflist_member("v:list_head", "v:value")
        result = query.to_dict()

        assert result["@type"] == "And"

    def test_rdflist_list_structure(self):
        """rdflist_list should generate group_by query structure."""
        query = WOQLQuery().lib().rdflist_list("v:list_head", "v:all_values")
        result = query.to_dict()

        # Should contain a group_by somewhere in the structure
        def contains_group_by(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "GroupBy":
                    return True
                for v in obj.values():
                    if contains_group_by(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_group_by(item):
                        return True
            return False

        assert contains_group_by(result)

    def test_rdflist_last_structure(self):
        """rdflist_last should generate path query to find last element."""
        query = WOQLQuery().lib().rdflist_last("v:list_head", "v:last_value")
        result = query.to_dict()

        # Should contain a Path query
        def contains_path(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "Path":
                    return True
                for v in obj.values():
                    if contains_path(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_path(item):
                        return True
            return False

        assert contains_path(result)

    def test_rdflist_nth0_static_index(self):
        """rdflist_nth0 with static index should work."""
        query = WOQLQuery().lib().rdflist_nth0("v:list_head", 2, "v:value")
        result = query.to_dict()

        # Should be valid query structure
        assert result["@type"] == "And"

    def test_rdflist_nth0_index_zero(self):
        """rdflist_nth0 with index 0 should use peek logic."""
        query = WOQLQuery().lib().rdflist_nth0("v:list_head", 0, "v:value")
        result = query.to_dict()

        assert result["@type"] == "And"

    def test_rdflist_nth0_negative_index_raises(self):
        """rdflist_nth0 with negative index should raise ValueError."""
        with pytest.raises(ValueError, match="index >= 0"):
            WOQLQuery().lib().rdflist_nth0("v:list", -1, "v:val")

    def test_rdflist_nth1_static_index(self):
        """rdflist_nth1 with static index should work."""
        query = WOQLQuery().lib().rdflist_nth1("v:list_head", 1, "v:value")
        result = query.to_dict()

        assert result["@type"] == "And"

    def test_rdflist_nth1_zero_index_raises(self):
        """rdflist_nth1 with index < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="index >= 1"):
            WOQLQuery().lib().rdflist_nth1("v:list", 0, "v:val")

    def test_rdflist_pop_structure(self):
        """rdflist_pop should generate delete and add triple operations."""
        query = WOQLQuery().lib().rdflist_pop("v:list_head", "v:popped")
        result = query.to_dict()

        # Should contain DeleteTriple and AddTriple
        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "DeleteTriple")
        assert contains_type(result, "AddTriple")

    def test_rdflist_push_structure(self):
        """rdflist_push should generate delete and add triple operations."""
        query = WOQLQuery().lib().rdflist_push("v:list_head", "v:new_value")
        result = query.to_dict()

        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "DeleteTriple")
        assert contains_type(result, "AddTriple")
        assert contains_type(result, "RandomKey")  # Python client uses RandomKey

    def test_rdflist_append_structure(self):
        """rdflist_append should generate append query structure."""
        query = WOQLQuery().lib().rdflist_append("v:list_head", "v:new_value")
        result = query.to_dict()

        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "Path")
        assert contains_type(result, "AddTriple")

    def test_rdflist_clear_structure(self):
        """rdflist_clear should generate delete operations."""
        query = WOQLQuery().lib().rdflist_clear("v:list_head", "v:empty_list")
        result = query.to_dict()

        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "DeleteTriple")
        assert contains_type(result, "Equals")

    def test_rdflist_empty_structure(self):
        """rdflist_empty should return eq with rdf:nil."""
        query = WOQLQuery().lib().rdflist_empty("v:empty")
        result = query.to_dict()

        assert result["@type"] == "Equals"

    def test_rdflist_is_empty_structure(self):
        """rdflist_is_empty should return eq check for rdf:nil."""
        query = WOQLQuery().lib().rdflist_is_empty("v:list")
        result = query.to_dict()

        assert result["@type"] == "Equals"

    def test_rdflist_slice_structure(self):
        """rdflist_slice should generate group_by with path pattern."""
        query = WOQLQuery().lib().rdflist_slice("v:list_head", 0, 3, "v:result")
        result = query.to_dict()

        def contains_group_by(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "GroupBy":
                    return True
                for v in obj.values():
                    if contains_group_by(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_group_by(item):
                        return True
            return False

        assert contains_group_by(result)

    def test_rdflist_slice_empty_range(self):
        """rdflist_slice with start >= end should return empty list eq."""
        query = WOQLQuery().lib().rdflist_slice("v:list", 5, 3, "v:result")
        result = query.to_dict()

        # Should contain Equals for empty list
        def contains_equals(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "Equals":
                    return True
                for v in obj.values():
                    if contains_equals(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_equals(item):
                        return True
            return False

        assert contains_equals(result)

    def test_rdflist_slice_negative_indices_raises(self):
        """rdflist_slice with negative indices should raise ValueError."""
        with pytest.raises(ValueError, match="negative indices"):
            WOQLQuery().lib().rdflist_slice("v:list", -1, 3, "v:result")

    def test_rdflist_insert_at_zero(self):
        """rdflist_insert at position 0 should work."""
        query = WOQLQuery().lib().rdflist_insert("v:list_head", 0, "v:value")
        result = query.to_dict()

        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "AddTriple")
        assert contains_type(result, "DeleteTriple")

    def test_rdflist_insert_at_position(self):
        """rdflist_insert at position > 0 should work."""
        query = WOQLQuery().lib().rdflist_insert("v:list_head", 2, "v:value")
        result = query.to_dict()

        def contains_path(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "Path":
                    return True
                for v in obj.values():
                    if contains_path(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_path(item):
                        return True
            return False

        assert contains_path(result)

    def test_rdflist_insert_negative_position_raises(self):
        """rdflist_insert with negative position should raise ValueError."""
        with pytest.raises(ValueError, match="position >= 0"):
            WOQLQuery().lib().rdflist_insert("v:list", -1, "v:val")

    def test_rdflist_drop_at_zero(self):
        """rdflist_drop at position 0 should work."""
        query = WOQLQuery().lib().rdflist_drop("v:list_head", 0)
        result = query.to_dict()

        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "DeleteTriple")
        assert contains_type(result, "AddTriple")

    def test_rdflist_drop_negative_position_raises(self):
        """rdflist_drop with negative position should raise ValueError."""
        with pytest.raises(ValueError, match="position >= 0"):
            WOQLQuery().lib().rdflist_drop("v:list", -1)

    def test_rdflist_swap_structure(self):
        """rdflist_swap should generate swap operations."""
        query = WOQLQuery().lib().rdflist_swap("v:list_head", 0, 2)
        result = query.to_dict()

        def contains_type(obj, type_name):
            if isinstance(obj, dict):
                if obj.get("@type") == type_name:
                    return True
                for v in obj.values():
                    if contains_type(v, type_name):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_type(item, type_name):
                        return True
            return False

        assert contains_type(result, "DeleteTriple")
        assert contains_type(result, "AddTriple")

    def test_rdflist_swap_same_position(self):
        """rdflist_swap with same positions should be a no-op (just type check)."""
        query = WOQLQuery().lib().rdflist_swap("v:list_head", 1, 1)
        result = query.to_dict()

        # Should contain a Triple check for rdf:type
        def contains_triple(obj):
            if isinstance(obj, dict):
                if obj.get("@type") == "Triple":
                    return True
                for v in obj.values():
                    if contains_triple(v):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if contains_triple(item):
                        return True
            return False

        assert contains_triple(result)

    def test_rdflist_swap_negative_position_raises(self):
        """rdflist_swap with negative position should raise ValueError."""
        with pytest.raises(ValueError, match="positions >= 0"):
            WOQLQuery().lib().rdflist_swap("v:list", -1, 2)


class TestRDFListVariableScoping:
    """Test that RDFList operations properly scope variables."""

    def setup_method(self):
        """Reset unique var counter before each test."""
        _reset_unique_var_counter(0)

    def test_rdflist_operations_use_unique_variables(self):
        """Multiple rdflist calls should use different internal variables."""
        _reset_unique_var_counter(0)

        query1 = WOQLQuery().lib().rdflist_peek("v:list1", "v:val1")

        _reset_unique_var_counter(100)  # Different starting point
        query2 = WOQLQuery().lib().rdflist_peek("v:list2", "v:val2")

        result1 = query1.to_dict()
        result2 = query2.to_dict()

        # Both should have valid structure
        assert result1["@type"] == "And"
        assert result2["@type"] == "And"

        # Internal variable names should be different (due to counter difference)
        result1_str = str(result1)
        result2_str = str(result2)

        # The unique counter values should differ
        assert "_1" in result1_str or "_2" in result1_str
        assert "_101" in result2_str or "_102" in result2_str

    def test_combined_rdflist_operations(self):
        """Multiple rdflist operations can be combined in a query."""
        _reset_unique_var_counter(0)

        query = WOQLQuery().woql_and(
            WOQLQuery().lib().rdflist_peek("v:list", "v:first"),
            WOQLQuery().lib().rdflist_length("v:list", "v:len"),
        )

        result = query.to_dict()
        assert result["@type"] == "And"

        # Should have multiple sub-queries
        assert len(result.get("and", [])) >= 2
