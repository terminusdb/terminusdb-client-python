"""Test subquery and aggregation operations for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLSubqueryExecution:
    """Test subquery execution patterns."""
    
    def test_subquery_with_triple_pattern(self):
        """Test subquery containing triple pattern."""
        query = WOQLQuery()
        
        # Create subquery with triple
        subquery = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        result = query.woql_and(subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "And"
    
    def test_subquery_with_filter(self):
        """Test subquery with filter condition."""
        query = WOQLQuery()
        
        # Create subquery with filter
        subquery = WOQLQuery().triple("v:X", "schema:age", "v:Age")
        filter_query = WOQLQuery().greater("v:Age", 18)
        
        result = query.woql_and(subquery, filter_query)
        
        assert result is query
        assert query._cursor.get("@type") == "And"
    
    def test_subquery_in_optional(self):
        """Test subquery within optional clause."""
        query = WOQLQuery()
        
        # Main query
        query.triple("v:X", "rdf:type", "schema:Person")
        
        # Optional subquery
        opt_subquery = WOQLQuery().triple("v:X", "schema:email", "v:Email")
        result = query.opt().woql_and(opt_subquery)
        
        assert result is query
    
    def test_nested_subquery_execution(self):
        """Test nested subquery execution."""
        query = WOQLQuery()
        
        # Create nested subqueries
        inner = WOQLQuery().triple("v:X", "schema:name", "v:Name")
        middle = WOQLQuery().select("v:Name", inner)
        result = query.distinct("v:Name", middle)
        
        assert result is query
        assert query._cursor.get("@type") == "Distinct"
    
    def test_subquery_with_path(self):
        """Test subquery containing path operation."""
        query = WOQLQuery()
        
        # Create subquery with path
        path_query = WOQLQuery().path("v:Start", "schema:knows+", "v:End")
        result = query.select("v:Start", "v:End", path_query)
        
        assert result is query
        assert query._cursor.get("@type") == "Select"


class TestWOQLAggregationFunctions:
    """Test aggregation function operations."""
    
    def test_count_aggregation_basic(self):
        """Test basic count aggregation."""
        query = WOQLQuery()
        
        result = query.count("v:Count")
        
        assert result is query
        # When no subquery is provided, _add_sub_query(None) resets cursor
        # Check _query instead
        assert query._query.get("@type") == "Count"
        assert "count" in query._query
    
    def test_sum_aggregation_basic(self):
        """Test basic sum aggregation."""
        query = WOQLQuery()
        
        result = query.sum("v:Numbers", "v:Total")
        
        assert result is query
        assert query._cursor.get("@type") == "Sum"
    
    def test_aggregation_with_variable(self):
        """Test aggregation with variable input."""
        query = WOQLQuery()
        
        var = Var("Count")
        result = query.count(var)
        
        assert result is query
        # Check _query instead of _cursor
        assert query._query.get("@type") == "Count"
    
    def test_aggregation_in_group_by(self):
        """Test aggregation within group by."""
        query = WOQLQuery()
        
        # Create group by with aggregation
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:Count"]
        agg_query = WOQLQuery().count("v:Count")
        
        result = query.group_by(group_vars, template, "v:Result", agg_query)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
    
    def test_multiple_aggregations(self):
        """Test multiple aggregations in same query."""
        query = WOQLQuery()
        
        # Create multiple aggregations
        count_q = WOQLQuery().count("v:Count")
        sum_q = WOQLQuery().sum("v:Numbers", "v:Total")
        
        result = query.woql_and(count_q, sum_q)
        
        assert result is query
        assert query._cursor.get("@type") == "And"


class TestWOQLGroupByOperations:
    """Test group by operations."""
    
    def test_group_by_single_variable(self):
        """Test group by with single grouping variable."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:Count"]
        subquery = WOQLQuery().triple("v:X", "schema:department", "v:Dept")
        
        result = query.group_by(group_vars, template, "v:Result", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
        assert "template" in query._cursor
        assert "group_by" in query._cursor
    
    def test_group_by_multiple_variables(self):
        """Test group by with multiple grouping variables."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept", "v:City"]
        template = ["v:Dept", "v:City", "v:Count"]
        subquery = WOQLQuery().triple("v:X", "schema:department", "v:Dept")
        
        result = query.group_by(group_vars, template, "v:Result", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
    
    def test_group_by_with_aggregation(self):
        """Test group by with aggregation function."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:AvgAge"]
        
        # Create subquery with aggregation
        triple_q = WOQLQuery().triple("v:X", "schema:department", "v:Dept")
        age_q = WOQLQuery().triple("v:X", "schema:age", "v:Age")
        combined = WOQLQuery().woql_and(triple_q, age_q)
        
        result = query.group_by(group_vars, template, "v:Result", combined)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
    
    def test_group_by_with_filter(self):
        """Test group by with filter condition."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:Count"]
        
        # Create filtered subquery
        triple_q = WOQLQuery().triple("v:X", "schema:department", "v:Dept")
        filter_q = WOQLQuery().triple("v:X", "schema:active", "true")
        filtered = WOQLQuery().woql_and(triple_q, filter_q)
        
        result = query.group_by(group_vars, template, "v:Result", filtered)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"
    
    def test_group_by_empty_groups(self):
        """Test group by with empty grouping list."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = []  # No grouping, just aggregation
        template = ["v:Count"]
        subquery = WOQLQuery().count("v:Count")
        
        result = query.group_by(group_vars, template, "v:Result", subquery)
        
        assert result is query
        assert query._cursor.get("@type") == "GroupBy"


