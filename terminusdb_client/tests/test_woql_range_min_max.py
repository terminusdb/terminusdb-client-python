"""Unit tests for WOQLQuery.range_min and range_max JSON serialization."""

import pytest

from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestRangeMinSerialization:
    """Tests that range_min produces the correct WOQL JSON AST."""

    def test_variable_result(self):
        """List and variable result."""
        query = WOQLQuery().range_min("v:list", "v:m")
        expected = {
            "@type": "RangeMin",
            "list": {"@type": "Value", "variable": "list"},
            "result": {"@type": "Value", "variable": "m"},
        }
        assert query.to_dict() == expected

    def test_raises_on_none_list(self):
        """Raises ValueError when list is None."""
        with pytest.raises(ValueError, match="RangeMin takes two parameters"):
            WOQLQuery().range_min(None, "v:m")

    def test_raises_on_none_result(self):
        """Raises ValueError when result is None."""
        with pytest.raises(ValueError, match="RangeMin takes two parameters"):
            WOQLQuery().range_min("v:list", None)


class TestRangeMaxSerialization:
    """Tests that range_max produces the correct WOQL JSON AST."""

    def test_variable_result(self):
        """List and variable result."""
        query = WOQLQuery().range_max("v:list", "v:m")
        expected = {
            "@type": "RangeMax",
            "list": {"@type": "Value", "variable": "list"},
            "result": {"@type": "Value", "variable": "m"},
        }
        assert query.to_dict() == expected

    def test_raises_on_none_list(self):
        """Raises ValueError when list is None."""
        with pytest.raises(ValueError, match="RangeMax takes two parameters"):
            WOQLQuery().range_max(None, "v:m")

    def test_raises_on_none_result(self):
        """Raises ValueError when result is None."""
        with pytest.raises(ValueError, match="RangeMax takes two parameters"):
            WOQLQuery().range_max("v:list", None)
