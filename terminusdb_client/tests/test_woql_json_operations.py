"""Test JSON and document operations for WOQL Query."""
import datetime as dt
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var, Doc


class TestWOQLJSONOperations:
    """Test JSON serialization, document handling, and type conversions."""
    
    def test_clean_object_with_var(self):
        """Test _clean_object with Var object."""
        query = WOQLQuery()
        var = Var("object_var")
        result = query._clean_object(var)
        assert "@type" in result
        assert result["variable"] == "object_var"
    
    def test_clean_object_with_doc(self):
        """Test _clean_object with Doc object."""
        query = WOQLQuery()
        doc = Doc({"key": "value"})
        result = query._clean_object(doc)
        assert result == doc.encoded
        assert result["@type"] == "Value"
    
    def test_clean_object_with_float(self):
        """Test _clean_object with float value."""
        query = WOQLQuery()
        result = query._clean_object(3.14)
        assert result["@type"] == "Value"
        assert result["data"]["@type"] == "xsd:decimal"
        assert abs(result["data"]["@value"] - 3.14) < 1e-10
    
    def test_clean_object_with_float_and_target(self):
        """Test _clean_object with float and explicit target type."""
        query = WOQLQuery()
        result = query._clean_object(3.14, target="xsd:float")
        assert result["data"]["@type"] == "xsd:float"
        assert abs(result["data"]["@value"] - 3.14) < 1e-10
    
    def test_clean_object_with_int(self):
        """Test _clean_object with integer value."""
        query = WOQLQuery()
        result = query._clean_object(42)
        assert result["@type"] == "Value"
        assert result["data"]["@type"] == "xsd:integer"
        assert result["data"]["@value"] == 42
    
    def test_clean_object_with_int_and_target(self):
        """Test _clean_object with integer and explicit target type."""
        query = WOQLQuery()
        result = query._clean_object(42, target="xsd:long")
        assert result["data"]["@type"] == "xsd:long"
        assert result["data"]["@value"] == 42
    
    def test_clean_object_with_bool(self):
        """Test _clean_object with boolean value."""
        query = WOQLQuery()
        result = query._clean_object(True)
        assert result["@type"] == "Value"
        assert result["data"]["@type"] == "xsd:boolean"
        assert result["data"]["@value"] is True
    
    def test_clean_object_with_bool_and_target(self):
        """Test _clean_object with boolean and explicit target type."""
        query = WOQLQuery()
        result = query._clean_object(False, target="custom:boolean")
        assert result["data"]["@type"] == "custom:boolean"
        assert result["data"]["@value"] is False
    
    def test_clean_object_with_date(self):
        """Test _clean_object with date object."""
        query = WOQLQuery()
        test_date = dt.date(2023, 1, 1)
        result = query._clean_object(test_date)
        assert result["@type"] == "Value"
        assert result["data"]["@type"] == "xsd:dateTime"
        assert "2023-01-01" in result["data"]["@value"]
    
    def test_clean_object_with_datetime(self):
        """Test _clean_object with datetime object."""
        query = WOQLQuery()
        test_datetime = dt.datetime(2023, 1, 1, 12, 30, 45)
        result = query._clean_object(test_datetime)
        assert result["@type"] == "Value"
        assert result["data"]["@type"] == "xsd:dateTime"
        assert "2023-01-01T12:30:45" in result["data"]["@value"]
    
    def test_clean_object_with_dict_value(self):
        """Test _clean_object with dict containing @value."""
        query = WOQLQuery()
        value_dict = {"@value": 42, "@type": "xsd:integer"}
        result = query._clean_object(value_dict)
        assert result["@type"] == "Value"
        assert result["data"] == value_dict
    
    def test_clean_object_with_plain_dict(self):
        """Test _clean_object with plain dictionary (no @value)."""
        query = WOQLQuery()
        plain_dict = {"key": "value", "number": 42}
        result = query._clean_object(plain_dict)
        assert result == plain_dict
    
    def test_clean_object_with_custom_object(self):
        """Test _clean_object with custom object (converts to string)."""
        query = WOQLQuery()
        
        class CustomObject:
            def __str__(self):
                return "custom_object_string"
        
        custom_obj = CustomObject()
        result = query._clean_object(custom_obj)
        assert result["@type"] == "Value"
        assert result["data"]["@type"] == "xsd:string"
        assert result["data"]["@value"] == "custom_object_string"
    
    def test_clean_data_value_with_string(self):
        """Test _clean_data_value with string."""
        query = WOQLQuery()
        result = query._clean_data_value("test_string")
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:string"
        assert result["data"]["@value"] == "test_string"
    
    def test_clean_data_value_with_variable_string(self):
        """Test _clean_data_value with variable string."""
        query = WOQLQuery()
        result = query._clean_data_value("v:test")
        # Variable strings are expanded via _expand_data_variable
        assert "variable" in result
        assert result["@type"] == "DataValue"
    
    def test_clean_data_value_with_string_and_target(self):
        """Test _clean_data_value with string and explicit target."""
        query = WOQLQuery()
        result = query._clean_data_value("test", target="custom:string")
        assert result["data"]["@type"] == "custom:string"
        assert result["data"]["@value"] == "test"
    
    def test_clean_data_value_with_var(self):
        """Test _clean_data_value with Var object."""
        query = WOQLQuery()
        var = Var("data_var")
        result = query._clean_data_value(var)
        assert "@type" in result
        assert result["variable"] == "data_var"
    
    def test_clean_data_value_with_float(self):
        """Test _clean_data_value with float value."""
        query = WOQLQuery()
        result = query._clean_data_value(3.14)
        assert result["@type"] == "DataValue"
        assert result["data"]["@type"] == "xsd:decimal"
        assert result["data"]["@value"] == 3.14
    
    def test_json_literal_wrapping(self):
        """Test _jlt method wraps values in JSON-LD literal format."""
        query = WOQLQuery()
        result = query._jlt("test_value", "xsd:string")
        assert result["@type"] == "xsd:string"
        assert result["@value"] == "test_value"
    
    def test_json_literal_without_type(self):
        """Test _jlt method with default type."""
        query = WOQLQuery()
        result = query._jlt("test_value")
        assert result["@type"] == "xsd:string"
        assert result["@value"] == "test_value"
    
    def test_json_literal_with_numeric_value(self):
        """Test _jlt method with numeric value."""
        query = WOQLQuery()
        result = query._jlt(42, "xsd:integer")
        assert result["@type"] == "xsd:integer"
        assert result["@value"] == 42
    
    def test_json_literal_with_boolean(self):
        """Test _jlt method with boolean value."""
        query = WOQLQuery()
        result = query._jlt(True, "xsd:boolean")
        assert result["@type"] == "xsd:boolean"
        assert result["@value"] is True
    
    def test_complex_nested_json_structure(self):
        """Test handling of complex nested JSON structures."""
        query = WOQLQuery()
        
        # Create a complex nested structure
        complex_obj = {
            "name": "Test Object",
            "values": [1, 2.5, True, None],
            "nested": {
                "inner": "value",
                "list": [{"a": 1}, {"b": 2}]
            },
            "var_ref": Var("reference")
        }
        
        # Clean the object
        result = query._clean_object(complex_obj)
        
        # Should return the dict unchanged (no @value)
        assert result == complex_obj
        assert result["name"] == "Test Object"
        assert len(result["values"]) == 4
        assert result["nested"]["inner"] == "value"
    
    def test_document_embedding_in_query(self):
        """Test embedding documents within queries."""
        query = WOQLQuery()
        doc = Doc({
            "title": "Test Document",
            "content": "This is a test",
            "metadata": {
                "created": dt.date(2023, 1, 1),
                "tags": ["test", "document"]
            }
        })
        
        # Use document in triple
        query.triple("doc_id", "schema:content", doc)
        
        # Check the document was properly encoded
        assert query._cursor["object"]["@type"] == "Value"
        assert "dictionary" in query._cursor["object"]
