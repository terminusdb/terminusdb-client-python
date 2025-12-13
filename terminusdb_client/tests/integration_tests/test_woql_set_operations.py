"""
Integration tests for WOQL set operations.

These tests verify the new set operations:
- set_difference
- set_intersection
- set_union
- set_member
- list_to_set
"""
import time

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def extract_values(result_list):
    """Extract raw values from a list of typed literals."""
    if not result_list:
        return []
    return [item["@value"] if isinstance(item, dict) and "@value" in item else item
            for item in result_list]


class TestWOQLSetOperations:
    """Tests for WOQL set operations."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        """Setup and teardown for each test."""
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_woql_set_operations"
        
        # Create database for tests
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        
        yield
        
        # Cleanup
        self.client.delete_database(self.db_name)

    def test_set_difference_basic(self):
        """Test set_difference computes difference between two lists."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", [1, 2, 3, 4]),
            WOQLQuery().eq("v:ListB", [2, 4]),
            WOQLQuery().set_difference("v:ListA", "v:ListB", "v:Diff")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["Diff"]) == [1, 3]

    def test_set_difference_subset(self):
        """Test set_difference returns empty when first list is subset."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", [1, 2]),
            WOQLQuery().eq("v:ListB", [1, 2, 3]),
            WOQLQuery().set_difference("v:ListA", "v:ListB", "v:Diff")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["Diff"] == []

    def test_set_difference_empty_list(self):
        """Test set_difference handles empty lists."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", []),
            WOQLQuery().eq("v:ListB", [1]),
            WOQLQuery().set_difference("v:ListA", "v:ListB", "v:Diff")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["Diff"] == []

    def test_set_intersection_basic(self):
        """Test set_intersection computes intersection of two lists."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", [1, 2, 3]),
            WOQLQuery().eq("v:ListB", [2, 3, 4]),
            WOQLQuery().set_intersection("v:ListA", "v:ListB", "v:Common")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["Common"]) == [2, 3]

    def test_set_intersection_no_common(self):
        """Test set_intersection returns empty when no common elements."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", [1, 2]),
            WOQLQuery().eq("v:ListB", [3, 4]),
            WOQLQuery().set_intersection("v:ListA", "v:ListB", "v:Common")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["Common"] == []

    def test_set_union_basic(self):
        """Test set_union computes union of two lists."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", [1, 2]),
            WOQLQuery().eq("v:ListB", [2, 3]),
            WOQLQuery().set_union("v:ListA", "v:ListB", "v:All")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["All"]) == [1, 2, 3]

    def test_set_union_removes_duplicates(self):
        """Test set_union removes duplicates."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", [1, 1, 2]),
            WOQLQuery().eq("v:ListB", [2, 2]),
            WOQLQuery().set_union("v:ListA", "v:ListB", "v:All")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["All"]) == [1, 2]

    def test_set_member_success(self):
        """Test set_member succeeds for element in set."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:MySet", [1, 2, 3]),
            WOQLQuery().set_member(2, "v:MySet")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1

    def test_set_member_failure(self):
        """Test set_member fails for element not in set."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:MySet", [1, 2, 3]),
            WOQLQuery().set_member(5, "v:MySet")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 0

    def test_list_to_set(self):
        """Test list_to_set removes duplicates and sorts."""
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:MyList", [3, 1, 2, 1]),
            WOQLQuery().list_to_set("v:MyList", "v:MySet")
        )
        
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert extract_values(result["bindings"][0]["MySet"]) == [1, 2, 3]

    def test_performance_large_sets(self):
        """Test set operations handle large sets efficiently."""
        list_a = list(range(1000))
        list_b = list(range(500, 1500))
        
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:ListA", list_a),
            WOQLQuery().eq("v:ListB", list_b),
            WOQLQuery().set_difference("v:ListA", "v:ListB", "v:Diff")
        )
        
        start_time = time.time()
        result = self.client.query(query)
        elapsed = time.time() - start_time
        
        assert len(result["bindings"]) == 1
        assert len(result["bindings"][0]["Diff"]) == 500
        
        # Should complete in under 1 second with O(n log n) algorithm
        assert elapsed < 1.0
