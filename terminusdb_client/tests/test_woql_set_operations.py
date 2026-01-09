"""Tests for WOQL set and list operations."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestWOQLConcatOperations:
    """Test concat operation edge cases."""
    
    def test_concat_args_introspection(self):
        """Test concat returns args list when called with 'args'."""
        result = WOQLQuery().concat("args", "v:Result")
        
        assert result == ["list", "concatenated"]
    
    def test_concat_with_string_containing_variables(self):
        """Test concat with string containing v: variables."""
        query = WOQLQuery()
        # This tests lines 2610-2622 - string parsing with v: variables
        result = query.concat("Hello v:Name, welcome!", "v:Result")
        
        assert result is query
        assert query._cursor["@type"] == "Concatenate"
    
    def test_concat_with_string_multiple_variables(self):
        """Test concat with string containing multiple v: variables."""
        query = WOQLQuery()
        # Tests complex string parsing with multiple variables
        result = query.concat("v:First v:Second v:Third", "v:Result")
        
        assert result is query
        assert query._cursor["@type"] == "Concatenate"
    
    def test_concat_with_string_variable_at_start(self):
        """Test concat with v: variable at the start of string."""
        query = WOQLQuery()
        # Tests line 2612-2613 - handling when first element exists
        result = query.concat("v:Name is here", "v:Result")
        
        assert result is query
        assert query._cursor["@type"] == "Concatenate"
    
    def test_concat_with_string_variable_with_special_chars(self):
        """Test concat with v: variable followed by special characters."""
        query = WOQLQuery()
        # Tests lines 2616-2621 - handling special characters after variables
        result = query.concat("Hello v:Name!", "v:Result")
        
        assert result is query
        assert query._cursor["@type"] == "Concatenate"
    
    def test_concat_with_list(self):
        """Test concat with list input."""
        query = WOQLQuery()
        # Tests line 2623 - list handling
        result = query.concat(["Hello", "v:Name"], "v:Result")
        
        assert result is query
        assert query._cursor["@type"] == "Concatenate"


class TestWOQLJoinOperations:
    """Test join operation edge cases."""
    
    def test_join_args_introspection(self):
        """Test join returns args list when called with 'args'."""
        result = WOQLQuery().join("args", ",", "v:Result")
        
        assert result == ["list", "separator", "join"]
    
    def test_join_with_list_and_separator(self):
        """Test join with list and separator."""
        query = WOQLQuery()
        # Tests lines 2651-2657 - join operation
        result = query.join(["v:Item1", "v:Item2"], ", ", "v:Result")
        
        assert result is query
        assert query._cursor["@type"] == "Join"
        assert "list" in query._cursor
        assert "separator" in query._cursor
        assert "result" in query._cursor


class TestWOQLSumOperations:
    """Test sum operation edge cases."""
    
    def test_sum_args_introspection(self):
        """Test sum returns args list when called with 'args'."""
        result = WOQLQuery().sum("args", "v:Total")
        
        assert result == ["list", "sum"]
    
    def test_sum_with_list_of_numbers(self):
        """Test sum with list of numbers."""
        query = WOQLQuery()
        # Tests lines 2678-2683 - sum operation
        result = query.sum(["v:Num1", "v:Num2", "v:Num3"], "v:Total")
        
        assert result is query
        assert query._cursor["@type"] == "Sum"
        assert "list" in query._cursor
        assert "sum" in query._cursor


class TestWOQLSliceOperations:
    """Test slice operation edge cases."""
    
    def test_slice_args_introspection(self):
        """Test slice returns args list when called with 'args'."""
        result = WOQLQuery().slice("args", "v:Result", 0, 5)
        
        assert result == ["list", "result", "start", "end"]
    
    def test_slice_with_start_and_end(self):
        """Test slice with start and end indices."""
        query = WOQLQuery()
        # Tests lines 2712-2713 and slice operation
        result = query.slice(["a", "b", "c", "d"], "v:Result", 1, 3)
        
        assert result is query
        assert query._cursor["@type"] == "Slice"
        assert "list" in query._cursor
        assert "result" in query._cursor
        assert "start" in query._cursor
        assert "end" in query._cursor
    
    def test_slice_with_only_start(self):
        """Test slice with only start index (no end)."""
        query = WOQLQuery()
        # Tests slice without end parameter
        result = query.slice(["a", "b", "c", "d"], "v:Result", 2)
        
        assert result is query
        assert query._cursor["@type"] == "Slice"
        assert "start" in query._cursor
    
    def test_slice_with_negative_index(self):
        """Test slice with negative start index."""
        query = WOQLQuery()
        # Tests negative indexing
        result = query.slice(["a", "b", "c", "d"], "v:Result", -2)
        
        assert result is query
        assert query._cursor["@type"] == "Slice"
    
    def test_slice_with_variable_indices(self):
        """Test slice with variable indices instead of integers."""
        query = WOQLQuery()
        # Tests line 2722 - non-integer start handling
        result = query.slice(["a", "b", "c"], "v:Result", "v:Start", "v:End")
        
        assert result is query
        assert query._cursor["@type"] == "Slice"


class TestWOQLMemberOperations:
    """Test member operation edge cases."""
    
    def test_member_with_list(self):
        """Test member operation with list."""
        query = WOQLQuery()
        result = query.member("v:Item", ["a", "b", "c"])
        
        assert result is query
        assert query._cursor["@type"] == "Member"
    
    def test_member_with_variable_list(self):
        """Test member operation with variable list."""
        query = WOQLQuery()
        result = query.member("v:Item", "v:List")
        
        assert result is query
        assert query._cursor["@type"] == "Member"


class TestWOQLSetDifferenceOperations:
    """Test set_difference operation."""
    
    def test_set_difference_basic(self):
        """Test set_difference with two lists."""
        query = WOQLQuery()
        result = query.set_difference(
            ["a", "b", "c"],
            ["b", "c", "d"],
            "v:Result"
        )
        
        assert result is query
        assert query._cursor["@type"] == "SetDifference"
        assert "list_a" in query._cursor
        assert "list_b" in query._cursor
        assert "result" in query._cursor


class TestWOQLSetIntersectionOperations:
    """Test set_intersection operation."""
    
    def test_set_intersection_basic(self):
        """Test set_intersection with two lists."""
        query = WOQLQuery()
        result = query.set_intersection(
            ["a", "b", "c"],
            ["b", "c", "d"],
            "v:Result"
        )
        
        assert result is query
        assert query._cursor["@type"] == "SetIntersection"
        assert "list_a" in query._cursor
        assert "list_b" in query._cursor
        assert "result" in query._cursor


class TestWOQLSetUnionOperations:
    """Test set_union operation."""
    
    def test_set_union_basic(self):
        """Test set_union with two lists."""
        query = WOQLQuery()
        result = query.set_union(
            ["a", "b", "c"],
            ["b", "c", "d"],
            "v:Result"
        )
        
        assert result is query
        assert query._cursor["@type"] == "SetUnion"
        assert "list_a" in query._cursor
        assert "list_b" in query._cursor
        assert "result" in query._cursor


class TestWOQLSetMemberOperations:
    """Test set_member operation."""
    
    def test_set_member_basic(self):
        """Test set_member operation."""
        query = WOQLQuery()
        result = query.set_member("v:Element", ["a", "b", "c"])
        
        assert result is query
        assert query._cursor["@type"] == "SetMember"
        assert "element" in query._cursor
        assert "set" in query._cursor


class TestWOQLListToSetOperations:
    """Test list_to_set operation."""
    
    def test_list_to_set_basic(self):
        """Test list_to_set operation."""
        query = WOQLQuery()
        result = query.list_to_set(["a", "b", "b", "c"], "v:UniqueSet")
        
        assert result is query
        assert query._cursor["@type"] == "ListToSet"
        assert "list" in query._cursor
        assert "set" in query._cursor
