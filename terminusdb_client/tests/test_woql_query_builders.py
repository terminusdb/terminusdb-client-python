"""Tests for WOQL query builder methods using standardized helpers."""
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var
from terminusdb_client.tests.woql_test_helpers import WOQLTestHelpers as H


# Basic Query Builders

def test_triple_basic():
    """Test triple() creates proper Triple structure."""
    query = WOQLQuery().triple("v:Subject", "rdf:type", "v:Object")

    H.assert_triple_structure(query)
    H.assert_is_variable(query._query["subject"], "Subject")
    H.assert_is_variable(query._query["object"], "Object")


def test_triple_with_strings():
    """Test triple() with plain string arguments."""
    query = WOQLQuery().triple("doc:Person1", "rdfs:label", "Alice")

    H.assert_triple_structure(query)
    assert query._query["subject"]["node"] == "doc:Person1"
    assert query._query["predicate"]["node"] == "rdfs:label"


def test_triple_with_var_objects():
    """Test triple() with Var objects."""
    s = Var("Subject")
    p = Var("Pred")
    o = Var("Obj")

    query = WOQLQuery().triple(s, p, o)

    H.assert_triple_structure(query)
    H.assert_is_variable(query._query["subject"], "Subject")
    H.assert_is_variable(query._query["predicate"], "Pred")
    H.assert_is_variable(query._query["object"], "Obj")


def test_triple_with_opt():
    """Test triple() with opt=True wraps in Optional."""
    query = WOQLQuery().triple("v:S", "v:P", "v:O", opt=True)

    H.assert_optional_structure(query)
    # The triple is nested inside the optional
    inner = query._query["query"]
    assert inner["@type"] == "Triple"


def test_select_basic():
    """Test select() creates proper Select structure."""
    query = WOQLQuery().select("v:X", "v:Y")

    H.assert_select_structure(query)
    assert query._query["variables"] == ["X", "Y"]


def test_select_with_strings_and_subquery():
    """Test select() with string variables (strings don't have to_dict)."""
    query = WOQLQuery().select("v:X", "v:Y", "v:Z")

    H.assert_select_structure(query)
    assert query._query["variables"] == ["X", "Y", "Z"]


def test_select_with_subquery():
    """Test select() with embedded subquery."""
    subquery = WOQLQuery().triple("v:X", "rdf:type", "owl:Class")

    query = WOQLQuery().select("v:X", subquery)

    H.assert_select_structure(query)
    assert query._query["variables"] == ["X"]
    assert query._query["query"]["@type"] == "Triple"


def test_select_empty():
    """Test select() with no arguments."""
    query = WOQLQuery().select()

    H.assert_select_structure(query)
    assert query._query["variables"] == []


def test_distinct_basic():
    """Test distinct() creates proper Distinct structure."""
    query = WOQLQuery().distinct("v:X")

    H.assert_query_type(query, "Distinct")
    H.assert_has_key(query, "variables")
    assert query._query["variables"] == ["X"]


def test_distinct_with_subquery():
    """Test distinct() with embedded subquery."""
    subquery = WOQLQuery().triple("v:X", "v:P", "v:Y")

    query = WOQLQuery().distinct("v:X", "v:Y", subquery)

    H.assert_query_type(query, "Distinct")
    assert query._query["variables"] == ["X", "Y"]
    assert query._query["query"]["@type"] == "Triple"


def test_woql_and_basic():
    """Test woql_and() creates proper And structure."""
    q1 = WOQLQuery().triple("v:X", "rdf:type", "v:T")
    q2 = WOQLQuery().triple("v:X", "rdfs:label", "v:L")

    query = WOQLQuery().woql_and(q1, q2)

    H.assert_and_structure(query, expected_count=2)
    assert query._query["and"][0]["@type"] == "Triple"
    assert query._query["and"][1]["@type"] == "Triple"


