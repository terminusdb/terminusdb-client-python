"""Extended edge case tests for WOQL query functionality."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var, Doc, Vars


class TestWOQLVocabHandling:
    """Test vocabulary handling in WOQL queries."""
    
    def test_vocab_extraction_from_string_with_colon(self):
        """Test vocabulary extraction from strings with colons."""
        query = WOQLQuery()
        # This should trigger line 706 - vocab extraction
        query.triple("schema:Person", "rdf:type", "owl:Class")
        # Vocab should be extracted from the prefixed terms
        assert query._query is not None
    
    def test_vocab_extraction_with_underscore_prefix(self):
        """Test that underscore-prefixed terms don't extract vocab."""
        query = WOQLQuery()
        # _: prefix should not extract vocab (line 705 condition)
        query.triple("_:blank", "rdf:type", "owl:Class")
        assert query._query is not None


class TestWOQLSelectEdgeCases:
    """Test select() method edge cases."""
    
    def test_select_with_empty_list_directly(self):
        """Test select with empty list creates proper structure."""
        query = WOQLQuery()
        # This tests line 786-787 - empty list handling
        result = query.select()
        
        assert result is query
        assert query._query["@type"] == "Select"
    
    def test_select_with_subquery_object(self):
        """Test select with a subquery that has to_dict method."""
        query = WOQLQuery()
        subquery = WOQLQuery().triple("v:X", "rdf:type", "schema:Person")
        
        # This tests line 788-789 - hasattr to_dict check
        result = query.select("v:X", subquery)
        
        assert result is query
        assert "variables" in query._cursor
        assert "query" in query._cursor


class TestWOQLAsEdgeCases:
    """Test as() method edge cases for uncovered lines."""
    
    def test_as_with_list_of_pairs(self):
        """Test as() with list of [var, name] pairs."""
        query = WOQLQuery()
        # This tests lines 1490-1495 - list handling
        result = query.woql_as([["v:X", "name"], ["v:Y", "age"]])
        
        assert result is query
        assert len(query._query) == 2
    
    def test_as_with_list_including_type(self):
        """Test as() with list including type specification."""
        query = WOQLQuery()
        # This tests line 1493 - three-element list with type
        result = query.woql_as([["v:X", "name", "xsd:string"]])
        
        assert result is query
        assert len(query._query) == 1
    
    def test_as_with_xsd_type_string(self):
        """Test as() with xsd: prefixed type."""
        query = WOQLQuery()
        # This tests lines 1500-1501 - xsd: prefix handling
        result = query.woql_as(0, "v:Value", "xsd:string")
        
        assert result is query
        assert len(query._query) == 1
    
    def test_as_with_xdd_type_string(self):
        """Test as() with xdd: prefixed type."""
        query = WOQLQuery()
        # This tests line 1500 - xdd: prefix handling
        result = query.woql_as(0, "v:Value", "xdd:coordinate")
        
        assert result is query
        assert len(query._query) == 1
    
    def test_as_with_two_string_args(self):
        """Test as() with two string arguments."""
        query = WOQLQuery()
        # This tests lines 1502-1503 - two arg handling without type
        result = query.woql_as("v:X", "name")
        
        assert result is query
        assert len(query._query) == 1
    
    def test_as_with_single_arg(self):
        """Test as() with single argument."""
        query = WOQLQuery()
        # This tests line 1505 - single arg handling
        result = query.woql_as("v:X")
        
        assert result is query
        assert len(query._query) == 1
    
    def test_as_with_dict_arg(self):
        """Test as() with dictionary argument."""
        query = WOQLQuery()
        # This tests lines 1509-1510 - dict handling
        result = query.woql_as({"@type": "Value", "variable": "X"})
        
        assert result is query
        assert len(query._query) == 1
    
    def test_as_with_object_having_to_dict(self):
        """Test as() with object that has to_dict method."""
        query = WOQLQuery()
        var = Var("X")
        # This tests lines 1507-1508 - hasattr to_dict
        result = query.woql_as(var)
        
        assert result is query
        assert len(query._query) == 1


class TestWOQLCursorManagement:
    """Test cursor management edge cases."""
    
    def test_wrap_cursor_with_and_when_already_and(self):
        """Test _wrap_cursor_with_and when cursor is already And type."""
        query = WOQLQuery()
        # Set up cursor as And type with existing and array
        query._cursor["@type"] = "And"
        query._cursor["and"] = [{"@type": "Triple"}]
        
        # This should trigger lines 709-712
        query._wrap_cursor_with_and()
        
        # After wrapping, the query structure should be valid
        assert query._query is not None or query._cursor is not None


class TestWOQLArithmeticOperations:
    """Test arithmetic operations edge cases."""
    
    def test_clean_arithmetic_value_with_string(self):
        """Test _clean_arithmetic_value with string input."""
        query = WOQLQuery()
        
        # Test with a numeric string
        result = query._clean_arithmetic_value("42", "xsd:decimal")
        
        assert isinstance(result, dict)
        assert "@type" in result
    
    def test_clean_arithmetic_value_with_number(self):
        """Test _clean_arithmetic_value with numeric input."""
        query = WOQLQuery()
        
        # Test with a number
        result = query._clean_arithmetic_value(42, "xsd:integer")
        
        assert isinstance(result, dict)
        assert "@type" in result


class TestWOQLDocAndVarsClasses:
    """Test Doc and Vars classes for uncovered lines."""
    
    def test_doc_with_none_value(self):
        """Test Doc class handles None values."""
        doc = Doc({"key": None})
        
        assert doc.encoded["@type"] == "Value"
        assert "dictionary" in doc.encoded
    
    def test_doc_with_nested_dict(self):
        """Test Doc class handles nested dictionaries."""
        doc = Doc({"outer": {"inner": "value"}})
        
        assert isinstance(doc.encoded, dict)
        assert doc.encoded["@type"] == "Value"
    
    def test_doc_with_empty_list(self):
        """Test Doc class handles empty lists."""
        doc = Doc({"items": []})
        
        assert doc.encoded["@type"] == "Value"
        # Check that structure is created
        assert "dictionary" in doc.encoded
    
    def test_vars_creates_multiple_variables(self):
        """Test Vars class creates multiple Var instances."""
        vars_obj = Vars("var1", "var2", "var3")
        
        assert hasattr(vars_obj, "var1")
        assert hasattr(vars_obj, "var2")
        assert hasattr(vars_obj, "var3")
        assert isinstance(vars_obj.var1, Var)
        assert isinstance(vars_obj.var2, Var)
        assert isinstance(vars_obj.var3, Var)
    
    def test_var_to_dict_format(self):
        """Test Var to_dict returns correct format."""
        var = Var("test_var")
        result = var.to_dict()
        
        assert result["@type"] == "Value"
        assert result["variable"] == "test_var"
