"""
Unit tests for WOQL localize() - verifying JSON structure only.
These tests do NOT connect to a database - they only verify the generated WOQL JSON.

These tests align with the JavaScript client's woqlLocalize.spec.js tests.
"""

from terminusdb_client.woqlquery import (
    WOQLQuery,
    Var,
    VarsUnique,
    _reset_unique_var_counter,
)


class TestWOQLLocalize:
    """Test suite for WOQL localize() method."""

    def setup_method(self):
        """Reset unique var counter before each test for predictable names."""
        _reset_unique_var_counter(0)

    def test_hide_local_variables_from_outer_scope(self):
        """Should hide local variables from outer scope (basic test)."""
        (localized, v) = WOQLQuery().localize(
            {
                "local_only": None,
            }
        )
        query = WOQLQuery().woql_and(
            WOQLQuery().triple("v:x", "v:y", "v:z"),
            localized(
                WOQLQuery().triple(v.local_only, "knows", "v:someone"),
            ),
        )

        result = query.to_dict()

        # Check that query has proper structure
        assert result["@type"] == "And"
        assert isinstance(result["and"], list)
        # Second element should be Select
        assert result["and"][1]["@type"] == "Select"
        assert isinstance(result["and"][1]["variables"], list)

        # CRITICAL: select("") creates variables:[] to hide all local variables
        assert result["and"][1]["variables"] == []

    def test_bind_outer_parameters_via_eq(self):
        """Should bind outer parameters via eq() clauses."""
        (localized, v) = WOQLQuery().localize(
            {
                "param1": "v:input1",
                "param2": "v:input2",
                "local": None,
            }
        )

        query = localized(
            WOQLQuery().triple(v.param1, "knows", v.param2),
        )

        result = query.to_dict()

        # Structure: And with eq bindings + Select wrapper
        assert result["@type"] == "And"
        and_clauses = result["and"]

        # Should have eq bindings before the select
        eq_count = sum(1 for c in and_clauses if c.get("@type") == "Equals")
        assert eq_count >= 2  # At least 2 eq bindings for 2 outer params

        # Last element should be Select
        select_clauses = [c for c in and_clauses if c.get("@type") == "Select"]
        assert len(select_clauses) >= 1

    def test_functional_mode(self):
        """Should work in functional mode."""
        (localized, v) = WOQLQuery().localize(
            {
                "x": "v:external_x",
                "temp": None,
            }
        )

        query = localized(
            WOQLQuery().woql_and(
                WOQLQuery().eq(
                    v.temp, {"@type": "xsd:string", "@value": "intermediate"}
                ),
                WOQLQuery().triple(v.x, "knows", v.temp),
            ),
        )

        result = query.to_dict()

        # Structure should be And with eq + Select
        assert result["@type"] == "And"
        and_clauses = result["and"]

        # Should have eq binding for external_x
        eq_count = sum(1 for c in and_clauses if c.get("@type") == "Equals")
        assert eq_count >= 1

        # Should have Select with empty variables
        select_clauses = [c for c in and_clauses if c.get("@type") == "Select"]
        assert len(select_clauses) >= 1
        assert select_clauses[-1]["variables"] == []

    def test_generate_unique_variable_names(self):
        """Should generate unique variable names."""
        _reset_unique_var_counter(0)

        (localized1, v1) = WOQLQuery().localize(
            {
                "var1": None,
            }
        )

        (localized2, v2) = WOQLQuery().localize(
            {
                "var1": None,
            }
        )

        # Variable names should be different between calls
        assert v1.var1.name != v2.var1.name

    def test_handle_only_local_variables(self):
        """Should handle only local variables (no outer bindings)."""
        (localized, v) = WOQLQuery().localize(
            {
                "local1": None,
                "local2": None,
            }
        )

        query = localized(
            WOQLQuery().triple(v.local1, "knows", v.local2),
        )

        result = query.to_dict()

        # With no outer bindings, should be just Select
        assert result["@type"] == "Select"
        assert result["variables"] == []

        # Query should be directly the triple (wrapped in And from select)
        assert result["query"]["@type"] in ["Triple", "And"]

    def test_handle_only_outer_parameters(self):
        """Should handle only outer parameters (no local variables)."""
        (localized, v) = WOQLQuery().localize(
            {
                "param1": "v:input1",
                "param2": "v:input2",
            }
        )

        query = localized(
            WOQLQuery().triple(v.param1, "knows", v.param2),
        )

        result = query.to_dict()
        assert result["@type"] == "And"
        # Should have eq bindings + Select
        assert len(result["and"]) >= 3

    def test_preserve_variable_types(self):
        """Should preserve variable types (Var instances)."""
        (localized, v) = WOQLQuery().localize(
            {
                "input": "v:x",
                "local": None,
            }
        )

        # v.input and v.local should be Var instances
        assert isinstance(v.input, Var)
        assert isinstance(v.local, Var)

    def test_handle_empty_parameter_specification(self):
        """Should handle empty parameter specification."""
        (localized, v) = WOQLQuery().localize({})

        query = localized(
            WOQLQuery().triple("v:s", "v:p", "v:o"),
        )

        result = query.to_dict()
        assert result["@type"] == "Select"
        assert result["variables"] == []

        # No eq bindings, just the query
        assert "query" in result


class TestVarsUnique:
    """Test suite for VarsUnique class."""

    def setup_method(self):
        """Reset unique var counter before each test."""
        _reset_unique_var_counter(0)

    def test_generates_unique_names(self):
        """VarsUnique should generate unique variable names."""
        v1 = VarsUnique("x", "y")
        v2 = VarsUnique("x", "y")

        # Names should have counter suffix
        assert "_" in v1.x.name
        assert "_" in v1.y.name

        # Different calls should have different names
        assert v1.x.name != v2.x.name
        assert v1.y.name != v2.y.name

    def test_counter_increments(self):
        """Counter should increment for each variable."""
        _reset_unique_var_counter(0)
        v = VarsUnique("a", "b", "c")

        # Each variable should have incrementing suffix
        assert v.a.name == "a_1"
        assert v.b.name == "b_2"
        assert v.c.name == "c_3"

    def test_reset_counter(self):
        """Counter reset should work correctly."""
        _reset_unique_var_counter(100)
        v = VarsUnique("test")
        assert v.test.name == "test_101"

    def test_var_instances(self):
        """VarsUnique should create Var instances."""
        v = VarsUnique("foo", "bar")
        assert isinstance(v.foo, Var)
        assert isinstance(v.bar, Var)

    def test_to_dict(self):
        """Var.to_dict should return proper WOQL structure."""
        _reset_unique_var_counter(0)
        v = VarsUnique("myvar")
        result = v.myvar.to_dict()

        assert result == {"@type": "Value", "variable": "myvar_1"}
