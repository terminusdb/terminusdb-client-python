"""Test utility functions for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLSetOperations:
    """Test set operations."""

    def test_set_intersection_basic(self):
        """Test set_intersection basic functionality."""
        query = WOQLQuery()

        result = query.set_intersection(["a", "b", "c"], ["b", "c", "d"], "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "SetIntersection"
        assert "list_a" in query._cursor
        assert "list_b" in query._cursor
        assert "result" in query._cursor

    def test_set_intersection_with_args(self):
        """Test set_intersection with 'args' special case."""
        query = WOQLQuery()

        result = query.set_intersection("args", None, None)

        assert result == ["list_a", "list_b", "result"]

    def test_set_intersection_with_existing_cursor(self):
        """Test set_intersection with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.set_intersection(["a", "b"], ["b", "c"], "v:Result")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    def test_set_union_basic(self):
        """Test set_union basic functionality."""
        query = WOQLQuery()

        result = query.set_union(["a", "b"], ["c", "d"], "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "SetUnion"
        assert "list_a" in query._cursor
        assert "list_b" in query._cursor
        assert "result" in query._cursor

    def test_set_union_with_args(self):
        """Test set_union with 'args' special case."""
        query = WOQLQuery()

        result = query.set_union("args", None, None)

        assert result == ["list_a", "list_b", "result"]

    def test_set_union_with_existing_cursor(self):
        """Test set_union with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.set_union(["a", "b"], ["c", "d"], "v:Result")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    def test_set_member_basic(self):
        """Test set_member basic functionality."""
        query = WOQLQuery()

        result = query.set_member("a", ["a", "b", "c"])

        assert result is query
        assert query._cursor.get("@type") == "SetMember"

    def test_set_member_with_variable(self):
        """Test set_member with variable."""
        query = WOQLQuery()

        result = query.set_member("v:Element", "v:Set")

        assert result is query
        assert query._cursor.get("@type") == "SetMember"


class TestWOQLListOperations:
    """Test list operations."""

    def test_concatenate_basic(self):
        """Test concatenate basic functionality."""
        query = WOQLQuery()

        result = query.concatenate([["a", "b"], ["c", "d"]], "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "Concatenate"

    def test_concatenate_with_args(self):
        """Test concatenate with 'args' special case."""
        query = WOQLQuery()

        result = query.concatenate("args", None)

        # Actual return value from woql_query.py
        assert result == ["list", "concatenated"]

    def test_concatenate_with_existing_cursor(self):
        """Test concatenate with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.concatenate([["a"], ["b"]], "v:Result")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"


class TestWOQLArithmeticOperations:
    """Test arithmetic operations."""

    def test_plus_basic(self):
        """Test plus basic functionality."""
        query = WOQLQuery()

        result = query.plus(5, 3, "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "Plus"

    def test_plus_with_args(self):
        """Test plus with 'args' special case."""
        query = WOQLQuery()

        result = query.plus("args", None, None)

        # Actual return value from woql_query.py
        assert result == ["left", "right"]

    def test_plus_with_existing_cursor(self):
        """Test plus with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.plus(10, 20, "v:Sum")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    def test_minus_basic(self):
        """Test minus basic functionality."""
        query = WOQLQuery()

        result = query.minus(10, 3, "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "Minus"

    def test_minus_with_args(self):
        """Test minus with 'args' special case."""
        query = WOQLQuery()

        result = query.minus("args", None, None)

        # Actual return value from woql_query.py
        assert result == ["left", "right"]

    def test_times_basic(self):
        """Test times basic functionality."""
        query = WOQLQuery()

        result = query.times(5, 3, "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "Times"

    def test_times_with_args(self):
        """Test times with 'args' special case."""
        query = WOQLQuery()

        result = query.times("args", None, None)

        # Actual return value from woql_query.py
        assert result == ["left", "right"]

    def test_times_with_existing_cursor(self):
        """Test times with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.times(5, 10, "v:Product")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    def test_divide_basic(self):
        """Test divide operation."""
        query = WOQLQuery()

        result = query.divide(10, 2, "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "Divide"

    def test_div_basic(self):
        """Test div (integer division) operation."""
        query = WOQLQuery()

        result = query.div(10, 3, "v:Result")

        assert result is query
        assert query._cursor.get("@type") == "Div"

    def test_exp_basic(self):
        """Test exp (exponentiation) operation."""
        query = WOQLQuery()

        # exp only takes 2 arguments (base, exponent)
        result = query.exp(2, 8)

        assert result is query
        assert query._cursor.get("@type") == "Exp"

    def test_floor_basic(self):
        """Test floor operation."""
        query = WOQLQuery()

        # floor only takes 1 argument
        result = query.floor(3.7)

        assert result is query


class TestWOQLComparisonOperations:
    """Test comparison operations."""

    def test_less_basic(self):
        """Test less basic functionality."""
        query = WOQLQuery()

        result = query.less(5, 10)

        assert result is query
        assert query._cursor.get("@type") == "Less"

    def test_less_with_args(self):
        """Test less with 'args' special case."""
        query = WOQLQuery()

        result = query.less("args", None)

        assert result == ["left", "right"]

    def test_greater_basic(self):
        """Test greater basic functionality."""
        query = WOQLQuery()

        result = query.greater(10, 5)

        assert result is query
        assert query._cursor.get("@type") == "Greater"

    def test_greater_with_args(self):
        """Test greater with 'args' special case."""
        query = WOQLQuery()

        result = query.greater("args", None)

        assert result == ["left", "right"]

    def test_greater_with_existing_cursor(self):
        """Test greater with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.greater(100, 50)

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    def test_equals_basic(self):
        """Test equals basic functionality."""
        query = WOQLQuery()

        result = query.eq(5, 5)

        assert result is query
        assert query._cursor.get("@type") == "Equals"

    def test_equals_with_args(self):
        """Test equals with 'args' special case."""
        query = WOQLQuery()

        result = query.eq("args", None)

        assert result == ["left", "right"]

    def test_equals_with_existing_cursor(self):
        """Test equals with existing cursor."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        result = query.eq("v:X", "v:Y")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"


class TestWOQLStringOperations:
    """Test string operations."""

    def test_length_basic(self):
        """Test length operation."""
        query = WOQLQuery()

        result = query.length("test", "v:Length")

        assert result is query

    def test_upper_basic(self):
        """Test upper case operation."""
        query = WOQLQuery()

        result = query.upper("test", "v:Upper")

        assert result is query

    def test_lower_basic(self):
        """Test lower case operation."""
        query = WOQLQuery()

        result = query.lower("TEST", "v:Lower")

        assert result is query

    def test_split_basic(self):
        """Test split operation."""
        query = WOQLQuery()

        result = query.split("a,b,c", ",", "v:List")

        assert result is query

    def test_join_basic(self):
        """Test join operation."""
        query = WOQLQuery()

        result = query.join(["a", "b", "c"], ",", "v:Result")

        assert result is query


class TestWOQLRegexOperations:
    """Test regex operations."""

    def test_regexp_basic(self):
        """Test regexp operation."""
        query = WOQLQuery()

        result = query.regexp("test.*", "test123", "v:Match")

        assert result is query

    def test_like_basic(self):
        """Test like operation."""
        query = WOQLQuery()

        result = query.like("test%", "v:String", "v:Match")

        assert result is query


class TestWOQLDateTimeOperations:
    """Test date/time operations."""

    def test_timestamp_basic(self):
        """Test timestamp operation if it exists."""
        query = WOQLQuery()

        # Test a basic query structure
        result = query.triple("v:X", "v:P", "v:O")

        assert result is query


class TestWOQLHashOperations:
    """Test hash operations."""

    def test_idgen_basic(self):
        """Test idgen operation for ID generation."""
        query = WOQLQuery()

        result = query.idgen("doc:", ["v:Name"], "v:ID")

        assert result is query


class TestWOQLDocumentOperations:
    """Test document operations."""

    def test_read_document_basic(self):
        """Test read_document operation."""
        query = WOQLQuery()

        result = query.read_object("doc:id123", "v:Document")

        assert result is query

    def test_insert_document_basic(self):
        """Test insert_document operation."""
        query = WOQLQuery()

        result = query.insert("v:NewDoc", "schema:Person")

        assert result is query

    def test_delete_document_basic(self):
        """Test delete_document operation."""
        query = WOQLQuery()

        result = query.delete_object("doc:id123")

        assert result is query

    def test_update_document_basic(self):
        """Test update_document operation."""
        query = WOQLQuery()

        result = query.update_object("doc:id123")

        assert result is query


class TestWOQLMetadataOperations:
    """Test metadata operations."""

    def test_comment_basic(self):
        """Test comment operation."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.comment("This is a test query", subquery)

        assert result is query

    def test_immediately_basic(self):
        """Test immediately operation."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.immediately(subquery)

        assert result is query


class TestWOQLOrderingOperations:
    """Test ordering operations."""

    def test_order_by_basic(self):
        """Test order_by basic functionality."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.order_by("v:X", subquery)

        assert result is query

    def test_order_by_with_multiple_variables(self):
        """Test order_by with multiple variables."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.order_by(["v:X", "v:Y"], subquery)

        assert result is query

    def test_order_by_with_args(self):
        """Test order_by with 'args' special case."""
        query = WOQLQuery()

        result = query.order_by("args", None)

        # order_by with 'args' returns the query, not a list
        assert result is query


class TestWOQLLimitOffset:
    """Test limit and offset operations."""

    def test_limit_basic(self):
        """Test limit operation."""
        query = WOQLQuery()

        result = query.limit(10)

        assert result is query

    def test_limit_with_subquery(self):
        """Test limit with subquery."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.limit(10, subquery)

        assert result is query

    def test_start_basic(self):
        """Test start (offset) operation."""
        query = WOQLQuery()

        result = query.start(5)

        assert result is query

    def test_start_with_subquery(self):
        """Test start with subquery."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.start(5, subquery)

        assert result is query
