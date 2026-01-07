"""Tests for WOQLQuery cleaning and expansion methods."""

import datetime
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var, Doc


def test_clean_subject_with_string():
    """Test _clean_subject with plain string."""
    query = WOQLQuery()

    result = query._clean_subject("testSubject")

    assert result["@type"] == "NodeValue"
    assert result["node"] == "testSubject"


def test_clean_subject_with_colon():
    """Test _clean_subject with URI string containing colon."""
    query = WOQLQuery()

    result = query._clean_subject("doc:Person")

    assert result["@type"] == "NodeValue"
    assert result["node"] == "doc:Person"


def test_clean_subject_with_vocab():
    """Test _clean_subject uses vocab mapping."""
    query = WOQLQuery()

    result = query._clean_subject("type")

    # "type" maps to "rdf:type" in SHORT_NAME_MAPPING
    assert result["@type"] == "NodeValue"
    assert result["node"] == "rdf:type"


def test_clean_subject_with_var():
    """Test _clean_subject with Var object."""
    query = WOQLQuery()
    var = Var("Subject")

    result = query._clean_subject(var)

    assert result["@type"] == "NodeValue"
    assert result["variable"] == "Subject"


def test_clean_subject_with_dict():
    """Test _clean_subject returns dict as-is."""
    query = WOQLQuery()
    input_dict = {"@type": "NodeValue", "node": "test"}

    result = query._clean_subject(input_dict)

    assert result == input_dict


def test_clean_subject_with_invalid_type():
    """Test _clean_subject raises ValueError for invalid type."""
    query = WOQLQuery()

    try:
        query._clean_subject(123)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Subject must be a URI string" in str(e)


def test_clean_predicate_with_string():
    """Test _clean_predicate with plain string."""
    query = WOQLQuery()

    result = query._clean_predicate("testPredicate")

    assert result["@type"] == "NodeValue"
    assert result["node"] == "testPredicate"


def test_clean_predicate_with_colon():
    """Test _clean_predicate with URI containing colon."""
    query = WOQLQuery()

    result = query._clean_predicate("rdf:type")

    assert result["@type"] == "NodeValue"
    assert result["node"] == "rdf:type"


def test_clean_predicate_with_vocab():
    """Test _clean_predicate uses vocab mapping."""
    query = WOQLQuery()

    result = query._clean_predicate("label")

    # "label" maps to "rdfs:label"
    assert result["@type"] == "NodeValue"
    assert result["node"] == "rdfs:label"


def test_clean_predicate_with_var():
    """Test _clean_predicate with Var object."""
    query = WOQLQuery()
    var = Var("Predicate")

    result = query._clean_predicate(var)

    assert result["@type"] == "NodeValue"
    assert result["variable"] == "Predicate"


def test_clean_predicate_with_dict():
    """Test _clean_predicate returns dict as-is."""
    query = WOQLQuery()
    input_dict = {"@type": "NodeValue", "node": "test"}

    result = query._clean_predicate(input_dict)

    assert result == input_dict


def test_clean_predicate_with_invalid_type():
    """Test _clean_predicate raises ValueError for invalid type."""
    query = WOQLQuery()

    try:
        query._clean_predicate(123)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Predicate must be a URI string" in str(e)


def test_clean_path_predicate_with_colon():
    """Test _clean_path_predicate with URI containing colon."""
    query = WOQLQuery()

    result = query._clean_path_predicate("doc:parent")

    assert result == "doc:parent"


def test_clean_path_predicate_with_vocab():
    """Test _clean_path_predicate uses vocab mapping."""
    query = WOQLQuery()

    result = query._clean_path_predicate("type")

    assert result == "rdf:type"


def test_clean_path_predicate_with_plain_string():
    """Test _clean_path_predicate with plain string."""
    query = WOQLQuery()

    result = query._clean_path_predicate("customPredicate")

    assert result == "customPredicate"


def test_clean_path_predicate_with_none():
    """Test _clean_path_predicate returns False for None."""
    query = WOQLQuery()

    result = query._clean_path_predicate(None)

    assert result is False


def test_clean_object_with_string():
    """Test _clean_object with plain string."""
    query = WOQLQuery()

    result = query._clean_object("testObject")

    assert result["@type"] == "Value"
    assert result["node"] == "testObject"


