"""Test cursor management and state tracking for WOQL Query."""
import datetime as dt
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLCursorManagement:
    """Test cursor positioning, movement, and state management."""

    def test_clean_data_value_with_float_target(self):
        """Test _clean_data_value with float and automatic target detection."""
        query = WOQLQuery()
        result = query._clean_data_value(3.14159)
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:decimal"
        assert abs(result["data"]["@value"] - 3.14159) < 1e-10

    def test_clean_data_value_with_float_explicit_target(self):
        """Test _clean_data_value with float and explicit target type."""
        query = WOQLQuery()
        result = query._clean_data_value(2.71828, target="xsd:float")
        assert result["data"]["@type"] == "xsd:float"
        assert abs(result["data"]["@value"] - 2.71828) < 1e-10

    def test_clean_data_value_with_int_target(self):
        """Test _clean_data_value with integer and automatic target detection."""
        query = WOQLQuery()
        result = query._clean_data_value(42)
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:integer"
        assert result["data"]["@value"] == 42

    def test_clean_data_value_with_int_explicit_target(self):
        """Test _clean_data_value with integer and explicit target type."""
        query = WOQLQuery()
        result = query._clean_data_value(100, target="xsd:long")
        assert result["data"]["@type"] == "xsd:long"
        assert result["data"]["@value"] == 100

    def test_clean_data_value_with_bool_target(self):
        """Test _clean_data_value with boolean and automatic target detection."""
        query = WOQLQuery()
        result = query._clean_data_value(True)
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:boolean"
        assert result["data"]["@value"] is True

    def test_clean_data_value_with_bool_explicit_target(self):
        """Test _clean_data_value with boolean and explicit target type."""
        query = WOQLQuery()
        result = query._clean_data_value(False, target="custom:boolean")
        assert result["data"]["@type"] == "custom:boolean"
        assert result["data"]["@value"] is False

    def test_clean_data_value_with_date_target(self):
        """Test _clean_data_value with date and automatic target detection."""
        query = WOQLQuery()
        test_date = dt.date(2023, 12, 25)
        result = query._clean_data_value(test_date)
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:dateTime"
        assert "2023-12-25" in result["data"]["@value"]

    def test_clean_data_value_with_date_explicit_target(self):
        """Test _clean_data_value with date and explicit target type."""
        query = WOQLQuery()
        test_datetime = dt.datetime(2023, 12, 25, 10, 30, 0)
        result = query._clean_data_value(test_datetime, target="xsd:dateTime")
        assert result["data"]["@type"] == "xsd:dateTime"
        assert "2023-12-25T10:30:00" in result["data"]["@value"]

    def test_clean_data_value_with_dict_value(self):
        """Test _clean_data_value with dict containing @value."""
        query = WOQLQuery()
        value_dict = {"@value": "test", "@type": "xsd:string"}
        result = query._clean_data_value(value_dict)
        assert result["@type"] == "DataValue"
        assert result["data"] == value_dict

    def test_clean_data_value_with_plain_dict(self):
        """Test _clean_data_value with plain dictionary (no @value)."""
        query = WOQLQuery()
        plain_dict = {"key": "value"}
        result = query._clean_data_value(plain_dict)
        assert result == plain_dict

    def test_clean_data_value_with_custom_object(self):
        """Test _clean_data_value with custom object (converts to string)."""
        query = WOQLQuery()

        class CustomData:
            def __str__(self):
                return "custom_data_representation"

        custom_obj = CustomData()
        result = query._clean_data_value(custom_obj)
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:string"
        assert result["data"]["@value"] == "custom_data_representation"

    def test_clean_arithmetic_value_with_string(self):
        """Test _clean_arithmetic_value with string."""
        query = WOQLQuery()
        result = query._clean_arithmetic_value("42")
        assert result["@type"] == "ArithmeticValue"
        assert result["data"]["@type"] == "xsd:string"
        assert result["data"]["@value"] == "42"

    def test_clean_arithmetic_value_with_variable_string(self):
        """Test _clean_arithmetic_value with variable string (v: prefix)."""
        query = WOQLQuery()
        result = query._clean_arithmetic_value("v:variable")
        # Should expand as arithmetic variable
        assert "@type" in result
        assert "variable" in str(result)

    def test_clean_arithmetic_value_with_float(self):
        """Test _clean_arithmetic_value with float value."""
        query = WOQLQuery()
        result = query._clean_arithmetic_value(3.14)
        assert result["@type"] == "ArithmeticValue"
        assert result["data"]["@type"] == "xsd:decimal"
        assert abs(result["data"]["@value"] - 3.14) < 1e-10

    def test_clean_arithmetic_value_with_float_explicit_target(self):
        """Test _clean_arithmetic_value with float and explicit target."""
        query = WOQLQuery()
        result = query._clean_arithmetic_value(2.5, target="xsd:double")
        assert result["data"]["@type"] == "xsd:double"
        assert abs(result["data"]["@value"] - 2.5) < 1e-10

    def test_clean_arithmetic_value_with_int(self):
        """Test _clean_arithmetic_value with integer value."""
        query = WOQLQuery()
        result = query._clean_arithmetic_value(100)
        assert result["@type"] == "ArithmeticValue"
        assert result["data"]["@type"] == "xsd:integer"
        assert result["data"]["@value"] == 100

    def test_clean_arithmetic_value_with_int_explicit_target(self):
        """Test _clean_arithmetic_value with integer and explicit target."""
        query = WOQLQuery()
        result = query._clean_arithmetic_value(50, target="xsd:short")
        assert result["data"]["@type"] == "xsd:short"
        assert result["data"]["@value"] == 50

    def test_cursor_initialization(self):
        """Test cursor is properly initialized."""
        query = WOQLQuery()
        assert query._cursor == query._query
        assert query._cursor is not None

    def test_cursor_movement_after_triple(self):
        """Test that cursor moves to new triple."""
        query = WOQLQuery()
        initial_cursor = query._cursor

        query.triple("s", "p", "o")
        # Cursor should remain at the new triple (same object but modified)
        assert query._cursor is initial_cursor
        assert query._cursor["@type"] == "Triple"

    def test_cursor_state_with_chained_operations(self):
        """Test cursor state through chained operations."""
        query = WOQLQuery()
        query.triple("s1", "p1", "o1")
        first_cursor = query._cursor

        # Use __and__ operator to chain queries
        query2 = WOQLQuery().triple("s2", "p2", "o2")
        combined = query.__and__(query2)

        assert combined._cursor != first_cursor
        assert combined._query.get("and") is not None

    def test_cursor_reset_with_subquery(self):
        """Test cursor behavior with subqueries."""
        query = WOQLQuery()
        query.triple("s", "p", "o")
        query._add_sub_query()
        # Cursor should be reset to new query object
        assert query._cursor == {}
        assert query._cursor is not query._query

    def test_cursor_tracking_with_update_operations(self):
        """Test cursor tracking with update operations."""
        query = WOQLQuery()
        assert query._contains_update is False

        # added_triple is a QUERY operation (finds triples added in commits)
        # It should NOT set _contains_update because it's not writing data
        query.added_triple("s", "p", "o")
        assert query._contains_update is False  # Correct - this is a read operation

        # Cursor should be at the added triple query
        assert query._cursor["@type"] == "AddedTriple"

    def test_nested_cursor_operations(self):
        """Test deeply nested cursor operations."""
        # Create nested structure using __and__ and __or__
        q1 = WOQLQuery().triple("a", "b", "c")
        q2 = WOQLQuery().triple("d", "e", "f")
        q3 = WOQLQuery().triple("g", "h", "i")

        nested = q1.__and__(q2).__or__(q3)

        assert nested._query.get("@type") == "Or"
        assert "and" in nested._query.get("or")[0]  # The 'and' is inside the 'or' structure
        assert "or" in nested._query

    def test_cursor_consistency_after_complex_query(self):
        """Test cursor remains consistent after complex query building."""
        query = WOQLQuery()

        # Build complex query
        query.triple("type", "rdf:type", "owl:Class")
        query.sub("type", "rdfs:subClassOf")  # sub takes only 2 arguments

        # Cursor should be at the last operation
        assert query._cursor["@type"] == "Subsumption"  # SubClassOf maps to Subsumption
        assert query._cursor["parent"]["node"] == "type"  # parent is wrapped as NodeValue
        assert query._cursor["child"]["node"] == "rdfs:subClassOf"  # child is wrapped as NodeValue

        # Overall query structure should be preserved
        assert "@type" in query._query
        assert query._query.get("@type") in ["And", "Triple"]