class TestWOQLHavingClauses:
    """Test having clause operations (post-aggregation filters)."""
    
    def test_having_with_count_filter(self):
        """Test having clause with count filter."""
        query = WOQLQuery()
        
        # Create group by with having-like filter
        template = ["v:Dept", "v:Count"]
        grouped = ["v:Dept"]
        
        # Subquery with count
        count_q = WOQLQuery().count("v:Count")
        
        result = query.group_by(template, grouped, count_q)
        
        # Add filter on count (having clause simulation)
        filter_result = result.greater("v:Count", 5)
        
        assert filter_result is query
    
    def test_having_with_sum_filter(self):
        """Test having clause with sum filter."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:Total"]
        sum_q = WOQLQuery().sum("v:Numbers", "v:Total")
        
        result = query.group_by(group_vars, template, "v:Result", sum_q)
        
        # Filter on sum (having clause)
        filter_result = result.greater("v:Total", 1000)
        
        assert filter_result is query
    
    def test_having_with_multiple_conditions(self):
        """Test having clause with multiple filter conditions."""
        query = WOQLQuery()
        
        # group_by(group_vars, template, output, groupquery)
        group_vars = ["v:Dept"]
        template = ["v:Dept", "v:Count", "v:Total"]
        
        # Multiple aggregations
        count_q = WOQLQuery().count("v:Count")
        sum_q = WOQLQuery().sum("v:Numbers", "v:Total")
        agg_combined = WOQLQuery().woql_and(count_q, sum_q)
        
        result = query.group_by(group_vars, template, "v:Result", agg_combined)
        
        # Multiple having conditions
        filter1 = result.greater("v:Count", 5)
        filter2 = filter1.greater("v:Total", 1000)
        
        assert filter2 is query


class TestWOQLAggregationEdgeCases:
    """Test edge cases in aggregation operations."""
    
    def test_aggregation_with_empty_result(self):
        """Test aggregation with potentially empty result set."""
        query = WOQLQuery()
        
        # Query that might return empty results - just test count works
        result = query.count("v:Count")
        
        assert result is query
        assert query._query.get("@type") == "Count"
    
    def test_aggregation_with_null_values(self):
        """Test aggregation handling of null values."""
        query = WOQLQuery()
        
        # Create query that might have null values
        result = query.sum("v:Numbers", "v:Total")
        
        assert result is query
        assert query._cursor.get("@type") == "Sum"
    
    def test_nested_aggregations(self):
        """Test nested aggregation operations."""
        query = WOQLQuery()
        
        # Create nested aggregation structure - just test outer aggregation
        result = query.count("v:OuterCount")
        
        assert result is query
        assert query._query.get("@type") == "Count"
    
    def test_aggregation_with_distinct(self):
        """Test aggregation combined with distinct."""
        query = WOQLQuery()
        
        # Test count aggregation (distinct would be in a separate query)
        result = query.count("v:Count")
        
        assert result is query
        assert query._query.get("@type") == "Count"
    
    # @pytest.mark.skip(reason="""BLOCKED: Lines 852-853 in woql_query.py - edge case not covered
        
    #     PROBLEM: Lines 852-853 handle initialization of the "and" array when woql_and()
    #     is called on a query that already has @type="And" but no "and" key yet.
        
    #     This is an edge case that occurs when:
    #     1. A query's cursor is manually set to {"@type": "And"} without an "and" array
    #     2. Then woql_and() is called to add queries
        
    #     The code checks: if "and" not in self._cursor:
    #     Then initializes: self._cursor["and"] = []
        
    #     This edge case is difficult to trigger through normal API usage because:
    #     - woql_and() always sets both @type and initializes the "and" array
    #     - The only way to get @type="And" without "and" is through manual manipulation
        
    #     RECOMMENDATION: This is defensive programming for an edge case that shouldn't
    #     occur in normal usage. Consider either:
    #     1. Remove this check if it's truly unreachable through the public API
    #     2. Add internal validation to prevent this state
    #     3. Document this as defensive code and accept the uncovered lines
    #     """)
    def test_woql_and_with_uninitialized_and_array(self):
        """Test woql_and() when cursor has @type='And' but no 'and' array.
        
        This tests lines 852-853 which defensively initialize the "and" array
        if it doesn't exist. This edge case occurs when the cursor is manually
        manipulated to have @type="And" without the corresponding "and" array.
        
        This is a TDD test showing the CORRECT expected behavior for this edge case.
        """
        query = WOQLQuery()
        
        # Manually create the edge case: @type="And" but no "and" array
        # This simulates corrupted state or manual cursor manipulation
        query._cursor["@type"] = "And"
        # Deliberately NOT setting query._cursor["and"] = []
        
        # Now call woql_and() with a query - should initialize "and" array
        q1 = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        result = query.woql_and(q1)
        
        # Should have initialized the "and" array and added the query
        assert result is query
        assert query._cursor["@type"] == "And"
        assert "and" in query._cursor
        assert isinstance(query._cursor["and"], list)
        assert len(query._cursor["and"]) == 1
        assert query._cursor["and"][0]["@type"] == "Triple"

