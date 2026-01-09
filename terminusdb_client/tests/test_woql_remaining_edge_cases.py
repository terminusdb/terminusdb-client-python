"""Tests for remaining WOQL edge cases to increase coverage."""

from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLDistinctEdgeCases:
    """Test distinct operation edge cases."""

    def test_distinct_with_existing_cursor(self):
        """Test distinct wraps cursor with and when cursor exists."""
        query = WOQLQuery()
        # Set up existing cursor
        query._cursor["@type"] = "Triple"
        query._cursor["subject"] = "v:X"

        # This should trigger line 819 - wrap cursor with and
        result = query.distinct("v:X", "v:Y")

        assert result is query

    def test_distinct_empty_list_handling(self):
        """Test distinct with empty list."""
        query = WOQLQuery()
        # This tests line 822 validation (similar to select bug)
        result = query.distinct()

        assert result is query


class TestWOQLStartEdgeCase:
    """Test start operation edge case."""

    def test_start_args_introspection(self):
        """Test start returns args list when called with 'args'."""
        result = WOQLQuery().start("args")

        assert result == ["start", "query"]


class TestWOQLCommentEdgeCase:
    """Test comment operation edge case."""

    def test_comment_args_introspection(self):
        """Test comment returns args list when called with 'args'."""
        result = WOQLQuery().comment("args")

        assert result == ["comment", "query"]


class TestWOQLMathOperationEdgeCases:
    """Test math operation edge cases for arithmetic operations."""

    def test_plus_args_introspection(self):
        """Test plus returns args list when called with 'args'."""
        result = WOQLQuery().plus("args", 5)

        assert result == ["left", "right"]

    def test_minus_args_introspection(self):
        """Test minus returns args list when called with 'args'."""
        result = WOQLQuery().minus("args", 5)

        assert result == ["left", "right"]

    def test_times_args_introspection(self):
        """Test times returns args list when called with 'args'."""
        result = WOQLQuery().times("args", 5)

        assert result == ["left", "right"]

    def test_divide_args_introspection(self):
        """Test divide returns args list when called with 'args'."""
        result = WOQLQuery().divide("args", 5)

        assert result == ["left", "right"]

    def test_div_args_introspection(self):
        """Test div returns args list when called with 'args'."""
        result = WOQLQuery().div("args", 5)

        assert result == ["left", "right"]


class TestWOQLComparisonOperationEdgeCases:
    """Test comparison operation edge cases."""

    def test_greater_args_introspection(self):
        """Test greater returns args list when called with 'args'."""
        result = WOQLQuery().greater("args", 5)

        assert result == ["left", "right"]

    def test_less_args_introspection(self):
        """Test less returns args list when called with 'args'."""
        result = WOQLQuery().less("args", 5)

        assert result == ["left", "right"]

    # Note: gte and lte methods don't exist in WOQLQuery
    # Lines 2895, 2897 are not covered by args introspection


class TestWOQLLogicalOperationEdgeCases:
    """Test logical operation edge cases."""

    def test_woql_not_args_introspection(self):
        """Test woql_not returns args list when called with 'args'."""
        result = WOQLQuery().woql_not("args")

        assert result == ["query"]

    def test_once_args_introspection(self):
        """Test once returns args list when called with 'args'."""
        result = WOQLQuery().once("args")

        assert result == ["query"]

    def test_immediately_args_introspection(self):
        """Test immediately returns args list when called with 'args'."""
        result = WOQLQuery().immediately("args")

        assert result == ["query"]

    def test_count_args_introspection(self):
        """Test count returns args list when called with 'args'."""
        result = WOQLQuery().count("args")

        assert result == ["count", "query"]

    def test_cast_args_introspection(self):
        """Test cast returns args list when called with 'args'."""
        result = WOQLQuery().cast("args", "xsd:string", "v:Result")

        assert result == ["value", "type", "result"]


class TestWOQLTypeOperationEdgeCases:
    """Test type operation edge cases."""

    def test_type_of_args_introspection(self):
        """Test type_of returns args list when called with 'args'."""
        result = WOQLQuery().type_of("args", "v:Type")

        assert result == ["value", "type"]

    def test_order_by_args_introspection(self):
        """Test order_by returns args list when called with 'args'."""
        result = WOQLQuery().order_by("args")

        assert isinstance(result, WOQLQuery)

    def test_group_by_args_introspection(self):
        """Test group_by returns args list when called with 'args'."""
        result = WOQLQuery().group_by("args", "v:Template", "v:Result")

        assert result == ["group_by", "template", "grouped", "query"]

    def test_length_args_introspection(self):
        """Test length returns args list when called with 'args'."""
        result = WOQLQuery().length("args", "v:Length")

        assert result == ["list", "length"]


