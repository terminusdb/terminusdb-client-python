"""
Integration tests for WOQL RangeMin and RangeMax predicates.

Tests finding minimum and maximum values in lists:
- Integer lists
- Date lists
- Single element
- Empty list
- Equal elements
"""

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def intv(v):
    """Build an xsd:integer typed literal."""
    return {"@type": "xsd:integer", "@value": v}


def datv(v):
    """Build an xsd:date typed literal."""
    return {"@type": "xsd:date", "@value": v}


class TestRangeMin:
    """Integration tests for RangeMin."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_range_min"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_min_integers(self):
        """Minimum of [7, 2, 9, 1, 5] is 1."""
        query = WOQLQuery().range_min(
            [intv(7), intv(2), intv(9), intv(1), intv(5)], "v:m"
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["m"]["@value"] == 1

    def test_min_single_element(self):
        """Single element list returns that element."""
        query = WOQLQuery().range_min([intv(42)], "v:m")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["m"]["@value"] == 42

    def test_min_empty_list(self):
        """Empty list yields no bindings."""
        query = WOQLQuery().range_min([], "v:m")
        result = self.client.query(query)
        assert len(result["bindings"]) == 0

    def test_min_dates(self):
        """Minimum of dates."""
        query = WOQLQuery().range_min(
            [datv("2024-06-15"), datv("2024-01-01"), datv("2024-03-01")], "v:m"
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["m"]["@value"] == "2024-01-01"

    def test_min_equal_elements(self):
        """All equal elements returns that element."""
        query = WOQLQuery().range_min([intv(3), intv(3), intv(3)], "v:m")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["m"]["@value"] == 3


class TestRangeMax:
    """Integration tests for RangeMax."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_range_max"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_max_integers(self):
        """Maximum of [7, 2, 9, 1, 5] is 9."""
        query = WOQLQuery().range_max(
            [intv(7), intv(2), intv(9), intv(1), intv(5)], "v:m"
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["m"]["@value"] == 9

    def test_max_dates(self):
        """Maximum of dates."""
        query = WOQLQuery().range_max(
            [datv("2024-06-15"), datv("2024-01-01"), datv("2024-03-01")], "v:m"
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["m"]["@value"] == "2024-06-15"
