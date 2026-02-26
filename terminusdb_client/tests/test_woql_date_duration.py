"""Unit tests for WOQLQuery.date_duration JSON serialization."""

from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestDateDurationSerialization:
    """Tests that date_duration produces the correct WOQL JSON AST."""

    def test_all_variables(self):
        """All three arguments as variables."""
        query = WOQLQuery().date_duration("v:s", "v:e", "v:d")
        expected = {
            "@type": "DateDuration",
            "start": {"@type": "Value", "variable": "s"},
            "end": {"@type": "Value", "variable": "e"},
            "duration": {"@type": "Value", "variable": "d"},
        }
        assert query.to_dict() == expected

    def test_start_and_end_ground_duration_variable(self):
        """Start and end as typed literals, duration as variable."""
        query = WOQLQuery().date_duration(
            {"@type": "xsd:date", "@value": "2024-01-01"},
            {"@type": "xsd:date", "@value": "2024-04-01"},
            "v:d",
        )
        result = query.to_dict()
        assert result["@type"] == "DateDuration"
        assert result["duration"] == {"@type": "Value", "variable": "d"}
        assert result["start"]["@type"] == "Value"
        assert result["end"]["@type"] == "Value"

    def test_start_and_duration_ground_end_variable(self):
        """Start and duration ground, end as variable."""
        query = WOQLQuery().date_duration(
            {"@type": "xsd:date", "@value": "2020-01-31"},
            "v:e",
            {"@type": "xsd:duration", "@value": "P1M"},
        )
        result = query.to_dict()
        assert result["@type"] == "DateDuration"
        assert result["end"] == {"@type": "Value", "variable": "e"}

    def test_end_and_duration_ground_start_variable(self):
        """End and duration ground, start as variable."""
        query = WOQLQuery().date_duration(
            "v:s",
            {"@type": "xsd:date", "@value": "2020-03-31"},
            {"@type": "xsd:duration", "@value": "P1M"},
        )
        result = query.to_dict()
        assert result["@type"] == "DateDuration"
        assert result["start"] == {"@type": "Value", "variable": "s"}

    def test_all_ground(self):
        """All three as typed literals (validation mode)."""
        query = WOQLQuery().date_duration(
            {"@type": "xsd:date", "@value": "2024-01-01"},
            {"@type": "xsd:date", "@value": "2024-04-01"},
            {"@type": "xsd:duration", "@value": "P91D"},
        )
        result = query.to_dict()
        assert result["@type"] == "DateDuration"
        assert result["start"]["@type"] == "Value"
        assert result["end"]["@type"] == "Value"
        assert result["duration"]["@type"] == "Value"

    def test_raises_on_none_start(self):
        """Raises ValueError when start is None."""
        import pytest

        with pytest.raises(ValueError, match="DateDuration takes three parameters"):
            WOQLQuery().date_duration(None, "v:e", "v:d")

    def test_raises_on_none_end(self):
        """Raises ValueError when end is None."""
        import pytest

        with pytest.raises(ValueError, match="DateDuration takes three parameters"):
            WOQLQuery().date_duration("v:s", None, "v:d")

    def test_raises_on_none_duration(self):
        """Raises ValueError when duration is None."""
        import pytest

        with pytest.raises(ValueError, match="DateDuration takes three parameters"):
            WOQLQuery().date_duration("v:s", "v:e", None)