def test_clean_object_with_v_prefix():
    """Test _clean_object with v: prefixed variable."""
    query = WOQLQuery()

    result = query._clean_object("v:MyVar")

    assert result["@type"] == "Value"
    assert result["variable"] == "MyVar"


def test_clean_object_with_var():
    """Test _clean_object with Var object."""
    query = WOQLQuery()
    var = Var("Object")

    result = query._clean_object(var)

    assert result["@type"] == "Value"
    assert result["variable"] == "Object"


def test_clean_object_with_doc():
    """Test _clean_object with Doc object."""
    query = WOQLQuery()
    doc = Doc({"name": "Alice"})

    result = query._clean_object(doc)

    # Should return the encoded version
    assert "@type" in result


def test_clean_object_with_int():
    """Test _clean_object with integer."""
    query = WOQLQuery()

    result = query._clean_object(42)

    assert result["@type"] == "Value"
    assert result["data"]["@type"] == "xsd:integer"
    assert result["data"]["@value"] == 42


def test_clean_object_with_float():
    """Test _clean_object with float."""
    query = WOQLQuery()

    result = query._clean_object(3.14)

    assert result["@type"] == "Value"
    assert result["data"]["@type"] == "xsd:decimal"
    assert result["data"]["@value"] == 3.14


def test_clean_object_with_bool():
    """Test _clean_object with boolean."""
    query = WOQLQuery()

    result = query._clean_object(True)

    assert result["@type"] == "Value"
    assert result["data"]["@type"] == "xsd:boolean"
    assert result["data"]["@value"] is True


def test_clean_object_with_date():
    """Test _clean_object with datetime."""
    query = WOQLQuery()
    dt = datetime.datetime(2025, 1, 1, 12, 0, 0)

    result = query._clean_object(dt)

    assert result["@type"] == "Value"
    assert result["data"]["@type"] == "xsd:dateTime"
    assert result["data"]["@value"] == "2025-01-01T12:00:00"


def test_clean_object_with_dict_value():
    """Test _clean_object with dict containing @value."""
    query = WOQLQuery()
    input_dict = {"@type": "xsd:string", "@value": "test"}

    result = query._clean_object(input_dict)

    assert result["@type"] == "Value"
    assert result["data"] == input_dict


def test_clean_object_with_plain_dict():
    """Test _clean_object with dict without @value."""
    query = WOQLQuery()
    input_dict = {"@type": "Custom", "node": "test"}

    result = query._clean_object(input_dict)

    assert result == input_dict


def test_clean_object_with_list():
    """Test _clean_object with list."""
    query = WOQLQuery()

    result = query._clean_object([1, "test", True])

    assert isinstance(result, list)
    assert len(result) == 3


def test_clean_object_with_custom_target():
    """Test _clean_object with custom target type."""
    query = WOQLQuery()

    result = query._clean_object(42, "xsd:long")

    assert result["data"]["@type"] == "xsd:long"


def test_clean_data_value_with_string():
    """Test _clean_data_value with string."""
    query = WOQLQuery()

    result = query._clean_data_value("test")

    assert result["@type"] == "DataValue"
    assert result["data"]["@type"] == "xsd:string"
    assert result["data"]["@value"] == "test"


def test_clean_data_value_with_v_prefix():
    """Test _clean_data_value with v: prefixed variable."""
    query = WOQLQuery()

    result = query._clean_data_value("v:MyVar")

    assert result["@type"] == "DataValue"
    assert result["variable"] == "MyVar"


def test_clean_data_value_with_var():
    """Test _clean_data_value with Var object."""
    query = WOQLQuery()
    var = Var("Data")

    result = query._clean_data_value(var)

    assert result["@type"] == "DataValue"
    assert result["variable"] == "Data"


def test_clean_data_value_with_int():
    """Test _clean_data_value with integer."""
    query = WOQLQuery()

    result = query._clean_data_value(100)

    assert result["@type"] == "DataValue"
    assert result["data"]["@type"] == "xsd:integer"
    assert result["data"]["@value"] == 100


