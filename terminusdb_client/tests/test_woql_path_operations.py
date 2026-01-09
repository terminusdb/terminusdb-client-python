"""Test path operations for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLPathOperations:
    """Test path-related operations and utilities."""
    

    
    def test_clean_subject_with_var(self):
        """Test _clean_subject with Var object."""
        query = WOQLQuery()
        var = Var("subject")
        result = query._clean_subject(var)
        assert "@type" in result
        assert result["variable"] == "subject"
    
    def test_clean_subject_with_plain_string(self):
        """Test _clean_subject with plain string (no colon, not in vocab)."""
        query = WOQLQuery()
        result = query._clean_subject("plain_string")
        # Should be expanded as node variable
        assert isinstance(result, dict)
    
    def test_clean_predicate_with_dict(self):
        """Test _clean_predicate with dictionary input."""
        query = WOQLQuery()
        test_dict = {"@id": "test_predicate"}
        result = query._clean_predicate(test_dict)
        assert result == test_dict
    
    def test_clean_predicate_with_var(self):
        """Test _clean_predicate with Var object."""
        query = WOQLQuery()
        var = Var("predicate")
        result = query._clean_predicate(var)
        assert "@type" in result
        assert result["variable"] == "predicate"
    
    def test_clean_predicate_with_plain_string(self):
        """Test _clean_predicate with plain string."""
        query = WOQLQuery()
        result = query._clean_predicate("plain_predicate")
        # Should be expanded as node variable
        assert isinstance(result, dict)
    
    def test_clean_predicate_error(self):
        """Test _clean_predicate raises ValueError for invalid input."""
        query = WOQLQuery()
        with pytest.raises(ValueError, match="Predicate must be a URI string"):
            query._clean_predicate(123)
    
    def test_clean_path_predicate_with_iri(self):
        """Test _clean_path_predicate with IRI string."""
        query = WOQLQuery()
        result = query._clean_path_predicate("http://example.org/predicate")
        assert result == "http://example.org/predicate"
    
    def test_clean_path_predicate_with_vocab_key(self):
        """Test _clean_path_predicate with vocabulary key."""
        query = WOQLQuery()
        result = query._clean_path_predicate("type")
        assert result == "rdf:type"
    
    def test_clean_path_predicate_with_plain_string(self):
        """Test _clean_path_predicate with plain string."""
        query = WOQLQuery()
        result = query._clean_path_predicate("unknown")
        assert result == "unknown"
    
    def test_clean_path_predicate_with_none(self):
        """Test _clean_path_predicate with None."""
        query = WOQLQuery()
        result = query._clean_path_predicate(None)
        assert result is False
    
    def test_added_triple_with_optional(self):
        """Test added_triple with optional flag."""
        query = WOQLQuery()
        query.added_triple("s", "p", "o", opt=True)
        # When opt=True, it wraps with Optional but creates a Triple inside
        assert query._query.get("@type") == "Optional"
        assert "Triple" in str(query._query)  # The inner query is Triple, not AddedTriple
        assert "subject" in query._cursor
        assert "predicate" in query._cursor
        assert "object" in query._cursor
    
    def test_added_triple_without_optional(self):
        """Test added_triple without optional flag."""
        query = WOQLQuery()
        result = query.added_triple("s", "p", "o")
        assert query._cursor["@type"] == "AddedTriple"
        assert "subject" in query._cursor
        assert "predicate" in query._cursor
        assert "object" in query._cursor
        assert result is query
    
    def test_added_triple_with_existing_cursor(self):
        """Test added_triple with existing cursor type."""
        query = WOQLQuery()
        query._cursor["@type"] = "Triple"
        query.added_triple("s", "p", "o")
        # Should wrap with and
        assert query._query.get("@type") == "And"
    
    def test_removed_triple_with_optional(self):
        """Test removed_triple with optional flag."""
        query = WOQLQuery()
        query.removed_triple("s", "p", "o", opt=True)
        # When opt=True, it wraps with Optional but creates a Triple inside
        assert query._query.get("@type") == "Optional"
        assert "Triple" in str(query._query)  # The inner query is Triple, not RemovedTriple
        assert "subject" in query._cursor
        assert "predicate" in query._cursor
        assert "object" in query._cursor
    
    def test_removed_triple_without_optional(self):
        """Test removed_triple without optional flag."""
        query = WOQLQuery()
        result = query.removed_triple("s", "p", "o")
        assert query._cursor["@type"] == "DeletedTriple"
        assert "subject" in query._cursor
        assert "predicate" in query._cursor
        assert "object" in query._cursor
        assert result is query
    
    def test_quad_with_optional(self):
        """Test quad with optional flag."""
        query = WOQLQuery()
        query.quad("s", "p", "o", "g", opt=True)
        # When opt=True, it wraps with Optional but creates a Triple inside
        assert query._query.get("@type") == "Optional"
        assert "Triple" in str(query._query)  # The inner query is Triple, not Quad
        assert "graph" in query._cursor
    
    def test_quad_without_optional(self):
        """Test quad without optional flag."""
        query = WOQLQuery()
        result = query.quad("s", "p", "o", "g")
        # When opt=False, it creates Triple with graph
        assert query._cursor["@type"] == "Triple"
        assert "graph" in query._cursor
        assert result is query
    
    def test_quad_with_no_graph_raises_error(self):
        """Test quad raises error when graph is None or empty."""
        query = WOQLQuery()
        with pytest.raises(ValueError, match="Quad takes four parameters"):
            query.quad("s", "p", "o", None)
        with pytest.raises(ValueError, match="Quad takes four parameters"):
            query.quad("s", "p", "o", "")
    
    def test_quad_with_existing_cursor(self):
        """Test quad with existing cursor type."""
        query = WOQLQuery()
        query._cursor["@type"] = "Triple"
        query.quad("s", "p", "o", "g")
        # Should wrap with and
        assert query._query.get("@type") == "And"
    
    @pytest.mark.skip(reason="Not implemented - args introspection feature disabled in JS client")
    def test_quad_with_special_args_subject(self):
        """Test quad with 'args' parameter for introspection.
        
        When 'args' is passed as the first parameter, methods should return
        a list of parameter names for API introspection.
        
        Note: JavaScript client has this feature commented out entirely.
        This test shows what the correct behavior should be if the feature
        were properly implemented. `quad()`, `added_triple()` and 
        `removed_quad()` do not implement this. Seems like an early
        experiment.
        
        The implementation should probably look something like this in 
        WOQLQuery:
        
        if sub and sub == "args":
            return ["subject", "predicate", "object", "graph"]
        
        """
        query = WOQLQuery()
        
        # Should return list of parameter names for API introspection
        result = query.quad("args", None, None, None)
        
        assert result == ["subject", "predicate", "object", "graph"]
    
    def test_added_quad_with_optional(self):
        """Test added_quad with optional flag."""
        query = WOQLQuery()
        query.added_quad("s", "p", "o", "g", opt=True)
        # When opt=True, it wraps with Optional but creates a Triple inside
        assert query._query.get("@type") == "Optional"
        assert "Triple" in str(query._query)  # The inner query is Triple, not AddedQuad
        assert "graph" in query._cursor
    
    def test_added_quad_without_optional(self):
        """Test added_quad without optional flag."""
        query = WOQLQuery()
        result = query.added_quad("s", "p", "o", "g")
        # When opt=False, it creates AddedTriple (not Triple)
        assert query._cursor["@type"] == "AddedTriple"
        assert "graph" in query._cursor
        assert result is query
    
    def test_path_composition(self):
        """Test complex path composition scenarios."""
        query = WOQLQuery()
        # Test multiple path operations
        query.triple(Var("s"), "predicate", Var("o"))
        query.added_triple("s2", "p2", "o2")
        query.removed_triple("s3", "p3", "o3")
        
        # Should have wrapped with and
        assert query._query.get("@type") == "And"
        assert len(query._query.get("and", [])) >= 2
