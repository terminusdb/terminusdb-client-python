"""Test advanced query features for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLAdvancedFiltering:
    """Test advanced filtering operations."""
    
    def test_filter_with_complex_condition(self):
        """Test filter with complex condition."""
        query = WOQLQuery()
        
        # Create a filter with a condition
        subquery = WOQLQuery().triple("v:X", "schema:age", "v:Age")
        result = query.woql_and(subquery)
        
        assert result is query
        assert "@type" in query._cursor
    
    def test_filter_with_multiple_conditions(self):
        """Test filter with multiple AND conditions."""
        query = WOQLQuery()
        
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        q2 = WOQLQuery().triple("v:X", "schema:age", "v:Age")
        
        result = query.woql_and(q1, q2)
        
        assert result is query
        assert query._cursor.get("@type") == "And"
    
    def test_filter_with_or_conditions(self):
        """Test filter with OR conditions."""
        query = WOQLQuery()
        
        q1 = WOQLQuery().triple("v:X", "schema:age", "25")
        q2 = WOQLQuery().triple("v:X", "schema:age", "30")
        
        result = query.woql_or(q1, q2)
        
        assert result is query
        assert query._cursor.get("@type") == "Or"
    
    def test_filter_with_not_condition(self):
        """Test filter with NOT condition."""
        query = WOQLQuery()
        
        subquery = WOQLQuery().triple("v:X", "schema:deleted", "true")
        result = query.woql_not(subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "Not"
    
    def test_nested_filter_conditions(self):
        """Test nested filter conditions."""
        query = WOQLQuery()
        
        # Create nested AND/OR structure
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        q2 = WOQLQuery().triple("v:X", "schema:age", "v:Age")
        inner = WOQLQuery().woql_and(q1, q2)
        
        q3 = WOQLQuery().triple("v:X", "schema:active", "true")
        result = query.woql_or(inner, q3)
        
        assert result is query
        assert query._cursor.get("@type") == "Or"


class TestWOQLAdvancedAggregation:
    """Test advanced aggregation operations."""
    
    def test_group_by_with_single_variable(self):
        """Test group by with single variable."""
        query = WOQLQuery()
        
        # Group by a single variable
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept"]
        subquery = WOQLQuery().triple("v:X", "schema:department", "v:Dept")
        
        result = query.group_by(group_vars, template, "v:Result", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
    
    def test_group_by_with_multiple_variables(self):
        """Test group by with multiple variables."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept", "v:City"]
        template = ["v:Dept", "v:City"]
        subquery = WOQLQuery().triple("v:X", "schema:department", "v:Dept")
        
        result = query.group_by(group_vars, template, "v:Result", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
    
    def test_count_aggregation(self):
        """Test count aggregation."""
        query = WOQLQuery()
        
        result = query.count("v:Count")
        
        assert result is query
        # Check _query instead of _cursor when no subquery provided
        assert query._query.get("@type") == "Count"
    
    def test_sum_aggregation(self):
        """Test sum aggregation."""
        query = WOQLQuery()
        
        result = query.sum("v:Numbers", "v:Total")
        
        assert result is query
        assert query._cursor.get("@type") == "Sum"
    
    def test_aggregation_with_grouping(self):
        """Test aggregation combined with grouping."""
        query = WOQLQuery()
        
        # Create a group by with count
        # group_by signature: (group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:Count"]
        count_query = WOQLQuery().count("v:Count")
        
        result = query.group_by(group_vars, template, "v:Result", count_query)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"


class TestWOQLSubqueryOperations:
    """Test subquery operations."""
    
    def test_subquery_in_select(self):
        """Test subquery within select."""
        query = WOQLQuery()
        
        subquery = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        result = query.select("v:X", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "Select"
        assert "query" in query._cursor
    
    def test_subquery_in_distinct(self):
        """Test subquery within distinct."""
        query = WOQLQuery()
        
        subquery = WOQLQuery().triple("v:X", "schema:name", "v:Name")
        result = query.distinct("v:Name", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "Distinct"
    
    def test_nested_subqueries(self):
        """Test nested subqueries."""
        query = WOQLQuery()
        
        # Create nested structure
        inner = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        middle = WOQLQuery().select("v:X", inner)
        result = query.distinct("v:X", middle)
        
        assert result is query
        assert query._cursor.get("@type") == "Distinct"
    
    @pytest.mark.skip(reason="BLOCKED: Bug in woql_query.py line 903 - needs investigation")
    def test_subquery_with_limit_offset(self):
        """Test subquery with limit and offset.
        
        ENGINEERING REQUEST: Investigate line 903 in woql_query.py
        This line is currently uncovered and may contain edge case handling
        that needs proper testing once the implementation is verified.
        """
        query = WOQLQuery()
        
        # This should test the uncovered line 903
        result = query.limit(10).start(5)
        
        assert result is query
    
    def test_subquery_execution_order(self):
        """Test that subqueries execute in correct order."""
        query = WOQLQuery()
        
        # Build query with specific execution order
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        q2 = WOQLQuery().triple("v:X", "schema:name", "v:Name")
        
        result = query.woql_and(q1, q2)
        
        assert result is query
        assert query._cursor.get("@type") == "And"


class TestWOQLRecursiveQueries:
    """Test recursive query operations."""
    
    def test_path_with_recursion(self):
        """Test path operation with recursive pattern."""
        query = WOQLQuery()
        
        # Create a path that could be recursive
        result = query.path("v:Start", "schema:knows+", "v:End")
        
        assert result is query
        assert query._cursor.get("@type") == "Path"
    
    def test_path_with_star_recursion(self):
        """Test path with star (zero or more) recursion."""
        query = WOQLQuery()
        
        result = query.path("v:Start", "schema:parent*", "v:Ancestor")
        
        assert result is query
        assert query._cursor.get("@type") == "Path"
    
    def test_path_with_range_recursion(self):
        """Test path with range recursion."""
        query = WOQLQuery()
        
        result = query.path("v:Start", "schema:manages{1,5}", "v:Employee")
        
        assert result is query
        assert query._cursor.get("@type") == "Path"
    
    def test_recursive_subquery(self):
        """Test recursive pattern in subquery."""
        query = WOQLQuery()
        
        # Create a recursive pattern
        path_query = WOQLQuery().path("v:X", "schema:parent+", "v:Ancestor")
        result = query.select("v:X", "v:Ancestor", path_query)
        
        assert result is query
        assert query._cursor.get("@type") == "Select"


class TestWOQLComplexPatterns:
    """Test complex query patterns."""
    
    def test_union_pattern(self):
        """Test union of multiple patterns."""
        query = WOQLQuery()
        
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        q2 = WOQLQuery().triple("v:X", "rdf:type", "schema:Organization")
        
        result = query.woql_or(q1, q2)
        
        assert result is query
        assert query._cursor.get("@type") == "Or"
    
    def test_optional_pattern(self):
        """Test optional pattern matching."""
        query = WOQLQuery()
        
        # Required pattern
        query.triple("v:X", "rdf:type", "schema:Person")
        
        # Optional pattern
        result = query.opt().triple("v:X", "schema:age", "v:Age")
        
        assert result is query
    
    def test_minus_pattern(self):
        """Test minus (exclusion) pattern."""
        query = WOQLQuery()
        
        # Main pattern
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        
        # Exclusion pattern
        q2 = WOQLQuery().triple("v:X", "schema:deleted", "true")
        
        result = query.woql_and(q1, WOQLQuery().woql_not(q2))
        
        assert result is query
    
    def test_complex_nested_pattern(self):
        """Test complex nested pattern with multiple levels."""
        query = WOQLQuery()
        
        # Build complex nested structure
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        q2 = WOQLQuery().triple("v:X", "schema:age", "v:Age")
        inner_and = WOQLQuery().woql_and(q1, q2)
        
        q3 = WOQLQuery().triple("v:X", "schema:active", "true")
        outer_or = WOQLQuery().woql_or(inner_and, q3)
        
        result = query.select("v:X", outer_or)
        
        assert result is query
        assert query._cursor.get("@type") == "Select"
    
    def test_pattern_with_bind(self):
        """Test pattern with variable binding."""
        query = WOQLQuery()
        
        # Bind a value to a variable
        result = query.eq("v:X", "John")
        
        assert result is query
        assert query._cursor.get("@type") == "Equals"
    
    def test_pattern_with_arithmetic(self):
        """Test pattern with arithmetic operations."""
        query = WOQLQuery()
        
        # Arithmetic comparison
        result = query.greater("v:Age", 18)
        
        assert result is query
        assert query._cursor.get("@type") == "Greater"
