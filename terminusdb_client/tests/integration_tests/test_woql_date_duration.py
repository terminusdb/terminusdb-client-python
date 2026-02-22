"""
Integration tests for WOQL DateDuration predicate.

Tests the tri-directional DateDuration(Start, End, Duration) predicate:
- Start + End → Duration (compute duration from two dates)
- Start + Duration → End (EOM-aware addition)
- Duration + End → Start (EOM-aware subtraction)
- All three ground (validation)
- EOM reversibility
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


class TestDateDurationComputeDuration:
    """Start + End → Duration."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_date_dur_compute"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_leap_year_91_days(self):
        """2024-01-01 to 2024-04-01 = P91D (leap year)."""
        query = WOQLQuery().date_duration(dat("2024-01-01"), dat("2024-04-01"), "v:d")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["d"]["@value"] == "P91D"

    def test_non_leap_year_90_days(self):
        """2025-01-01 to 2025-04-01 = P90D (non-leap year)."""
        query = WOQLQuery().date_duration(dat("2025-01-01"), dat("2025-04-01"), "v:d")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["d"]["@value"] == "P90D"

    def test_zero_duration(self):
        """Same date produces P0D."""
        query = WOQLQuery().date_duration(dat("2024-01-01"), dat("2024-01-01"), "v:d")
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["d"]["@value"] == "P0D"

    def test_datetime_time_difference(self):
        """dateTime with sub-day difference produces PT9H30M."""
        query = WOQLQuery().date_duration(
            dtm("2024-01-01T08:00:00Z"), dtm("2024-01-01T17:30:00Z"), "v:d"
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["d"]["@value"] == "PT9H30M"

    def test_datetime_midnight_to_midnight(self):
        """Midnight-to-midnight omits time component: P3D."""
        query = WOQLQuery().date_duration(
            dtm("2024-01-01T00:00:00Z"), dtm("2024-01-04T00:00:00Z"), "v:d"
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["d"]["@value"] == "P3D"


class TestDateDurationAddition:
    """Start + Duration → End (EOM-aware)."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_date_dur_add"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_jan31_plus_1m_leap(self):
        """Jan 31 + P1M = Feb 29 (leap year EOM)."""
        query = WOQLQuery().date_duration(dat("2020-01-31"), "v:e", dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["e"]["@value"] == "2020-02-29"

    def test_jan31_plus_1m_non_leap(self):
        """Jan 31 + P1M = Feb 28 (non-leap year EOM)."""
        query = WOQLQuery().date_duration(dat("2021-01-31"), "v:e", dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["e"]["@value"] == "2021-02-28"

    def test_feb29_plus_1m_eom_preservation(self):
        """Feb 29 + P1M = Mar 31 (EOM preservation)."""
        query = WOQLQuery().date_duration(dat("2020-02-29"), "v:e", dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["e"]["@value"] == "2020-03-31"

    def test_apr30_plus_1m_eom_preservation(self):
        """Apr 30 + P1M = May 31 (EOM preservation)."""
        query = WOQLQuery().date_duration(dat("2020-04-30"), "v:e", dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["e"]["@value"] == "2020-05-31"

    def test_dec31_plus_1m_year_boundary(self):
        """Dec 31 + P1M = Jan 31 next year."""
        query = WOQLQuery().date_duration(dat("2020-12-31"), "v:e", dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["e"]["@value"] == "2021-01-31"


class TestDateDurationSubtraction:
    """Duration + End → Start (EOM-aware)."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_date_dur_sub"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_mar31_minus_1m_leap(self):
        """Mar 31 - P1M = Feb 29 (leap year)."""
        query = WOQLQuery().date_duration("v:s", dat("2020-03-31"), dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@value"] == "2020-02-29"

    def test_mar31_minus_1m_non_leap(self):
        """Mar 31 - P1M = Feb 28 (non-leap year)."""
        query = WOQLQuery().date_duration("v:s", dat("2021-03-31"), dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@value"] == "2021-02-28"

    def test_jan31_minus_1m_year_boundary(self):
        """Jan 31 - P1M = Dec 31 previous year."""
        query = WOQLQuery().date_duration("v:s", dat("2021-01-31"), dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@value"] == "2020-12-31"


class TestDateDurationEOMReversibility:
    """EOM reversibility: add then subtract returns original."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_date_dur_eom"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_feb29_minus_1m_equals_jan31(self):
        """Feb 29 - P1M = Jan 31 (reverse of Jan 31 + P1M = Feb 29)."""
        query = WOQLQuery().date_duration("v:s", dat("2020-02-29"), dur("P1M"))
        result = self.client.query(query)
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["s"]["@value"] == "2020-01-31"


class TestDateDurationValidation:
    """All three ground — validation mode."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, docker_url):
        self.client = Client(docker_url, user_agent=test_user_agent)
        self.client.connect()
        self.db_name = "test_date_dur_val"
        if self.db_name in self.client.list_databases():
            self.client.delete_database(self.db_name)
        self.client.create_database(self.db_name)
        yield
        self.client.delete_database(self.db_name)

    def test_consistent_succeeds(self):
        """Consistent start+end+duration returns one binding."""
        query = WOQLQuery().date_duration(
            dat("2024-01-01"), dat("2024-04-01"), dur("P91D")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 1

    def test_inconsistent_fails(self):
        """Inconsistent start+end+duration returns zero bindings."""
        query = WOQLQuery().date_duration(
            dat("2024-01-01"), dat("2024-04-01"), dur("P90D")
        )
        result = self.client.query(query)
        assert len(result["bindings"]) == 0
