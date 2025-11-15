"""Tests for WOQLQuery class methods in woql_query.py."""
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


def test_woqlquery_initialization_empty():
    """Test WOQLQuery initialization with no arguments."""
    query = WOQLQuery()
    
    assert query._query == {}
    assert query._cursor == query._query
    assert query._chain_ended is False
    assert query._contains_update is False
    assert query._graph == "schema"


def test_woqlquery_initialization_with_query():
    """Test WOQLQuery initialization with query dict."""
    initial_query = {"@type": "Triple", "subject": "v:X"}
    query = WOQLQuery(query=initial_query)
    
    assert query._query == initial_query
    assert query._cursor == query._query


def test_woqlquery_initialization_with_graph():
    """Test WOQLQuery initialization with custom graph."""
    query = WOQLQuery(graph="instance")
    
    assert query._graph == "instance"


def test_woqlquery_aliases():
    """Test that WOQLQuery has expected method aliases."""
    query = WOQLQuery()
    
    # Check aliases exist
    assert hasattr(query, 'subsumption')
    assert hasattr(query, 'equals')
    assert hasattr(query, 'substring')
    assert hasattr(query, 'update')
    assert hasattr(query, 'delete')
    assert hasattr(query, 'read')
    assert hasattr(query, 'insert')
    assert hasattr(query, 'optional')
    assert hasattr(query, 'idgenerator')
    assert hasattr(query, 'concatenate')
    assert hasattr(query, 'typecast')


def test_woqlquery_add_operator():
    """Test WOQLQuery __add__ operator."""
    q1 = WOQLQuery({"@type": "Query1"})
    q2 = WOQLQuery({"@type": "Query2"})
    
    result = q1 + q2
    
    assert isinstance(result, WOQLQuery)
    assert result._query.get("@type") == "And"


def test_woqlquery_and_operator():
    """Test WOQLQuery __and__ operator."""
    q1 = WOQLQuery({"@type": "Query1"})
    q2 = WOQLQuery({"@type": "Query2"})
    
    result = q1 & q2
    
    assert isinstance(result, WOQLQuery)
    assert result._query.get("@type") == "And"


def test_woqlquery_or_operator():
    """Test WOQLQuery __or__ operator."""
    q1 = WOQLQuery({"@type": "Query1"})
    q2 = WOQLQuery({"@type": "Query2"})
    
    result = q1 | q2
    
    assert isinstance(result, WOQLQuery)
    assert result._query.get("@type") == "Or"


def test_woqlquery_invert_operator():
    """Test WOQLQuery __invert__ operator (not)."""
    q = WOQLQuery({"@type": "Query"})
    
    result = ~q
    
    assert isinstance(result, WOQLQuery)
    assert result._query.get("@type") == "Not"


def test_add_sub_query_with_query():
    """Test _add_sub_query with a query object."""
    query = WOQLQuery()
    sub_query = {"@type": "Triple"}
    
    result = query._add_sub_query(sub_query)
    
    assert result is query  # Returns self
    assert query._cursor["query"] == sub_query


def test_add_sub_query_without_query():
    """Test _add_sub_query creates empty object when no query provided."""
    query = WOQLQuery()
    original_cursor = query._cursor
    
    result = query._add_sub_query()
    
    assert result is query
    assert "query" in original_cursor
    # Cursor is moved to the new empty object
    assert query._cursor == {}
    assert original_cursor["query"] == query._cursor


def test_contains_update_check_false():
    """Test _contains_update_check returns False for read query."""
    query = WOQLQuery({"@type": "Triple", "subject": "v:X"})
    
    assert query._contains_update_check() is False


def test_contains_update_check_true_direct():
    """Test _contains_update_check detects update operators."""
    query = WOQLQuery({"@type": "AddTriple"})
    
    assert query._contains_update_check() is True


def test_contains_update_check_in_consequent():
    """Test _contains_update_check detects updates in consequent."""
    query = WOQLQuery({
        "@type": "When",
        "consequent": {"@type": "DeleteTriple"}
    })
    
    assert query._contains_update_check() is True


def test_contains_update_check_in_nested_query():
    """Test _contains_update_check detects updates in nested query."""
    query = WOQLQuery({
        "@type": "Select",
        "query": {"@type": "UpdateObject"}
    })
    
    assert query._contains_update_check() is True


def test_contains_update_check_in_and():
    """Test _contains_update_check detects updates in And clause."""
    query = WOQLQuery({
        "@type": "And",
        "and": [
            {"@type": "Triple"},
            {"@type": "AddQuad"}
        ]
    })
    
    assert query._contains_update_check() is True


def test_contains_update_check_in_or():
    """Test _contains_update_check detects updates in Or clause."""
    query = WOQLQuery({
        "@type": "Or",
        "or": [
            {"@type": "Triple"},
            {"@type": "DeleteObject"}
        ]
    })
    
    assert query._contains_update_check() is True


def test_contains_update_check_non_dict():
    """Test _contains_update_check returns False for non-dict."""
    query = WOQLQuery()
    
    assert query._contains_update_check("not a dict") is False


def test_updated_method():
    """Test _updated marks query as containing update."""
    query = WOQLQuery()
    
    assert query._contains_update is False
    result = query._updated()
    
    assert result is query  # Returns self
    assert query._contains_update is True


def test_jlt_default_type():
    """Test _jlt wraps value with default xsd:string type."""
    query = WOQLQuery()
    
    result = query._jlt("test value")
    
    assert result == {"@type": "xsd:string", "@value": "test value"}


