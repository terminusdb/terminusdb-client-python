"""
Integration tests for WOQL IntervalRelationTyped predicate.

Tests Allen's Interval Algebra on xdd:dateTimeInterval values:
- Validation mode (relation ground)
- Classification mode (relation as variable)
- dateTime interval support
"""

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def iv(v):
    """Build an xdd:dateTimeInterval typed literal."""
    return {"@type": "xdd:dateTimeInterval", "@value": v}


def rel(v):
    """Build an xsd:string typed literal for the relation name."""
    return {"@type": "xsd:string", "@value": v}


class TestIntervalRelationTypedValidation:
    """Validation mode: relation is ground."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_irt_validate"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_meets(self):
        """Q1 meets Q2."""
        query = WOQLQuery().interval_relation_typed(
            rel("meets"), iv("2024-01-01/2024-04-01"), iv("2024-04-01/2024-07-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1

    def test_meets_rejected_with_gap(self):
        """Gap between intervals fails meets."""
        query = WOQLQuery().interval_relation_typed(
            rel("meets"), iv("2024-01-01/2024-04-01"), iv("2024-05-01/2024-07-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 0

    def test_before(self):
        """Q1 before Q3."""
        query = WOQLQuery().interval_relation_typed(
            rel("before"), iv("2024-01-01/2024-03-01"), iv("2024-06-01/2024-09-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1

    def test_during(self):
        """Sub-interval during year."""
        query = WOQLQuery().interval_relation_typed(
            rel("during"), iv("2024-03-01/2024-06-01"), iv("2024-01-01/2024-12-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1

    def test_equals(self):
        """Same interval."""
        query = WOQLQuery().interval_relation_typed(
            rel("equals"), iv("2024-01-01/2024-06-01"), iv("2024-01-01/2024-06-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1

    def test_contains(self):
        """FY contains Q2."""
        query = WOQLQuery().interval_relation_typed(
            rel("contains"), iv("2024-01-01/2025-01-01"), iv("2024-04-01/2024-07-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1


class TestIntervalRelationTypedClassification:
    """Classification mode: relation is a variable."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_irt_classify"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_classifies_meets(self):
        """Adjacent intervals classified as meets."""
        query = WOQLQuery().interval_relation_typed(
            "v:rel", iv("2024-01-01/2024-04-01"), iv("2024-04-01/2024-07-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["rel"]["@value"] == "meets"

    def test_classifies_before(self):
        """Non-overlapping intervals classified as before."""
        query = WOQLQuery().interval_relation_typed(
            "v:rel", iv("2024-01-01/2024-03-01"), iv("2024-06-01/2024-09-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["rel"]["@value"] == "before"

    def test_classifies_during(self):
        """Nested interval classified as during."""
        query = WOQLQuery().interval_relation_typed(
            "v:rel", iv("2024-03-01/2024-06-01"), iv("2024-01-01/2024-12-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["rel"]["@value"] == "during"

    def test_classifies_equals(self):
        """Identical intervals classified as equals."""
        query = WOQLQuery().interval_relation_typed(
            "v:rel", iv("2024-01-01/2024-06-01"), iv("2024-01-01/2024-06-01")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["rel"]["@value"] == "equals"

    def test_classifies_datetime_meets(self):
        """dateTime intervals classified as meets."""
        query = WOQLQuery().interval_relation_typed(
            "v:rel",
            iv("2024-01-01T08:00:00Z/2024-01-01T12:00:00Z"),
            iv("2024-01-01T12:00:00Z/2024-01-01T17:00:00Z"),
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["rel"]["@value"] == "meets"
