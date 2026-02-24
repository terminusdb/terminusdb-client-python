"""
Integration tests for WOQL select() with empty variable list

Tests that select() with no arguments is valid and works correctly.
This is needed for patterns like localize() where we want to hide
all inner variables while still executing the inner query.
"""

import pytest

from terminusdb_client import Client
from terminusdb_client.woqlquery.woql_query import WOQLQuery


@pytest.fixture(scope="module")
def select_empty_db(docker_url):
    """Create a client and test database for select empty tests."""
    client = Client(docker_url)
    client.connect()

    db_name = "db__test_select_empty"

    # Create test database if it doesn't exist
    if db_name not in client.list_databases():
        client.create_database(db_name)
    else:
        client.connect(db=db_name)

    yield client

    # Cleanup
    try:
        client.delete_database(db_name, "admin")
    except Exception:
        pass


class TestWOQLSelectEmpty:
    """Integration tests for WOQL select() with empty variable list."""

    @pytest.fixture(autouse=True)
    def setup(self, select_empty_db):
        """Setup client reference for each test."""
        self.client = select_empty_db

    def test_select_no_args_returns_empty_bindings(self):
        """select() with no arguments should be valid and return empty bindings."""
        # select() with no arguments should:
        # 1. Be valid syntax (not throw client-side error)
        # 2. Execute successfully on server
        # 3. Return bindings with no variables (empty dicts)

        query = WOQLQuery().select(WOQLQuery().eq("v:X", WOQLQuery().string("test")))

        result = self.client.query(query)

        assert result is not None
        assert "bindings" in result
        assert len(result["bindings"]) == 1

        # The binding should be empty since select() hides all variables
        binding = result["bindings"][0]
        assert len(binding) == 0

    def test_select_hides_inner_variables_outer_visible(self):
        """select() should hide inner variables while outer variables remain visible."""
        # Pattern: outer variable is visible, inner variables are hidden by select()
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:Outer", WOQLQuery().string("visible")),
            WOQLQuery().select(
                WOQLQuery().woql_and(
                    WOQLQuery().eq("v:Inner", WOQLQuery().string("hidden")),
                    # Use both variables to ensure query executes
                    WOQLQuery().eq("v:Both", "v:Inner"),
                )
            ),
        )

        result = self.client.query(query)

        assert result is not None
        assert "bindings" in result
        assert len(result["bindings"]) == 1

        binding = result["bindings"][0]

        # v:Outer should be visible (defined outside select())
        outer = binding.get("Outer") or binding.get("v:Outer")
        assert outer is not None
        assert outer.get("@value") == "visible"

        # v:Inner and v:Both should NOT be visible (inside select())
        assert binding.get("Inner") is None
        assert binding.get("v:Inner") is None
        assert binding.get("Both") is None
        assert binding.get("v:Both") is None

    def test_select_allows_outer_binding_through_unification(self):
        """select() should hide inner variables but allow outer variables to be bound."""
        # Pattern: outer variable is visible and gets value through unification
        query = WOQLQuery().woql_and(
            WOQLQuery().eq("v:Outer", "v:Outer"),
            WOQLQuery().select(
                WOQLQuery().woql_and(
                    WOQLQuery().eq("v:Inner", WOQLQuery().string("hidden")),
                    WOQLQuery().eq(
                        "v:Inner_Shared_Value", WOQLQuery().string("visible")
                    ),
                    # Use both variables to ensure query executes
                    WOQLQuery().eq("v:Outer", "v:Inner_Shared_Value"),
                )
            ),
        )

        result = self.client.query(query)

        assert result is not None
        assert "bindings" in result
        assert len(result["bindings"]) == 1

        binding = result["bindings"][0]

        # v:Outer should be visible (defined outside select())
        outer = binding.get("Outer") or binding.get("v:Outer")
        assert outer is not None
        assert outer.get("@value") == "visible"

        # v:Inner should NOT be visible (inside select())
        assert binding.get("Inner") is None
        assert binding.get("v:Inner") is None

    def test_select_generated_json_has_empty_variables_array(self):
        """select() with no variables should generate JSON with empty variables array."""
        # Verify the WOQL builder generates correct JSON with empty variables array
        query = WOQLQuery().select(WOQLQuery().eq("v:X", WOQLQuery().string("test")))

        json_query = query.to_dict()

        assert json_query["@type"] == "Select"
        assert "variables" in json_query
        assert isinstance(json_query["variables"], list)
        assert len(json_query["variables"]) == 0

    def test_two_localized_blocks_bind_same_variable_name_different_values(self):
        """Two localized blocks can bind same variable name to different values."""
        # KEY TEST: Demonstrates select() scope isolation
        # Two separate localized blocks use the same internal variable name (v:temp)
        # but bind it to different values - proving they don't interfere

        localized1, v1 = WOQLQuery().localize(
            {
                "result": "v:result1",
                "temp": None,  # local variable - same name in both blocks
            }
        )

        localized2, v2 = WOQLQuery().localize(
            {
                "result": "v:result2",
                "temp": None,  # local variable - same name, different scope
            }
        )

        query = WOQLQuery().woql_and(
            # First localized block: temp = "first", result1 = temp
            localized1(
                WOQLQuery().woql_and(
                    WOQLQuery().eq(v1.temp, WOQLQuery().string("first")),
                    WOQLQuery().eq(v1.result, v1.temp),
                )
            ),
            # Second localized block: temp = "second", result2 = temp
            localized2(
                WOQLQuery().woql_and(
                    WOQLQuery().eq(v2.temp, WOQLQuery().string("second")),
                    WOQLQuery().eq(v2.result, v2.temp),
                )
            ),
        )

        result = self.client.query(query)

        assert result is not None
        assert "bindings" in result
        assert len(result["bindings"]) == 1

        binding = result["bindings"][0]

        # v:result1 should be "first" (from first localized block)
        result1 = binding.get("result1") or binding.get("v:result1")
        assert result1 is not None
        assert result1.get("@value") == "first"

        # v:result2 should be "second" (from second localized block)
        result2 = binding.get("result2") or binding.get("v:result2")
        assert result2 is not None
        assert result2.get("@value") == "second"

        # The temp variables should NOT be visible (they're local)
        assert binding.get("temp") is None
        assert binding.get("v:temp") is None

    def test_localize_pattern_hides_local_exposes_outer(self):
        """localize pattern: select() hides local variables, eq() exposes outer params."""
        # This is the real use case: localize() pattern
        # - Outer parameters are bound via eq() OUTSIDE select()
        # - Local variables are hidden by select()

        # Simulate what localize() should do with select() (not select(''))
        outer_param = "v:param_unique_123"
        local_var = "v:local_unique_456"

        query = WOQLQuery().woql_and(
            # Outer eq() bindings - these should be visible
            WOQLQuery().eq("v:MyParam", outer_param),
            # select() with no args - hides everything inside
            WOQLQuery().select(
                WOQLQuery().woql_and(
                    # Bind the unique param to a value
                    WOQLQuery().eq(outer_param, WOQLQuery().string("param_value")),
                    # Use a local variable (should be hidden)
                    WOQLQuery().eq(local_var, WOQLQuery().string("local_value")),
                )
            ),
        )

        result = self.client.query(query)

        assert result is not None
        assert "bindings" in result
        assert len(result["bindings"]) == 1

        binding = result["bindings"][0]

        # v:MyParam should be visible (eq() is outside select())
        # and unified with outer_param which was bound inside
        my_param = binding.get("MyParam") or binding.get("v:MyParam")
        assert my_param is not None
        assert my_param.get("@value") == "param_value"