def test_woql_and_flattens_nested_and():
    """Test woql_and() flattens nested And queries."""
    q1 = WOQLQuery().triple("v:A", "v:B", "v:C")
    q2 = WOQLQuery().triple("v:D", "v:E", "v:F")
    nested = WOQLQuery().woql_and(q1, q2)

    q3 = WOQLQuery().triple("v:G", "v:H", "v:I")
    query = WOQLQuery().woql_and(nested, q3)

    H.assert_and_structure(query, expected_count=3)


def test_woql_and_with_existing_cursor():
    """Test woql_and() with existing query in cursor."""
    query = WOQLQuery().triple("v:X", "v:Y", "v:Z")
    query.woql_and(WOQLQuery().triple("v:A", "v:B", "v:C"))

    H.assert_and_structure(query, expected_count=2)


def test_woql_or_basic():
    """Test woql_or() creates proper Or structure."""
    q1 = WOQLQuery().triple("v:X", "rdf:type", "Person")
    q2 = WOQLQuery().triple("v:X", "rdf:type", "Company")

    query = WOQLQuery().woql_or(q1, q2)

    H.assert_or_structure(query, expected_count=2)
    assert query._query["or"][0]["@type"] == "Triple"
    assert query._query["or"][1]["@type"] == "Triple"


def test_woql_or_multiple():
    """Test woql_or() with multiple queries."""
    q1 = WOQLQuery().triple("v:X", "v:P1", "v:O1")
    q2 = WOQLQuery().triple("v:X", "v:P2", "v:O2")
    q3 = WOQLQuery().triple("v:X", "v:P3", "v:O3")

    query = WOQLQuery().woql_or(q1, q2, q3)

    H.assert_or_structure(query, expected_count=3)


def test_woql_not():
    """Test not operator creates proper Not structure."""
    inner = WOQLQuery().triple("v:X", "v:P", "v:O")

    query = ~inner

    H.assert_not_structure(query)
    assert query._query["query"]["@type"] == "Triple"


def test_using_basic():
    """Test using() creates proper Using structure."""
    query = WOQLQuery().using("myCollection")

    H.assert_query_type(query, "Using")
    H.assert_key_value(query, "collection", "myCollection")


def test_using_with_subquery():
    """Test using() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().using("myCollection", subquery)

    H.assert_query_type(query, "Using")
    assert query._query["collection"] == "myCollection"
    assert query._query["query"]["@type"] == "Triple"


def test_using_invalid_collection():
    """Test using() raises ValueError for invalid collection."""
    try:
        WOQLQuery().using(123)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Collection ID" in str(e)


def test_comment_basic():
    """Test comment() creates proper Comment structure."""
    query = WOQLQuery().comment("This is a comment")

    H.assert_query_type(query, "Comment")
    H.assert_has_key(query, "comment")
    assert query._query["comment"]["@type"] == "xsd:string"


def test_comment_with_subquery():
    """Test comment() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().comment("Test comment", subquery)

    H.assert_query_type(query, "Comment")
    assert query._query["query"]["@type"] == "Triple"


def test_woql_from_basic():
    """Test woql_from() creates proper From structure."""
    query = WOQLQuery().woql_from("instance/main")

    H.assert_query_type(query, "From")
    H.assert_key_value(query, "graph", "instance/main")


def test_woql_from_with_subquery():
    """Test woql_from() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().woql_from("instance/main", subquery)

    H.assert_query_type(query, "From")
    assert query._query["graph"] == "instance/main"
    assert query._query["query"]["@type"] == "Triple"


def test_woql_from_invalid_graph():
    """Test woql_from() raises ValueError for invalid graph."""
    try:
        WOQLQuery().woql_from(123)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Graph Filter Expression" in str(e)


def test_into_basic():
    """Test into() creates proper Into structure."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().into("instance/main", subquery)

    H.assert_query_type(query, "Into")
    H.assert_key_value(query, "graph", "instance/main")


