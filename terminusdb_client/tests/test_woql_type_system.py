"""Test type system operations for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLTypeConversion:
    """Test type conversion operations."""

    def test_get_with_as_vars_having_to_dict(self):
        """Test get method with as_vars having to_dict to cover line 1444-1445."""
        query = WOQLQuery()

        # Create object with to_dict method
        as_vars = WOQLQuery().woql_as("v:X", "col1")

        result = query.get(as_vars)

        assert result is query
        assert query._query.get("@type") == "Get"
        assert "columns" in query._query

    def test_get_with_plain_as_vars(self):
        """Test get method with plain as_vars to cover line 1446-1447."""
        query = WOQLQuery()

        # Pass plain variables (no to_dict method)
        result = query.get(["v:X", "v:Y"])

        assert result is query
        assert query._query.get("@type") == "Get"

    def test_get_with_query_resource(self):
        """Test get method with query_resource to cover line 1448-1449."""
        query = WOQLQuery()

        resource = {"url": "http://example.com/data"}
        result = query.get(["v:X"], resource)

        assert result is query
        assert "resource" in query._query

    def test_get_without_query_resource(self):
        """Test get method without query_resource to cover line 1450-1452."""
        query = WOQLQuery()

        result = query.get(["v:X"])

        assert result is query
        # Should have empty resource
        assert "resource" in query._query

    def test_get_with_args_special_case(self):
        """Test get with 'args' as first parameter."""
        query = WOQLQuery()

        # When first param is "args", returns metadata
        result = query.get("args")

        assert result == ["columns", "resource"]

    def test_put_with_existing_cursor(self):
        """Test put method with existing cursor to cover line 1459-1460."""
        query = WOQLQuery()

        # Set up existing cursor
        query._cursor["@type"] = "Triple"

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.put(["v:X"], subquery)

        assert result is query
        # Should wrap with And
        assert query._query.get("@type") == "And"

    def test_put_with_as_vars_having_to_dict(self):
        """Test put method with as_vars having to_dict to cover line 1462-1463."""
        query = WOQLQuery()

        as_vars = WOQLQuery().woql_as("v:X", "col1")
        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")

        result = query.put(as_vars, subquery)

        assert result is query
        assert query._cursor.get("@type") == "Put"

    def test_put_with_plain_as_vars(self):
        """Test put method with plain as_vars to cover line 1464-1465."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query.put(["v:X", "v:Y"], subquery)

        assert result is query
        assert query._cursor.get("@type") == "Put"

    def test_put_with_query_resource(self):
        """Test put method with query_resource to cover line 1467-1468."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        resource = {"url": "http://example.com/data"}

        result = query.put(["v:X"], subquery, resource)

        assert result is query
        assert "resource" in query._cursor

    def test_put_with_args_special_case(self):
        """Test put with 'args' as first parameter."""
        query = WOQLQuery()

        # When first param is "args", returns metadata
        result = query.put("args", None)

        assert result == ["columns", "query", "resource"]


class TestWOQLTypeInference:
    """Test type inference operations."""

    def test_typecast_basic(self):
        """Test basic typecast operation."""
        query = WOQLQuery()

        result = query.typecast("v:Value", "xsd:integer", "v:Result")

        assert result is query

    def test_typecast_with_literal_type(self):
        """Test typecast with literal type parameter."""
        query = WOQLQuery()

        result = query.typecast("v:Value", "xsd:string", "v:Result", "en")

        assert result is query

    def test_cast_operation(self):
        """Test cast operation."""
        query = WOQLQuery()

        result = query.cast("v:Value", "xsd:decimal", "v:Result")

        assert result is query


class TestWOQLCustomTypes:
    """Test custom type operations."""

    def test_isa_type_check(self):
        """Test isa type checking."""
        query = WOQLQuery()

        result = query.isa("v:X", "schema:Person")

        assert result is query

    def test_isa_with_variable(self):
        """Test isa with variable type."""
        query = WOQLQuery()

        result = query.isa("v:X", "v:Type")

        assert result is query


class TestWOQLTypeValidation:
    """Test type validation operations."""

    def test_typeof_operation(self):
        """Test type_of operation."""
        query = WOQLQuery()

        result = query.type_of("v:Value", "v:Type")

        assert result is query

    def test_type_checking_with_literals(self):
        """Test type checking with literal values."""
        query = WOQLQuery()

        # Check type of literal
        result = query.type_of(42, "v:Type")

        assert result is query

    def test_type_checking_with_variables(self):
        """Test type checking with variables."""
        query = WOQLQuery()

        var = Var("Value")
        result = query.type_of(var, "v:Type")

        assert result is query


class TestWOQLDataTypes:
    """Test data type operations."""

    def test_string_type_conversion(self):
        """Test string type conversion."""
        query = WOQLQuery()

        # string() returns a dict, not WOQLQuery
        result = query.string("test_string")

        assert isinstance(result, dict)
        assert result["@type"] == "xsd:string"
        assert result["@value"] == "test_string"

    def test_number_type_conversion(self):
        """Test number type conversion."""
        query = WOQLQuery()

        result = query.typecast(42, "xsd:integer", "v:Result")

        assert result is query

    def test_boolean_type_conversion(self):
        """Test boolean type conversion."""
        query = WOQLQuery()

        result = query.typecast(True, "xsd:boolean", "v:Result")

        assert result is query

    def test_datetime_type_conversion(self):
        """Test datetime type conversion."""
        query = WOQLQuery()

        result = query.typecast("2024-01-01", "xsd:dateTime", "v:Result")

        assert result is query


class TestWOQLTypeCoercion:
    """Test type coercion operations."""

    def test_coerce_to_dict_with_dict(self):
        """Test _coerce_to_dict with dictionary input."""
        query = WOQLQuery()

        test_dict = {"@type": "Triple", "subject": "s"}
        result = query._coerce_to_dict(test_dict)

        assert result == test_dict

    def test_coerce_to_dict_with_query(self):
        """Test _coerce_to_dict with WOQLQuery input."""
        query = WOQLQuery()

        subquery = WOQLQuery().triple("v:S", "v:P", "v:O")
        result = query._coerce_to_dict(subquery)

        assert isinstance(result, dict)
        assert "@type" in result

    def test_coerce_to_dict_with_string(self):
        """Test _coerce_to_dict with string input."""
        query = WOQLQuery()

        result = query._coerce_to_dict("test_string")

        # Should handle string appropriately
        assert result is not None


class TestWOQLTypeSystem:
    """Test type system integration."""

    def test_type_system_with_schema(self):
        """Test type system integration with schema."""
        query = WOQLQuery()

        # Define a type in schema
        result = query.triple("schema:Person", "rdf:type", "owl:Class")

        assert result is query
        assert query._cursor.get("@type") == "Triple"

    def test_type_system_with_properties(self):
        """Test type system with property definitions."""
        query = WOQLQuery()

        # Define a property with domain/range
        result = query.triple("schema:name", "rdf:type", "owl:DatatypeProperty")

        assert result is query

    def test_type_system_with_constraints(self):
        """Test type system with constraints."""
        query = WOQLQuery()

        # Add type constraint
        result = query.triple("v:X", "rdf:type", "schema:Person")

        assert result is query


class TestWOQLTypeEdgeCases:
    """Test edge cases in type system."""

    def test_type_with_null_value(self):
        """Test type operations with null values."""
        query = WOQLQuery()

        # Test with None
        result = query.typecast(None, "xsd:string", "v:Result")

        assert result is query

    def test_type_with_empty_string(self):
        """Test type operations with empty string."""
        query = WOQLQuery()

        result = query.string("")

        assert isinstance(result, dict)
        assert result["@type"] == "xsd:string"
        assert result["@value"] == ""

    def test_type_with_special_characters(self):
        """Test type operations with special characters."""
        query = WOQLQuery()

        result = query.string("test@#$%")

        assert isinstance(result, dict)
        assert result["@type"] == "xsd:string"
        assert result["@value"] == "test@#$%"

    def test_type_with_unicode(self):
        """Test type operations with unicode."""
        query = WOQLQuery()

        result = query.string("测试")

        assert isinstance(result, dict)
        assert result["@type"] == "xsd:string"
        assert result["@value"] == "测试"


class TestWOQLTypeCompatibility:
    """Test type compatibility operations."""

    def test_compatible_types(self):
        """Test operations with compatible types."""
        query = WOQLQuery()

        # Integer to decimal should be compatible
        result = query.typecast("42", "xsd:decimal", "v:Result")

        assert result is query

    def test_incompatible_types(self):
        """Test operations with potentially incompatible types."""
        query = WOQLQuery()

        # String to integer might fail at runtime
        result = query.typecast("not_a_number", "xsd:integer", "v:Result")

        assert result is query

    def test_type_hierarchy(self):
        """Test type hierarchy operations."""
        query = WOQLQuery()

        # Test subclass relationships
        result = query.sub("schema:Employee", "schema:Person")

        assert result is query