def test_clean_data_value_with_float():
    """Test _clean_data_value with float."""
    query = WOQLQuery()

    result = query._clean_data_value(2.5)

    assert result["@type"] == "DataValue"
    assert result["data"]["@type"] == "xsd:decimal"
    assert result["data"]["@value"] == 2.5


def test_clean_data_value_with_bool():
    """Test _clean_data_value with boolean."""
    query = WOQLQuery()

    result = query._clean_data_value(False)

    assert result["@type"] == "DataValue"
    assert result["data"]["@type"] == "xsd:boolean"
    assert result["data"]["@value"] is False


def test_clean_data_value_with_date():
    """Test _clean_data_value with datetime."""
    query = WOQLQuery()
    dt = datetime.date(2025, 1, 1)

    result = query._clean_data_value(dt)

    assert result["@type"] == "DataValue"
    assert result["data"]["@type"] == "xsd:dateTime"
    assert "2025-01-01" in result["data"]["@value"]


def test_clean_data_value_with_dict_value():
    """Test _clean_data_value with dict containing @value."""
    query = WOQLQuery()
    input_dict = {"@type": "xsd:decimal", "@value": 3.14}

    result = query._clean_data_value(input_dict)

    assert result["@type"] == "DataValue"
    assert result["data"] == input_dict


def test_clean_data_value_with_plain_dict():
    """Test _clean_data_value with dict without @value."""
    query = WOQLQuery()
    input_dict = {"@type": "Custom"}

    result = query._clean_data_value(input_dict)

    assert result == input_dict


def test_clean_arithmetic_value_with_string():
    """Test _clean_arithmetic_value with string."""
    query = WOQLQuery()

    result = query._clean_arithmetic_value("42")

    assert result["@type"] == "ArithmeticValue"
    assert result["data"]["@value"] == "42"


def test_clean_arithmetic_value_with_v_prefix():
    """Test _clean_arithmetic_value with v: prefixed variable."""
    query = WOQLQuery()

    result = query._clean_arithmetic_value("v:Count")

    assert result["@type"] == "ArithmeticValue"
    assert result["variable"] == "Count"


def test_clean_arithmetic_value_with_int():
    """Test _clean_arithmetic_value with integer."""
    query = WOQLQuery()

    result = query._clean_arithmetic_value(50)

    assert result["@type"] == "ArithmeticValue"
    assert result["data"]["@type"] == "xsd:integer"
    assert result["data"]["@value"] == 50


def test_clean_arithmetic_value_with_float():
    """Test _clean_arithmetic_value with float."""
    query = WOQLQuery()

    result = query._clean_arithmetic_value(7.5)

    assert result["@type"] == "ArithmeticValue"
    assert result["data"]["@type"] == "xsd:decimal"
    assert result["data"]["@value"] == 7.5


def test_clean_arithmetic_value_with_bool():
    """Test _clean_arithmetic_value with boolean."""
    query = WOQLQuery()

    result = query._clean_arithmetic_value(True)

    assert result["@type"] == "ArithmeticValue"
    assert result["data"]["@type"] == "xsd:boolean"


def test_clean_arithmetic_value_with_date():
    """Test _clean_arithmetic_value with datetime."""
    query = WOQLQuery()
    dt = datetime.date(2025, 6, 15)

    result = query._clean_arithmetic_value(dt)

    assert result["@type"] == "ArithmeticValue"
    assert result["data"]["@type"] == "xsd:dateTime"


def test_clean_arithmetic_value_with_dict_value():
    """Test _clean_arithmetic_value with dict containing @value."""
    query = WOQLQuery()
    input_dict = {"@type": "xsd:integer", "@value": 999}

    result = query._clean_arithmetic_value(input_dict)

    assert result["@type"] == "ArithmeticValue"
    assert result["data"] == input_dict


def test_clean_arithmetic_value_with_plain_dict():
    """Test _clean_arithmetic_value with dict without @value."""
    query = WOQLQuery()
    input_dict = {"@type": "Custom"}

    result = query._clean_arithmetic_value(input_dict)

    assert result == input_dict


def test_clean_node_value_with_string():
    """Test _clean_node_value with plain string."""
    query = WOQLQuery()

    result = query._clean_node_value("nodeId")

    assert result["@type"] == "NodeValue"
    assert result["node"] == "nodeId"