def test_jlt_custom_type():
    """Test _jlt wraps value with custom type."""
    query = WOQLQuery()
    
    result = query._jlt(42, "xsd:integer")
    
    assert result == {"@type": "xsd:integer", "@value": 42}


def test_jlt_type_without_prefix():
    """Test _jlt adds xsd: prefix when not present."""
    query = WOQLQuery()
    
    result = query._jlt(3.14, "decimal")
    
    assert result == {"@type": "xsd:decimal", "@value": 3.14}


def test_varj_with_var_object():
    """Test _varj with Var object."""
    query = WOQLQuery()
    var = Var("myVar")
    
    result = query._varj(var)
    
    assert result == {"@type": "Value", "variable": "myVar"}


def test_varj_with_v_prefix():
    """Test _varj strips v: prefix."""
    query = WOQLQuery()
    
    result = query._varj("v:myVariable")
    
    assert result == {"@type": "Value", "variable": "myVariable"}


def test_varj_with_plain_string():
    """Test _varj with plain string."""
    query = WOQLQuery()
    
    result = query._varj("varName")
    
    assert result == {"@type": "Value", "variable": "varName"}


def test_varj_multiple_variations():
    """Test _varj handles various variable formats."""
    query = WOQLQuery()
    
    # Test multiple cases
    assert query._varj(Var("a"))["variable"] == "a"
    assert query._varj("v:b")["variable"] == "b"
    assert query._varj("c")["variable"] == "c"


def test_coerce_to_dict_with_to_dict_method():
    """Test _coerce_to_dict calls to_dict() if available."""
    query = WOQLQuery()
    var = Var("x")
    
    result = query._coerce_to_dict(var)
    
    assert result == {"@type": "Value", "variable": "x"}


def test_coerce_to_dict_with_true():
    """Test _coerce_to_dict handles True specially."""
    query = WOQLQuery()
    
    result = query._coerce_to_dict(True)
    
    assert result == {"@type": "True"}


def test_coerce_to_dict_with_dict():
    """Test _coerce_to_dict returns dict as-is."""
    query = WOQLQuery()
    input_dict = {"@type": "Test"}
    
    result = query._coerce_to_dict(input_dict)
    
    assert result == input_dict


def test_raw_var_with_var_object():
    """Test _raw_var extracts name from Var object."""
    query = WOQLQuery()
    var = Var("myVar")
    
    result = query._raw_var(var)
    
    assert result == "myVar"


def test_raw_var_with_v_prefix():
    """Test _raw_var strips v: prefix."""
    query = WOQLQuery()
    
    result = query._raw_var("v:varName")
    
    assert result == "varName"


def test_raw_var_with_plain_string():
    """Test _raw_var returns plain string as-is."""
    query = WOQLQuery()
    
    result = query._raw_var("plainName")
    
    assert result == "plainName"


def test_raw_var_list():
    """Test _raw_var_list processes list of variables."""
    query = WOQLQuery()
    vars_list = [Var("x"), "v:y", "z"]
    
    result = query._raw_var_list(vars_list)
    
    assert result == ["x", "y", "z"]


def test_asv_with_column_index():
    """Test _asv with integer column index."""
    query = WOQLQuery()
    
    result = query._asv(0, "varName")
    
    assert result["@type"] == "Column"
    assert result["indicator"]["@type"] == "Indicator"
    assert result["indicator"]["index"] == 0
    assert result["variable"] == "varName"


def test_asv_with_column_name():
    """Test _asv with string column name."""
    query = WOQLQuery()
    
    result = query._asv("ColName", "varName")
    
    assert result["@type"] == "Column"
    assert result["indicator"]["@type"] == "Indicator"
    assert result["indicator"]["name"] == "ColName"
    assert result["variable"] == "varName"


def test_asv_with_var_object():
    """Test _asv with Var object as variable name."""
    query = WOQLQuery()
    var = Var("myVar")
    
    result = query._asv("ColName", var)
    
    assert result["variable"] == "myVar"


def test_asv_strips_v_prefix():
    """Test _asv strips v: prefix from variable name."""
    query = WOQLQuery()
    
    result = query._asv("ColName", "v:varName")
    
    assert result["variable"] == "varName"


def test_asv_with_type():
    """Test _asv includes type when provided."""
    query = WOQLQuery()
    
    result = query._asv("ColName", "varName", "xsd:string")
    
    assert result["type"] == "xsd:string"


def test_wfrom_with_format():
    """Test _wfrom sets format."""
    query = WOQLQuery()
    opts = {"format": "csv"}
    
    query._wfrom(opts)
    
    assert query._cursor["format"]["@type"] == "Format"
    assert query._cursor["format"]["format_type"]["@value"] == "csv"


def test_wfrom_with_format_header():
    """Test _wfrom sets format_header."""
    query = WOQLQuery()
    opts = {"format": "csv", "format_header": True}
    
    query._wfrom(opts)
    
    assert query._cursor["format"]["format_header"]["@value"] is True
    assert query._cursor["format"]["format_header"]["@type"] == "xsd:boolean"


def test_wfrom_without_format():
    """Test _wfrom does nothing without format option."""
    query = WOQLQuery()
    
    query._wfrom(None)
    
    assert "format" not in query._cursor


def test_arop_with_dict():
    """Test _arop returns dict as-is."""
    query = WOQLQuery()
    input_dict = {"@type": "Value", "data": 42}
    
    result = query._arop(input_dict)
    
    assert result == input_dict
