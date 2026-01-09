"""Test edge cases and error handling for WOQL Query components."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var, Vars, Doc, SHORT_NAME_MAPPING, UPDATE_OPERATORS


class TestVarEdgeCases:
    """Test edge cases for Var class."""
    
    def test_var_to_dict(self):
        """Test Var.to_dict method returns correct structure."""
        var = Var("test_var")
        result = var.to_dict()
        assert result == {
            "@type": "Value",
            "variable": "test_var"
        }
    
    def test_var_str_representation(self):
        """Test Var string representation."""
        var = Var("my_variable")
        assert str(var) == "my_variable"


class TestVarsEdgeCases:
    """Test edge cases for Vars class."""
    
    def test_vars_single_attribute(self):
        """Test Vars with single attribute."""
        vars_obj = Vars("x")
        assert hasattr(vars_obj, "x")
        assert str(vars_obj.x) == "x"
    
    def test_vars_multiple_attributes(self):
        """Test Vars with multiple attributes."""
        vars_obj = Vars("x", "y", "z")
        assert hasattr(vars_obj, "x")
        assert hasattr(vars_obj, "y")
        assert hasattr(vars_obj, "z")
        assert str(vars_obj.x) == "x"
        assert str(vars_obj.y) == "y"
        assert str(vars_obj.z) == "z"


class TestDocEdgeCases:
    """Test edge cases for Doc class."""
    
    def test_doc_none_value(self):
        """Test Doc with None value returns None."""
        doc = Doc(None)
        assert doc.encoded is None
    
    def test_doc_str_method(self):
        """Test Doc string representation."""
        doc = Doc("test")
        assert str(doc) == "test"
    
    def test_doc_empty_list(self):
        """Test Doc with empty list."""
        doc = Doc([])
        result = doc.to_dict()
        assert result["@type"] == "Value"
        assert result["list"] == []
    
    def test_doc_nested_list(self):
        """Test Doc with nested list containing various types."""
        doc = Doc([1, "string", True, None, {"key": "value"}])
        result = doc.to_dict()
        assert result["@type"] == "Value"
        assert len(result["list"]) == 5
        assert result["list"][0]["data"]["@type"] == "xsd:integer"
        assert result["list"][1]["data"]["@type"] == "xsd:string"
        assert result["list"][2]["data"]["@type"] == "xsd:boolean"
        assert result["list"][3] is None
        assert result["list"][4]["dictionary"]["@type"] == "DictionaryTemplate"
    
    def test_doc_empty_dict(self):
        """Test Doc with empty dictionary."""
        doc = Doc({})
        result = doc.to_dict()
        assert result["@type"] == "Value"
        assert result["dictionary"]["@type"] == "DictionaryTemplate"
        assert result["dictionary"]["data"] == []
    
    def test_doc_dict_with_none_values(self):
        """Test Doc with dictionary containing None values."""
        doc = Doc({"field1": None, "field2": "value"})
        result = doc.to_dict()
        assert result["@type"] == "Value"
        pairs = result["dictionary"]["data"]
        assert len(pairs) == 2
        assert pairs[0]["field"] == "field1"
        assert pairs[0]["value"] is None
        assert pairs[1]["field"] == "field2"
        assert pairs[1]["value"]["data"]["@value"] == "value"
    
    def test_doc_with_var(self):
        """Test Doc with Var object."""
        var = Var("my_var")
        doc = Doc({"reference": var})
        result = doc.to_dict()
        pairs = result["dictionary"]["data"]
        assert pairs[0]["value"]["variable"] == "my_var"
    
    def test_doc_complex_nested_structure(self):
        """Test Doc with complex nested structure."""
        doc = Doc({
            "level1": {
                "level2": [1, 2, {"level3": Var("deep_var")}]
            },
            "list_of_dicts": [{"a": 1}, {"b": 2}]
        })
        result = doc.to_dict()
        assert result["@type"] == "Value"
        # Verify structure is preserved
        level1_pair = next(p for p in result["dictionary"]["data"] if p["field"] == "level1")
        assert level1_pair["value"]["dictionary"]["@type"] == "DictionaryTemplate"


class TestWOQLQueryEdgeCases:
    """Test edge cases for WOQLQuery initialization and basic operations."""
    
    def test_query_init_with_empty_dict(self):
        """Test WOQLQuery initialization with empty dictionary."""
        query = WOQLQuery({})
        assert query._query == {}
        assert query._graph == "schema"
    
    def test_query_init_with_custom_graph(self):
        """Test WOQLQuery initialization with custom graph."""
        query = WOQLQuery(graph="instance")
        assert query._graph == "instance"
        assert query._query == {}
    
    def test_query_init_with_existing_query(self):
        """Test WOQLQuery initialization with existing query."""
        existing_query = {"@type": "Query", "query": {"@type": "Triple"}}
        query = WOQLQuery(existing_query)
        assert query._query == existing_query
    
    def test_query_aliases(self):
        """Test all query method aliases are properly set."""
        query = WOQLQuery()
        assert query.subsumption == query.sub
        assert query.equals == query.eq
        assert query.substring == query.substr
        assert query.update == query.update_document
        assert query.delete == query.delete_document
        assert query.read == query.read_document
        assert query.insert == query.insert_document
        assert query.optional == query.opt
        assert query.idgenerator == query.idgen
        assert query.concatenate == query.concat
        assert query.typecast == query.cast
    
    def test_query_internal_state_initialization(self):
        """Test query internal state is properly initialized."""
        query = WOQLQuery()
        assert query._cursor == query._query
        assert query._chain_ended is False
        assert query._contains_update is False
        assert query._triple_builder_context == {}
        assert query._vocab == SHORT_NAME_MAPPING
        assert query._update_operators == UPDATE_OPERATORS