def test_into_invalid_graph():
    """Test into() raises ValueError for invalid graph."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    try:
        WOQLQuery().into(None, subquery)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Graph Filter Expression" in str(e)


def test_execute_without_commit():
    """Test execute() calls client.query without commit_msg."""
    query = WOQLQuery().triple("v:X", "v:Y", "v:Z")
    client = H.create_mock_client()

    result = query.execute(client)

    client.query.assert_called_once_with(query)
    assert result["@type"] == "api:WoqlResponse"


def test_execute_with_commit():
    """Test execute() calls client.query with commit_msg."""
    query = WOQLQuery().triple("v:X", "v:Y", "v:Z")
    client = H.create_mock_client()

    result = query.execute(client, commit_msg="Test commit")

    client.query.assert_called_once_with(query, "Test commit")
    assert result["@type"] == "api:WoqlResponse"


# Chaining Tests

def test_chaining_triple_and_triple():
    """Test chaining multiple triple() calls."""
    query = WOQLQuery().triple("v:X", "rdf:type", "Person")
    query.triple("v:X", "rdfs:label", "v:Name")

    H.assert_and_structure(query, expected_count=2)
    assert query._query["and"][0]["@type"] == "Triple"
    assert query._query["and"][1]["@type"] == "Triple"


def test_chaining_select_with_triple():
    """Test chaining select() with triple()."""
    inner_query = WOQLQuery().triple("v:X", "rdf:type", "Person")
    query = WOQLQuery().select("v:X", inner_query)

    H.assert_select_structure(query)
    assert query._query["query"]["@type"] == "Triple"


def test_operators_return_self():
    """Test that query methods return self for chaining."""
    query = WOQLQuery()

    result1 = query.triple("v:X", "v:Y", "v:Z")
    assert result1 is query

    result2 = query.select("v:X")
    # select wraps, so cursor changes but returns self
    assert result2 is query


# Edge Cases

def test_select_with_empty_list():
    """Test select() explicitly with empty list."""
    query = WOQLQuery().select()

    H.assert_select_structure(query)
    assert query._query["variables"] == []


def test_woql_and_empty():
    """Test woql_and() with no arguments."""
    query = WOQLQuery().woql_and()

    H.assert_and_structure(query, expected_count=0)


def test_woql_or_empty():
    """Test woql_or() with no arguments."""
    query = WOQLQuery().woql_or()

    H.assert_or_structure(query, expected_count=0)


def test_triple_with_integer_object():
    """Test triple() with integer as object."""
    query = WOQLQuery().triple("v:X", "schema:age", 42)

    H.assert_triple_structure(query)
    obj = query._query["object"]
    assert obj["@type"] == "Value"
    assert obj["data"]["@type"] == "xsd:integer"
    assert obj["data"]["@value"] == 42


def test_triple_with_string_object():
    """Test triple() with string literal as object."""
    query = WOQLQuery().triple("v:X", "rdfs:label", "Alice")

    H.assert_triple_structure(query)
    obj = query._query["object"]
    # String without v: prefix becomes a node
    assert "node" in obj or obj.get("@type") == "Value"


# Args Introspection Tests

def test_using_args_introspection():
    """Test using() returns args list when called with 'args'."""
    result = WOQLQuery().using("args")

    assert result == ["collection", "query"]


def test_comment_args_introspection():
    """Test comment() returns args list when called with 'args'."""
    result = WOQLQuery().comment("args")

    assert result == ["comment", "query"]


def test_select_args_introspection():
    """Test select() returns args list when called with 'args'."""
    result = WOQLQuery().select("args")

    assert result == ["variables", "query"]


def test_distinct_args_introspection():
    """Test distinct() returns args list when called with 'args'."""
    result = WOQLQuery().distinct("args")

    assert result == ["variables", "query"]


def test_woql_and_args_introspection():
    """Test woql_and() returns args list when called with 'args'."""
    result = WOQLQuery().woql_and("args")

    assert result == ["and"]


def test_woql_or_args_introspection():
    """Test woql_or() returns args list when called with 'args'."""
    result = WOQLQuery().woql_or("args")

    assert result == ["or"]


def test_woql_from_args_introspection():
    """Test woql_from() returns args list when called with 'args'."""
    result = WOQLQuery().woql_from("args")

    assert result == ["graph", "query"]


def test_into_args_introspection():
    """Test into() returns args list when called with 'args'."""
    result = WOQLQuery().into("args", None)

    assert result == ["graph", "query"]
