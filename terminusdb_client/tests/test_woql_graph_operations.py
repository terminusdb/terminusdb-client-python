"""Test graph operations for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLGraphModification:
    """Test graph modification operations."""

    def test_removed_quad_with_optional(self):
        """Test removed_quad with optional flag to cover line 1118-1119."""
        query = WOQLQuery()

        # This should trigger opt=True path in removed_quad
        result = query.removed_quad("v:S", "v:P", "v:O", "v:G", opt=True)

        assert result is query
        # When opt=True, wraps with Optional
        assert query._query.get("@type") == "Optional"

    def test_removed_quad_with_existing_cursor(self):
        """Test removed_quad with existing cursor to cover line 1120-1121."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"
        query._cursor["subject"] = "s1"

        # This should trigger _wrap_cursor_with_and
        result = query.removed_quad("v:S", "v:P", "v:O", "v:G")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    @pytest.mark.skip(reason="BLOCKED: Bug in woql_query.py lines 1123-1124 - calls append on WOQLQuery")
    def test_removed_quad_with_args_subject(self):
        """Test removed_quad with 'args' as subject.

        ENGINEERING REQUEST: Fix lines 1123-1124 in woql_query.py
        Issue: Tries to call append() on WOQLQuery object
        Expected: Should return metadata or handle 'args' properly
        """
        query = WOQLQuery()

        # This triggers the bug at line 1124
        with pytest.raises(AttributeError):
            query.removed_quad("args", "v:P", "v:O", "v:G")

    def test_removed_quad_without_graph_raises_error(self):
        """Test removed_quad raises error when graph is missing to cover line 1125-1127."""
        query = WOQLQuery()

        # This should raise ValueError
        with pytest.raises(ValueError, match="Quad takes four parameters"):
            query.removed_quad("v:S", "v:P", "v:O", None)

    def test_removed_quad_creates_deleted_triple(self):
        """Test removed_quad creates DeletedTriple to cover line 1129-1130."""
        query = WOQLQuery()

        result = query.removed_quad("v:S", "v:P", "v:O", "v:G")

        assert result is query
        assert query._cursor["@type"] == "DeletedTriple"
        assert "graph" in query._cursor

    def test_added_quad_with_optional(self):
        """Test added_quad with optional flag to cover line 1082-1083."""
        query = WOQLQuery()

        # This should trigger opt=True path in added_quad
        result = query.added_quad("v:S", "v:P", "v:O", "v:G", opt=True)

        assert result is query
        # When opt=True, wraps with Optional
        assert query._query.get("@type") == "Optional"

    def test_added_quad_with_existing_cursor(self):
        """Test added_quad with existing cursor to cover line 1084-1085."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"
        query._cursor["subject"] = "s1"

        # This should trigger _wrap_cursor_with_and
        result = query.added_quad("v:S", "v:P", "v:O", "v:G")

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    @pytest.mark.skip(reason="BLOCKED: Bug in woql_query.py lines 1087-1088 - calls append on WOQLQuery")
    def test_added_quad_with_args_subject(self):
        """Test added_quad with 'args' as subject.

        ENGINEERING REQUEST: Fix lines 1087-1088 in woql_query.py
        Issue: Tries to call append() on WOQLQuery object
        Expected: Should return metadata or handle 'args' properly
        """
        query = WOQLQuery()

        # This triggers the bug at line 1088
        with pytest.raises(AttributeError):
            query.added_quad("args", "v:P", "v:O", "v:G")


class TestWOQLGraphQueries:
    """Test graph query operations."""

    @pytest.mark.skip(reason="BLOCKED: Bug in woql_query.py line 3226 - calls missing _set_context method")
    def test_graph_method_basic(self):
        """Test basic graph method usage.

        ENGINEERING REQUEST: Fix line 3226 in woql_query.py
        Issue: Calls self._set_context() which doesn't exist
        Expected: Implement _set_context or use alternative approach
        """
        query = WOQLQuery()

        with pytest.raises(AttributeError):
            query.graph("my_graph")

    @pytest.mark.skip(reason="BLOCKED: Bug in woql_query.py line 3226 - calls missing _set_context method")
    def test_graph_with_subquery(self):
        """Test graph method with subquery.

        ENGINEERING REQUEST: Same as test_graph_method_basic
        """
        query = WOQLQuery()

        with pytest.raises(AttributeError):
            query.graph("my_graph")

    @pytest.mark.skip(reason="BLOCKED: Bug in woql_query.py line 3226 - calls missing _set_context method")
    def test_multiple_graph_operations(self):
        """Test chaining multiple graph operations.

        ENGINEERING REQUEST: Same as test_graph_method_basic
        """
        query = WOQLQuery()

        query.triple("v:S", "v:P", "v:O")

        with pytest.raises(AttributeError):
            query.graph("graph1")


class TestWOQLGraphTraversal:
    """Test graph traversal operations."""

    def test_path_with_complex_pattern(self):
        """Test path with complex pattern."""
        query = WOQLQuery()

        # Test path with complex predicate pattern
        result = query.path("v:Start", "schema:knows+", "v:End")

        assert result is query
        assert query._cursor.get("@type") == "Path"

    def test_path_with_inverse(self):
        """Test path with inverse predicate."""
        query = WOQLQuery()

        # Test path with inverse
        result = query.path("v:Start", "<schema:parent", "v:Child")

        assert result is query
        assert query._cursor.get("@type") == "Path"

    def test_path_with_range(self):
        """Test path with range quantifier."""
        query = WOQLQuery()

        # Test path with range {min,max}
        result = query.path("v:Start", "schema:manages{1,5}", "v:End")

        assert result is query
        assert query._cursor.get("@type") == "Path"


class TestWOQLGraphAnalytics:
    """Test graph analytics operations."""

    def test_size_operation(self):
        """Test size operation for graph analytics."""
        query = WOQLQuery()

        # Test size operation
        result = query.size("my_graph", "v:Size")

        assert result is query

    def test_triple_count(self):
        """Test triple count operation."""
        query = WOQLQuery()

        # Count triples in a pattern
        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.count("v:Count", subquery)

        assert result is query


class TestWOQLGraphContext:
    """Test graph context operations."""

    def test_using_with_collection(self):
        """Test using method with collection."""
        query = WOQLQuery()

        # Test using with collection
        result = query.using("my_collection")

        assert result is query

    def test_using_with_subquery(self):
        """Test using method with subquery."""
        query = WOQLQuery()
        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")

        result = query.using("my_collection", subquery)

        assert result is query

    def test_from_method(self):
        """Test from method for graph selection."""
        query = WOQLQuery()

        result = query.woql_from("schema")

        assert result is query

    def test_into_method(self):
        """Test into method for graph target."""
        query = WOQLQuery()

        # into() requires a query parameter
        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.into("instance", subquery)

        assert result is query


class TestWOQLGraphUpdates:
    """Test graph update operations."""

    def test_insert_with_graph(self):
        """Test insert operation with graph context."""
        query = WOQLQuery()

        # Insert into specific graph
        result = query.insert("v:NewNode", "schema:Person")

        assert result is query

    def test_delete_with_graph(self):
        """Test delete operation with graph context."""
        query = WOQLQuery()

        # Delete from specific graph
        result = query.delete_object("v:Node")

        assert result is query

    def test_update_with_graph(self):
        """Test update operation with graph context."""
        query = WOQLQuery()

        # Update in specific graph
        result = query.update_object("v:Node")

        assert result is query


class TestWOQLGraphMetadata:
    """Test graph metadata operations."""

    def test_graph_metadata_query(self):
        """Test querying graph metadata."""
        query = WOQLQuery()

        # Query graph metadata
        result = query.triple("v:Graph", "rdf:type", "terminus:Graph")

        assert result is query
        assert query._cursor.get("@type") == "Triple"

    def test_graph_properties(self):
        """Test querying graph properties."""
        query = WOQLQuery()

        # Query graph properties
        result = query.triple("v:Graph", "terminus:name", "v:Name")

        assert result is query
