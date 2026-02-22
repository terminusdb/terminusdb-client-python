"""
Integration tests for WOQL interval duration predicates.

These tests verify the new interval features:
- Interval with xsd:dateTime endpoints
- IntervalStartDuration (start + duration decomposition)
- IntervalDurationEnd (duration + end decomposition)
- Roundtrip consistency across all three interval views
"""

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery

test_user_agent = "terminusdb-client-python-tests"


def dat(v):
    """Build an xsd:date typed literal."""
    return {"@type": "xsd:date", "@value": v}


def dtm(v):
    """Build an xsd:dateTime typed literal."""
    return {"@type": "xsd:dateTime", "@value": v}


def dur(v):
    """Build an xsd:duration typed literal."""
    return {"@type": "xsd:duration", "@value": v}


def dti(v):
    """Build an xdd:dateTimeInterval typed literal."""
    return {"@type": "xdd:dateTimeInterval", "@value": v}


class TestIntervalDateTimeEndpoints:
    """Tests for Interval predicate with xsd:dateTime endpoints."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_interval_duration"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_construct_from_datetime_endpoints(self):
        """Construct interval from two xsd:dateTime values."""
        query = WOQLQuery().interval(dtm("2025-01-01T09:00:00Z"),
                                     dtm("2025-01-01T17:30:00Z"),
                                     "v:iv")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["iv"]["@value"] == \
            "2025-01-01T09:00:00Z/2025-01-01T17:30:00Z"

    def test_construct_mixed_date_datetime(self):
        """Construct interval with date start and dateTime end."""
        query = WOQLQuery().interval(dat("2025-01-01"),
                                     dtm("2025-04-01T12:00:00Z"),
                                     "v:iv")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["iv"]["@value"] == \
            "2025-01-01/2025-04-01T12:00:00Z"

    def test_deconstruct_datetime_interval(self):
        """Deconstruct dateTime interval preserves types."""
        query = WOQLQuery().interval("v:s", "v:e",
                                     dti("2025-01-01T09:00:00Z/2025-04-01T17:30:00Z"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@type"] == "xsd:dateTime"
        assert result["bindings"][0]["e"]["@type"] == "xsd:dateTime"


class TestIntervalStartDuration:
    """Tests for IntervalStartDuration predicate."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_interval_start_dur"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_extract_start_and_duration_from_date_interval(self):
        """Extract start + P90D duration from a 90-day interval."""
        query = WOQLQuery().interval_start_duration(
            "v:s", "v:d", dti("2025-01-01/2025-04-01"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@value"] == "2025-01-01"
        assert result["bindings"][0]["d"]["@value"] == "P90D"

    def test_extract_sub_day_duration_from_datetime_interval(self):
        """Extract PT8H30M duration from a sub-day dateTime interval."""
        query = WOQLQuery().interval_start_duration(
            "v:s", "v:d",
            dti("2025-01-01T09:00:00Z/2025-01-01T17:30:00Z"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@type"] == "xsd:dateTime"
        assert result["bindings"][0]["d"]["@value"] == "PT8H30M"

    def test_construct_interval_from_start_and_duration(self):
        """Construct [Jan 1, Apr 1) from start date + P90D."""
        query = WOQLQuery().interval_start_duration(
            dat("2025-01-01"), dur("P90D"), "v:iv")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["iv"]["@value"] == "2025-01-01/2025-04-01"

    def test_construct_full_year_interval(self):
        """Construct a 365-day interval from start + P365D."""
        query = WOQLQuery().interval_start_duration(
            dat("2025-01-01"), dur("P365D"), "v:iv")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["iv"]["@value"] == "2025-01-01/2026-01-01"


class TestIntervalDurationEnd:
    """Tests for IntervalDurationEnd predicate."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_interval_dur_end"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_extract_duration_and_end_from_interval(self):
        """Extract P90D + end date from a 90-day interval."""
        query = WOQLQuery().interval_duration_end(
            "v:d", "v:e", dti("2025-01-01/2025-04-01"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["e"]["@value"] == "2025-04-01"
        assert result["bindings"][0]["d"]["@value"] == "P90D"

    def test_construct_interval_from_duration_and_end(self):
        """Construct [Jan 1, Apr 1) from P90D + end date."""
        query = WOQLQuery().interval_duration_end(
            dur("P90D"), dat("2025-04-01"), "v:iv")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["iv"]["@value"] == "2025-01-01/2025-04-01"


class TestIntervalThreeViewsRoundtrip:
    """Roundtrip test: all three decomposition views of the same interval agree."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_interval_roundtrip"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_three_views_agree(self):
        """start/end, start/duration, and duration/end all agree."""
        iv = dti("2025-01-01/2025-04-01")
        query = WOQLQuery().woql_and(
            WOQLQuery().interval("v:s1", "v:e1", iv),
            WOQLQuery().interval_start_duration("v:s2", "v:d2", iv),
            WOQLQuery().interval_duration_end("v:d3", "v:e3", iv),
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        b = result["bindings"][0]
        assert b["s1"]["@value"] == b["s2"]["@value"]
        assert b["e1"]["@value"] == b["e3"]["@value"]
        assert b["d2"]["@value"] == b["d3"]["@value"]
        assert b["d2"]["@value"] == "P90D"
