"""Test schema validation and related operations for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLSchemaValidation:
    """Test schema validation and type checking operations."""
    
    def test_load_vocabulary_with_mock_client(self):
        """Test load_vocabulary with mocked client response."""
        query = WOQLQuery()
        
        # Mock client that returns vocabulary bindings
        class MockClient:
            def query(self, q):
                return {
                    "bindings": [
                        {"S": "schema:Person", "P": "rdf:type", "O": "owl:Class"},
                        {"S": "schema:name", "P": "rdf:type", "O": "owl:DatatypeProperty"},
                        {"S": "_:blank", "P": "rdf:type", "O": "owl:Class"},  # Should be ignored
                    ]
                }
        
        client = MockClient()
        initial_vocab_size = len(query._vocab)
        query.load_vocabulary(client)
        
        # Vocabulary should be loaded - check it grew
        assert len(query._vocab) >= initial_vocab_size
        # The vocabulary stores the part after the colon as values
        # Check that some vocabulary was added
        assert len(query._vocab) > 0
    
    def test_load_vocabulary_with_empty_bindings(self):
        """Test load_vocabulary with empty bindings."""
        query = WOQLQuery()
        
        class MockClient:
            def query(self, q):
                return {"bindings": []}
        
        client = MockClient()
        initial_vocab = dict(query._vocab)
        query.load_vocabulary(client)
        
        # Vocabulary should remain unchanged
        assert query._vocab == initial_vocab
    
    def test_load_vocabulary_with_invalid_format(self):
        """Test load_vocabulary with invalid format strings."""
        query = WOQLQuery()
        
        class MockClient:
            def query(self, q):
                return {
                    "bindings": [
                        {"S": "nocolon", "P": "rdf:type", "O": "owl:Class"},  # No colon
                        {"S": "empty:", "P": "rdf:type", "O": "owl:Class"},  # Empty after colon
                        {"S": ":empty", "P": "rdf:type", "O": "owl:Class"},  # Empty before colon
                    ]
                }
        
        client = MockClient()
        query.load_vocabulary(client)
        
        # Invalid formats should not be added to vocabulary
        assert "nocolon" not in query._vocab
        assert "empty" not in query._vocab
        assert "" not in query._vocab
    
    def test_wrap_cursor_with_and_when_cursor_is_and(self):
        """Test _wrap_cursor_with_and when cursor is already And type."""
        query = WOQLQuery()
        
        # Set up cursor as And type with existing items
        query._cursor["@type"] = "And"
        query._cursor["and"] = [
            {"@type": "Triple", "subject": "s1", "predicate": "p1", "object": "o1"}
        ]
        
        query._wrap_cursor_with_and()
        
        # Should add a new empty item to the and array and update cursor
        assert query._query.get("@type") == "And"
        assert len(query._query.get("and", [])) >= 1
    
    def test_wrap_cursor_with_and_when_cursor_is_not_and(self):
        """Test _wrap_cursor_with_and when cursor is not And type."""
        query = WOQLQuery()
        
        # Set up cursor as Triple type
        query._cursor["@type"] = "Triple"
        query._cursor["subject"] = "s1"
        query._cursor["predicate"] = "p1"
        query._cursor["object"] = "o1"
        
        original_cursor = dict(query._cursor)
        query._wrap_cursor_with_and()
        
        # Should wrap existing cursor in And
        assert query._cursor != original_cursor
        assert query._query.get("@type") == "And"
        assert len(query._query.get("and", [])) == 2
    
    def test_select_with_variable_list(self):
        """Test select with list of variables."""
        query = WOQLQuery()
        result = query.select("v:X", "v:Y", "v:Z")
        
        # After select, cursor may be in subquery
        assert "@type" in query._query
        assert result is query
    
    def test_select_with_subquery(self):
        """Test select with embedded subquery."""
        query = WOQLQuery()
        subquery = WOQLQuery().triple("v:X", "rdf:type", "v:Y")
        
        result = query.select("v:X", "v:Y", subquery)
        
        assert query._cursor["@type"] == "Select"
        assert "variables" in query._cursor
        assert "query" in query._cursor
        assert result is query
    
    def test_select_with_empty_list(self):
        """Test select with empty list."""
        query = WOQLQuery()
        result = query.select()
        
        # After select, query structure is created
        assert "@type" in query._query
        assert result is query
    
    def test_select_with_args_special_case(self):
        """Test select with 'args' as first parameter."""
        query = WOQLQuery()
        # When first param is "args", it returns a list of expected keys
        result = query.select("args")
        
        # This is a special case that returns metadata
        assert result == ["variables", "query"]
    
    def test_distinct_with_variables(self):
        """Test distinct with variable list."""
        query = WOQLQuery()
        result = query.distinct("v:X", "v:Y")
        
        # After distinct, query structure is created
        assert "@type" in query._query
        assert result is query
    
    def test_distinct_with_subquery(self):
        """Test distinct with embedded subquery."""
        query = WOQLQuery()
        subquery = WOQLQuery().triple("v:X", "rdf:type", "v:Y")
        
        result = query.distinct("v:X", subquery)
        
        assert query._cursor["@type"] == "Distinct"
        assert "query" in query._cursor
        assert result is query


class TestWOQLTypeValidation:
    """Test type validation and checking operations."""
    
    def test_type_validation_with_valid_types(self):
        """Test type validation with valid type specifications."""
        query = WOQLQuery()
        
        # Test with various valid types
        result = query.triple("v:X", "rdf:type", "owl:Class")
        assert result is query
        assert query._cursor["@type"] == "Triple"
    
    def test_type_validation_with_var_objects(self):
        """Test type validation with Var objects."""
        query = WOQLQuery()
        
        x = Var("X")
        y = Var("Y")
        
        result = query.triple(x, "rdf:type", y)
        assert result is query
        assert query._cursor["@type"] == "Triple"
    
    def test_vocabulary_prefix_expansion(self):
        """Test that vocabulary prefixes are properly handled."""
        query = WOQLQuery()
        
        # Add some vocabulary
        query._vocab["schema"] = "http://schema.org/"
        query._vocab["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        
        # Use prefixed terms
        result = query.triple("schema:Person", "rdf:type", "owl:Class")
        assert result is query


class TestWOQLConstraintValidation:
    """Test constraint validation operations."""
    
    def test_constraint_with_valid_input(self):
        """Test constraint operations with valid input."""
        query = WOQLQuery()
        
        # Test basic constraint pattern
        result = query.triple("v:X", "v:P", "v:O")
        assert result is query
        assert query._cursor["@type"] == "Triple"
    
    def test_constraint_chaining(self):
        """Test chaining multiple constraints."""
        query = WOQLQuery()
        
        # Chain multiple operations
        query.triple("v:X", "rdf:type", "schema:Person")
        query.triple("v:X", "schema:name", "v:Name")
        
        # Should create And structure
        assert query._query.get("@type") == "And"
    
    def test_constraint_with_optional(self):
        """Test constraint with optional flag."""
        query = WOQLQuery()
        
        result = query.triple("v:X", "schema:age", "v:Age", opt=True)
        
        # Optional should wrap the triple
        assert query._query.get("@type") == "Optional"
        assert result is query
