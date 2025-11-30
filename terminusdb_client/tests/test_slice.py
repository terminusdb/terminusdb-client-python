"""
Unit tests for WOQL slice operator

Tests the Python client binding for slice(input_list, result, start, end=None)
"""

import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery

from .woqljson.woqlSliceJson import WOQL_SLICE_JSON


class TestWOQLSlice:
    """Test cases for the slice operator"""

    def test_basic_slice(self):
        """AC-1: Basic slicing - slice([a,b,c,d], result, 1, 3) returns [b,c]"""
        woql_object = WOQLQuery().slice(["a", "b", "c", "d"], "v:Result", 1, 3)
        assert woql_object.to_dict() == WOQL_SLICE_JSON["basicSlice"]

    def test_negative_indices(self):
        """AC-3: Negative indices - slice([a,b,c,d], result, -2, -1) returns [c]"""
        woql_object = WOQLQuery().slice(["a", "b", "c", "d"], "v:Result", -2, -1)
        assert woql_object.to_dict() == WOQL_SLICE_JSON["negativeIndices"]

    def test_without_end(self):
        """Optional end - slice([a,b,c,d], result, 1) returns [b,c,d]"""
        woql_object = WOQLQuery().slice(["a", "b", "c", "d"], "v:Result", 1)
        assert woql_object.to_dict() == WOQL_SLICE_JSON["withoutEnd"]

    def test_variable_list(self):
        """Variable list input - slice(v:MyList, result, 0, 2)"""
        woql_object = WOQLQuery().slice("v:MyList", "v:Result", 0, 2)
        assert woql_object.to_dict() == WOQL_SLICE_JSON["variableList"]

    def test_variable_indices(self):
        """Variable indices - slice([x,y,z], result, v:Start, v:End)"""
        woql_object = WOQLQuery().slice(["x", "y", "z"], "v:Result", "v:Start", "v:End")
        assert woql_object.to_dict() == WOQL_SLICE_JSON["variableIndices"]

    def test_empty_list(self):
        """AC-6: Empty list - slice([], result, 0, 1) returns []"""
        woql_object = WOQLQuery().slice([], "v:Result", 0, 1)
        assert woql_object.to_dict() == WOQL_SLICE_JSON["emptyList"]

    def test_slice_type(self):
        """Verify the @type is correctly set to 'Slice'"""
        woql_object = WOQLQuery().slice(["a", "b"], "v:Result", 0, 1)
        assert woql_object.to_dict()["@type"] == "Slice"

    def test_chaining_with_and(self):
        """Test that slice works with method chaining via woql_and"""
        woql_object = WOQLQuery().woql_and(
            WOQLQuery().eq("v:MyList", ["a", "b", "c"]),
            WOQLQuery().slice("v:MyList", "v:Result", 1, 3),
        )
        result = woql_object.to_dict()
        assert result["@type"] == "And"
        assert len(result["and"]) == 2
        assert result["and"][1]["@type"] == "Slice"

    def test_single_element_slice(self):
        """AC-2: Single element - slice([a,b,c,d], result, 1, 2) returns [b]"""
        woql_object = WOQLQuery().slice(["a", "b", "c", "d"], "v:Result", 1, 2)
        result = woql_object.to_dict()
        assert result["@type"] == "Slice"
        assert result["start"]["data"]["@value"] == 1
        assert result["end"]["data"]["@value"] == 2

    def test_full_range(self):
        """AC-7: Full range - slice([a,b,c,d], result, 0, 4) returns [a,b,c,d]"""
        woql_object = WOQLQuery().slice(["a", "b", "c", "d"], "v:Result", 0, 4)
        result = woql_object.to_dict()
        assert result["@type"] == "Slice"
        assert result["start"]["data"]["@value"] == 0
        assert result["end"]["data"]["@value"] == 4