def test_clean_node_value_with_v_prefix():
    """Test _clean_node_value with v: prefixed variable."""
    query = WOQLQuery()

    result = query._clean_node_value("v:Node")

    assert result["@type"] == "NodeValue"
    assert result["variable"] == "Node"


def test_clean_node_value_with_var():
    """Test _clean_node_value with Var object."""
    query = WOQLQuery()
    var = Var("MyNode")

    result = query._clean_node_value(var)

    assert result["@type"] == "NodeValue"
    assert result["variable"] == "MyNode"


def test_clean_node_value_with_dict():
    """Test _clean_node_value with dict."""
    query = WOQLQuery()
    input_dict = {"@type": "Custom", "node": "test"}

    result = query._clean_node_value(input_dict)

    assert result == input_dict


def test_clean_node_value_with_other_type():
    """Test _clean_node_value with non-string, non-Var, non-dict."""
    query = WOQLQuery()

    result = query._clean_node_value(12345)

    assert result["@type"] == "NodeValue"
    assert result["node"] == 12345


def test_clean_graph():
    """Test _clean_graph returns graph as-is."""
    query = WOQLQuery()

    result = query._clean_graph("instance/main")

    assert result == "instance/main"


def test_expand_variable_with_v_prefix():
    """Test _expand_variable with v: prefix."""
    query = WOQLQuery()

    result = query._expand_variable("v:MyVar", "Value")

    assert result["@type"] == "Value"
    assert result["variable"] == "MyVar"


def test_expand_variable_with_always_true():
    """Test _expand_variable with always=True."""
    query = WOQLQuery()

    result = query._expand_variable("MyVar", "Value", always=True)

    assert result["@type"] == "Value"
    assert result["variable"] == "MyVar"


def test_expand_variable_without_v_prefix():
    """Test _expand_variable without v: prefix and always=False."""
    query = WOQLQuery()

    result = query._expand_variable("nodeId", "NodeValue")

    assert result["@type"] == "NodeValue"
    assert result["node"] == "nodeId"


def test_expand_variable_with_var_object():
    """Test _expand_variable with Var object."""
    query = WOQLQuery()
    var = Var("X")

    result = query._expand_variable(var, "DataValue")

    assert result["@type"] == "DataValue"
    assert result["variable"] == "X"


def test_expand_value_variable():
    """Test _expand_value_variable helper."""
    query = WOQLQuery()

    result = query._expand_value_variable("v:Val")

    assert result["@type"] == "Value"
    assert result["variable"] == "Val"


def test_expand_node_variable():
    """Test _expand_node_variable helper."""
    query = WOQLQuery()

    result = query._expand_node_variable("v:Node")

    assert result["@type"] == "NodeValue"
    assert result["variable"] == "Node"


def test_expand_data_variable():
    """Test _expand_data_variable helper."""
    query = WOQLQuery()

    result = query._expand_data_variable("v:Data")

    assert result["@type"] == "DataValue"
    assert result["variable"] == "Data"


def test_expand_arithmetic_variable():
    """Test _expand_arithmetic_variable helper."""
    query = WOQLQuery()

    result = query._expand_arithmetic_variable("v:Arith")

    assert result["@type"] == "ArithmeticValue"
    assert result["variable"] == "Arith"


def test_to_json():
    """Test to_json serializes query."""
    query = WOQLQuery({"@type": "Triple"})

    result = query.to_json()

    assert isinstance(result, str)
    assert "@type" in result
    assert "Triple" in result


def test_from_json():
    """Test from_json deserializes query."""
    query = WOQLQuery()
    json_str = '{"@type": "Triple", "subject": "v:X"}'

    result = query.from_json(json_str)

    assert result is query
    assert query._query["@type"] == "Triple"


def test_json_without_input():
    """Test _json returns JSON string when no input."""
    query = WOQLQuery({"@type": "And", "and": []})

    result = query._json()

    assert isinstance(result, str)
    # The query is serialized to JSON
    assert "{" in result and "}" in result


def test_json_with_input():
    """Test _json sets query when input provided."""
    query = WOQLQuery()
    json_str = '{"@type": "Or"}'

    result = query._json(json_str)

    assert result is query
    assert query._query["@type"] == "Or"