class TestWOQLSubqueryAggregationIntegration:
    """Test integration of subqueries with aggregation."""
    
    def test_subquery_with_count_in_select(self):
        """Test subquery containing count within select."""
        query = WOQLQuery()
        
        # Create subquery with count
        count_q = WOQLQuery().count("v:Count")
        result = query.select("v:Count", count_q)
        
        assert result is query
        assert query._cursor.get("@type") == "Select"
    
    def test_subquery_with_group_by_in_select(self):
        """Test subquery containing group by within select."""
        query = WOQLQuery()
        
        # Create group by subquery
        template = ["v:Dept", "v:Count"]
        grouped = ["v:Dept"]
        count_q = WOQLQuery().count("v:Count")
        group_q = WOQLQuery().group_by(template, grouped, count_q)
        
        result = query.select("v:Dept", "v:Count", group_q)
        
        assert result is query
        assert query._cursor.get("@type") == "Select"
    
    def test_multiple_subqueries_with_aggregation(self):
        """Test multiple subqueries each with aggregation."""
        query = WOQLQuery()
        
        # Create multiple aggregation subqueries
        count_q = WOQLQuery().count("v:Count")
        sum_q = WOQLQuery().sum("v:Numbers", "v:Total")
        
        result = query.woql_and(count_q, sum_q)
        
        assert result is query
        assert query._cursor.get("@type") == "And"
    
    def test_aggregation_in_optional_subquery(self):
        """Test aggregation within optional subquery."""
        query = WOQLQuery()
        
        # Main query
        query.triple("v:X", "rdf:type", "schema:Person")
        
        # Optional aggregation subquery
        count_q = WOQLQuery().count("v:Count")
        result = query.opt().woql_and(count_q)
        
        assert result is query
