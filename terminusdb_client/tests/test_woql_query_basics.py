"""Tests for basic woql_query.py classes and functions."""
from terminusdb_client.woqlquery.woql_query import Var, Vars, Doc, SHORT_NAME_MAPPING


def test_var_creation():
    """Test Var class instantiation."""
    var = Var("myVar")

    assert var.name == "myVar"


def test_var_str():
    """Test Var __str__ method."""
    var = Var("testVar")

    assert str(var) == "testVar"


def test_var_to_dict():
    """Test Var to_dict method."""
    var = Var("myVariable")

    result = var.to_dict()

    assert result == {"@type": "Value", "variable": "myVariable"}


def test_vars_creation():
    """Test Vars class creates attributes for each arg."""
    vars_obj = Vars("x", "y", "z")

    assert hasattr(vars_obj, "x")
    assert hasattr(vars_obj, "y")
    assert hasattr(vars_obj, "z")
    assert isinstance(vars_obj.x, Var)
    assert vars_obj.x.name == "x"
    assert vars_obj.y.name == "y"
    assert vars_obj.z.name == "z"


def test_vars_empty():
    """Test Vars with no arguments."""
    vars_obj = Vars()

    # Should create object successfully even with no args
    assert vars_obj is not None


def test_doc_with_string():
    """Test Doc class with string value."""
    doc = Doc("test string")

    result = doc.to_dict()

    assert result == {
        "@type": "Value",
        "data": {"@type": "xsd:string", "@value": "test string"}
    }


def test_doc_with_bool():
    """Test Doc class with boolean value."""
    doc_true = Doc(True)
    doc_false = Doc(False)

    assert doc_true.to_dict() == {
        "@type": "Value",
        "data": {"@type": "xsd:boolean", "@value": True}
    }
    assert doc_false.to_dict() == {
        "@type": "Value",
        "data": {"@type": "xsd:boolean", "@value": False}
    }


def test_doc_with_int():
    """Test Doc class with integer value."""
    doc = Doc(42)

    result = doc.to_dict()

    assert result == {
        "@type": "Value",
        "data": {"@type": "xsd:integer", "@value": 42}
    }


def test_doc_with_float():
    """Test Doc class with float value."""
    doc = Doc(3.14)

    result = doc.to_dict()

    assert result == {
        "@type": "Value",
        "data": {"@type": "xsd:decimal", "@value": 3.14}
    }


def test_doc_with_none():
    """Test Doc class with None value."""
    doc = Doc(None)

    result = doc.to_dict()

    assert result is None


def test_doc_with_list():
    """Test Doc class with list value."""
    doc = Doc([1, "test", True])

    result = doc.to_dict()

    assert result["@type"] == "Value"
    assert "list" in result
    assert len(result["list"]) == 3
    # Check first element
    assert result["list"][0] == {
        "@type": "Value",
        "data": {"@type": "xsd:integer", "@value": 1}
    }


def test_doc_with_var():
    """Test Doc class with Var value."""
    var = Var("myVar")
    doc = Doc(var)

    result = doc.to_dict()

    assert result == {
        "@type": "Value",
        "variable": "myVar"
    }


def test_doc_with_dict():
    """Test Doc class with dictionary value."""
    doc = Doc({"name": "Alice", "age": 30})

    result = doc.to_dict()

    assert result["@type"] == "Value"
    assert "dictionary" in result
    assert result["dictionary"]["@type"] == "DictionaryTemplate"
    assert len(result["dictionary"]["data"]) == 2

    # Find the name field
    name_pair = next(p for p in result["dictionary"]["data"] if p["field"] == "name")
    assert name_pair["value"] == {
        "@type": "Value",
        "data": {"@type": "xsd:string", "@value": "Alice"}
    }


def test_doc_str():
    """Test Doc __str__ method."""
    doc = Doc({"key": "value"})

    result = str(doc)

    assert result == "{'key': 'value'}"


def test_doc_nested_structures():
    """Test Doc with nested list and dict."""
    doc = Doc({
        "list": [1, 2, 3],
        "nested": {"inner": "value"}
    })

    result = doc.to_dict()

    assert result["@type"] == "Value"
    assert "dictionary" in result


def test_short_name_mapping_exists():
    """Test SHORT_NAME_MAPPING dictionary exists and has expected keys."""
    assert "type" in SHORT_NAME_MAPPING
    assert SHORT_NAME_MAPPING["type"] == "rdf:type"

    assert "label" in SHORT_NAME_MAPPING
    assert SHORT_NAME_MAPPING["label"] == "rdfs:label"

    assert "string" in SHORT_NAME_MAPPING
    assert SHORT_NAME_MAPPING["string"] == "xsd:string"

    assert "integer" in SHORT_NAME_MAPPING
    assert SHORT_NAME_MAPPING["integer"] == "xsd:integer"


def test_doc_with_empty_list():
    """Test Doc with empty list."""
    doc = Doc([])

    result = doc.to_dict()

    assert result == {"@type": "Value", "list": []}


def test_doc_with_empty_dict():
    """Test Doc with empty dictionary."""
    doc = Doc({})

    result = doc.to_dict()

    assert result == {
        "@type": "Value",
        "dictionary": {"@type": "DictionaryTemplate", "data": []}
    }


def test_doc_with_nested_var():
    """Test Doc with Var inside a list."""
    var = Var("x")
    doc = Doc([1, var, "test"])

    result = doc.to_dict()

    assert result["list"][1] == {"@type": "Value", "variable": "x"}


def test_doc_with_mixed_types():
    """Test Doc with various mixed types in dict."""
    var = Var("status")
    doc = Doc({
        "id": 1,
        "name": "Test",
        "active": True,
        "score": 95.5,
        "status": var,
        "tags": ["a", "b"],
        "metadata": None
    })

    result = doc.to_dict()

    assert result["@type"] == "Value"
    assert "dictionary" in result
    assert result["dictionary"]["@type"] == "DictionaryTemplate"
    assert len(result["dictionary"]["data"]) == 7


def test_vars_multiple_creation():
    """Test Vars creates multiple Var instances."""
    v = Vars("name", "age", "city")

    # All should be Var instances
    assert isinstance(v.name, Var)
    assert isinstance(v.age, Var)
    assert isinstance(v.city, Var)

    # Each should have correct name
    assert v.name.name == "name"
    assert v.age.name == "age"
    assert v.city.name == "city"

    # They should be different objects
    assert v.name is not v.age
    assert v.age is not v.city
