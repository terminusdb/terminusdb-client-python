"""
Integration tests for WOQL Collect predicate.

Collect gathers all solutions from a sub-query into a list,
completing the list/binding symmetry alongside Member:
- Member: List -> Bindings (destructure)
- Collect: Bindings -> List (gather)
"""

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def extract_values(result_list):
    """Extract raw values from a list of typed literals."""
    if not result_list:
        return []
    return [
        item["@value"] if isinstance(item, dict) and "@value" in item else item
        for item in result_list
    ]


class TestWOQLCollect:
    """Tests for the WOQL Collect predicate."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        """Setup and teardown for each test."""
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_woql_collect"

        # Create database for tests
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)

        # Add schema
        self.client.insert_document(
            [
                {
                    "@type": "@context",
                    "@base": "terminusdb:///data/",
                    "@schema": "terminusdb:///schema#",
                },
                {
                    "@id": "NamedThing",
                    "@type": "Class",
                    "@key": {"@type": "Lexical", "@fields": ["name"]},
                    "name": "xsd:string",
                },
            ],
            graph_type="schema",
            full_replace=True,
        )

        # Insert test documents
        self.client.insert_document(
            [
                {"@type": "NamedThing", "name": "Alice"},
                {"@type": "NamedThing", "name": "Bob"},
                {"@type": "NamedThing", "name": "Carol"},
            ]
        )

        yield

        # Cleanup
        self.client.delete_database(self.db_name)

    def test_collect_triple_objects_into_list(self):
        """Collect gathers all matching triple objects into a single list."""
        query = WOQLQuery().collect(
            "v:name",
            "v:names",
            WOQLQuery().triple("v:doc", "name", "v:name"),
        )

        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        names = sorted(extract_values(result["bindings"][0]["names"]))
        assert names == ["Alice", "Bob", "Carol"]

    def test_collect_empty_result(self):
        """Collect produces empty list when sub-query has no solutions."""
        query = WOQLQuery().collect(
            "v:x",
            "v:collected",
            WOQLQuery().triple("v:doc", "nonexistent_property", "v:x"),
        )

        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["collected"] == []

    def test_collect_composes_with_length(self):
        """Collect result can be used with length to count solutions."""
        query = WOQLQuery().woql_and(
            WOQLQuery().collect(
                "v:name",
                "v:names",
                WOQLQuery().triple("v:doc", "name", "v:name"),
            ),
            WOQLQuery().length("v:names", "v:count"),
        )

        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["count"]["@value"] == 3

    def test_collect_with_limit_in_subquery(self):
        """Collect respects limit inside the sub-query."""
        query = WOQLQuery().collect(
            "v:name",
            "v:names",
            WOQLQuery().limit(2, WOQLQuery().triple("v:doc", "name", "v:name")),
        )

        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert len(result["bindings"][0]["names"]) == 2

    def test_collect_with_list_template(self):
        """Collect with multi-element list template produces nested lists."""
        query = WOQLQuery().collect(
            ["v:doc", "v:name"],
            "v:pairs",
            WOQLQuery().triple("v:doc", "name", "v:name"),
        )

        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        pairs = result["bindings"][0]["pairs"]
        assert len(pairs) == 3
        for pair in pairs:
            assert isinstance(pair, list)
            assert len(pair) == 2