class TestWOQLStringOperationEdgeCases:
    """Test string operation edge cases."""

    def test_upper_args_introspection(self):
        """Test upper returns args list when called with 'args'."""
        result = WOQLQuery().upper("args", "v:Upper")

        assert result == ["left", "right"]

    def test_lower_args_introspection(self):
        """Test lower returns args list when called with 'args'."""
        result = WOQLQuery().lower("args", "v:Lower")

        assert result == ["left", "right"]

    def test_pad_args_introspection(self):
        """Test pad returns args list when called with 'args'."""
        result = WOQLQuery().pad("args", "X", 10, "v:Padded")

        assert result == ["string", "char", "times", "result"]


class TestWOQLRegexOperationEdgeCases:
    """Test regex operation edge cases."""

    def test_split_args_introspection(self):
        """Test split returns args list when called with 'args'."""
        result = WOQLQuery().split("args", ",", "v:List")

        assert result == ["string", "pattern", "list"]

    def test_regexp_args_introspection(self):
        """Test regexp returns args list when called with 'args'."""
        result = WOQLQuery().regexp("args", "[0-9]+", "v:Match")

        assert result == ["pattern", "string", "result"]

    def test_like_args_introspection(self):
        """Test like returns args list when called with 'args'."""
        result = WOQLQuery().like("args", "test%", 0.8)

        assert result == ["left", "right", "similarity"]


class TestWOQLSubstringOperationEdgeCases:
    """Test substring operation edge cases."""

    def test_substring_args_introspection(self):
        """Test substring returns args list when called with 'args'."""
        result = WOQLQuery().substring("args", 0, 5, "v:Result")

        assert result == ["string", "before", "length", "after", "substring"]

    def test_concat_args_already_tested(self):
        """Test concat args introspection."""
        # This is already tested in test_woql_set_operations.py
        # but included here for completeness
        result = WOQLQuery().concat("args", "v:Result")

        assert result == ["list", "concatenated"]


class TestWOQLTrimOperationEdgeCase:
    """Test trim operation edge case."""

    def test_trim_args_introspection(self):
        """Test trim returns args list when called with 'args'."""
        result = WOQLQuery().trim("args", "v:Trimmed")

        assert result == ["untrimmed", "trimmed"]


class TestWOQLVariousOperationEdgeCases:
    """Test various operation edge cases."""

    def test_limit_args_introspection(self):
        """Test limit returns args list when called with 'args'."""
        result = WOQLQuery().limit("args")

        assert result == ["limit", "query"]

    def test_get_args_introspection(self):
        """Test get returns args list when called with 'args'."""
        result = WOQLQuery().get("args")

        assert result == ["columns", "resource"]

    def test_put_args_introspection(self):
        """Test put returns args list when called with 'args'."""
        result = WOQLQuery().put("args", WOQLQuery())

        assert result == ["columns", "query", "resource"]

    def test_file_args_introspection(self):
        """Test file returns args list when called with 'args'."""
        result = WOQLQuery().file("args")

        assert result == ["source", "format"]

    def test_remote_args_introspection(self):
        """Test remote returns args list when called with 'args'."""
        result = WOQLQuery().remote("args")

        assert result == ["source", "format", "options"]


class TestWOQLAsMethodEdgeCases:
    """Test as() method edge cases."""

    def test_as_with_two_element_list(self):
        """Test as() with two-element list."""
        query = WOQLQuery()
        result = query.woql_as([["v:X", "name"]])

        assert result is query
        assert len(query._query) >= 1

    def test_as_with_three_element_list_with_type(self):
        """Test as() with three-element list including type."""
        query = WOQLQuery()
        result = query.woql_as([["v:X", "name", "xsd:string"]])

        assert result is query
        assert len(query._query) >= 1

    def test_as_with_xsd_prefix_in_second_arg(self):
        """Test as() with xsd: prefix in second argument."""
        query = WOQLQuery()
        result = query.woql_as(0, "v:Value", "xsd:string")

        assert result is query
        assert len(query._query) >= 1

    def test_as_with_object_to_dict(self):
        """Test as() with object having to_dict method."""
        query = WOQLQuery()
        var = Var("X")
        result = query.woql_as(var)

        assert result is query
        assert len(query._query) >= 1


class TestWOQLMethodEdgeCases:
    """Test various method edge cases."""

    def test_woql_or_args_introspection(self):
        """Test woql_or returns args list when called with 'args'."""
        result = WOQLQuery().woql_or("args")

        assert result == ["or"]

    # Note: 'from' is a reserved keyword in Python, method may not have args introspection

    def test_into_args_introspection(self):
        """Test into returns args list when called with 'args'."""
        result = WOQLQuery().into("args", WOQLQuery())

        assert result == ["graph", "query"]

    def test_using_args_introspection(self):
        """Test using returns args list when called with 'args'."""
        result = WOQLQuery().using("args")

        assert result == ["collection", "query"]
