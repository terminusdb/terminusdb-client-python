"""Unit tests for WOQLQuery.interval_relation_typed JSON serialization."""

from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestIntervalRelationTypedSerialization:
    """Tests that interval_relation_typed produces the correct WOQL JSON AST."""

    def test_all_variables(self):
        """All three arguments as variables."""
        query = WOQLQuery().interval_relation_typed("v:rel", "v:x", "v:y")
        expected = {
            "@type": "IntervalRelationTyped",
            "relation": {"@type": "Value", "variable": "rel"},
            "x": {"@type": "Value", "variable": "x"},
            "y": {"@type": "Value", "variable": "y"},
        }
        assert query.to_dict() == expected

    def test_relation_ground_intervals_variable(self):
        """Relation as typed literal, intervals as variables."""
        query = WOQLQuery().interval_relation_typed(
            {"@type": "xsd:string", "@value": "meets"}, "v:x", "v:y"
        )
        result = query.to_dict()
        assert result["@type"] == "IntervalRelationTyped"
        assert result["x"] == {"@type": "Value", "variable": "x"}
        assert result["y"] == {"@type": "Value", "variable": "y"}

    def test_all_ground(self):
        """All three as typed literals (validation mode)."""
        query = WOQLQuery().interval_relation_typed(
            {"@type": "xsd:string", "@value": "meets"},
            {"@type": "xdd:dateTimeInterval", "@value": "2024-01-01/2024-04-01"},
            {"@type": "xdd:dateTimeInterval", "@value": "2024-04-01/2024-07-01"},
        )
        result = query.to_dict()
        assert result["@type"] == "IntervalRelationTyped"
        assert result["relation"]["@type"] == "Value"
        assert result["x"]["@type"] == "Value"
        assert result["y"]["@type"] == "Value"

    def test_raises_on_none_relation(self):
        """Raises ValueError when relation is None."""
        import pytest
        with pytest.raises(ValueError, match="IntervalRelationTyped takes three parameters"):
            WOQLQuery().interval_relation_typed(None, "v:x", "v:y")

    def test_raises_on_none_x(self):
        """Raises ValueError when x is None."""
        import pytest
        with pytest.raises(ValueError, match="IntervalRelationTyped takes three parameters"):
            WOQLQuery().interval_relation_typed("v:rel", None, "v:y")

    def test_raises_on_none_y(self):
        """Raises ValueError when y is None."""
        import pytest
        with pytest.raises(ValueError, match="IntervalRelationTyped takes three parameters"):
            WOQLQuery().interval_relation_typed("v:rel", "v:x", None)
