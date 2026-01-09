"""Tests for advanced WOQL query methods using standardized helpers."""

from terminusdb_client.woqlquery.woql_query import WOQLQuery
from terminusdb_client.tests.woql_test_helpers import WOQLTestHelpers as H


# Optional Query Tests


def test_opt_basic():
    """Test opt() creates proper Optional structure."""
    query = WOQLQuery().opt()

    H.assert_optional_structure(query)


def test_opt_with_subquery():
    """Test opt() with embedded subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().opt(subquery)

    H.assert_optional_structure(query)
    assert query._query["query"]["@type"] == "Triple"


def test_opt_args_introspection():
    """Test opt() returns args list when called with 'args'."""
    result = WOQLQuery().opt("args")

    assert result == ["query"]


# Result Control Tests


def test_limit_basic():
    """Test limit() creates proper Limit structure."""
    query = WOQLQuery().limit(10)

    H.assert_query_type(query, "Limit")
    H.assert_key_value(query, "limit", 10)


def test_limit_with_subquery():
    """Test limit() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().limit(5, subquery)

    H.assert_query_type(query, "Limit")
    assert query._query["limit"] == 5
    assert query._query["query"]["@type"] == "Triple"


def test_limit_args_introspection():
    """Test limit() returns args list when called with 'args'."""
    result = WOQLQuery().limit("args")

    assert result == ["limit", "query"]


def test_start_basic():
    """Test start() creates proper Start structure."""
    query = WOQLQuery().start(0)

    H.assert_query_type(query, "Start")
    H.assert_key_value(query, "start", 0)


def test_start_with_offset():
    """Test start() with non-zero offset."""
    query = WOQLQuery().start(100)

    H.assert_query_type(query, "Start")
    H.assert_key_value(query, "start", 100)


def test_start_with_subquery():
    """Test start() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().start(50, subquery)

    H.assert_query_type(query, "Start")
    assert query._query["start"] == 50
    assert query._query["query"]["@type"] == "Triple"


def test_start_args_introspection():
    """Test start() returns args list when called with 'args'."""
    result = WOQLQuery().start("args")

    assert result == ["start", "query"]


def test_order_by_basic():
    """Test order_by() creates proper OrderBy structure."""
    query = WOQLQuery().order_by("v:Name")

    H.assert_query_type(query, "OrderBy")
    H.assert_has_key(query, "ordering")


def test_order_by_ascending():
    """Test order_by() with explicit asc order."""
    query = WOQLQuery().order_by("v:Age", order="asc")

    H.assert_query_type(query, "OrderBy")
    assert query._query["ordering"][0]["@type"] == "OrderTemplate"


def test_order_by_descending():
    """Test order_by() with desc order."""
    query = WOQLQuery().order_by("v:Age", order="desc")

    H.assert_query_type(query, "OrderBy")
    # Ordering structure should be created
    assert "ordering" in query._query


def test_order_by_multiple_vars():
    """Test order_by() with multiple variables."""
    query = WOQLQuery().order_by("v:Name", "v:Age")

    H.assert_query_type(query, "OrderBy")
    # Should have multiple ordering criteria
    assert "ordering" in query._query


def test_order_by_args_introspection():
    """Test order_by() with args doesn't fail (order_by has complex args handling)."""
    # order_by doesn't have simple args introspection, it processes args differently
    # Just verify it doesn't crash and returns a query object
    result = WOQLQuery().order_by("v:X")

    assert isinstance(result, WOQLQuery)


# Document Operations Tests


def test_insert_document_basic():
    """Test insert_document() creates proper InsertDocument structure."""
    query = WOQLQuery().insert_document({"@type": "Person", "name": "Alice"})

    H.assert_query_type(query, "InsertDocument")
    H.assert_has_key(query, "document")
    assert query._contains_update is True


def test_insert_document_with_variable():
    """Test insert_document() with variable."""
    query = WOQLQuery().insert_document("v:Doc")

    H.assert_query_type(query, "InsertDocument")
    H.assert_is_variable(query._query["document"], "Doc")


def test_insert_document_with_identifier():
    """Test insert_document() with identifier."""
    query = WOQLQuery().insert_document({"@type": "Person"}, "v:ID")

    H.assert_query_type(query, "InsertDocument")
    H.assert_has_key(query, "identifier")


def test_insert_document_args_introspection():
    """Test insert_document() returns args list when called with 'args'."""
    result = WOQLQuery().insert_document("args")

    assert result == ["document"]


def test_update_document_basic():
    """Test update_document() creates proper UpdateDocument structure."""
    query = WOQLQuery().update_document(
        {"@id": "Person/Alice", "name": "Alice Updated"}
    )

    H.assert_query_type(query, "UpdateDocument")
    H.assert_has_key(query, "document")
    assert query._contains_update is True


def test_update_document_with_variable():
    """Test update_document() with variable."""
    query = WOQLQuery().update_document("v:Doc")

    H.assert_query_type(query, "UpdateDocument")
    H.assert_is_variable(query._query["document"], "Doc")


def test_update_document_with_identifier():
    """Test update_document() with identifier."""
    query = WOQLQuery().update_document({"name": "Updated"}, "v:ID")

    H.assert_query_type(query, "UpdateDocument")
    H.assert_has_key(query, "identifier")


def test_update_document_args_introspection():
    """Test update_document() returns args list when called with 'args'."""
    result = WOQLQuery().update_document("args")

    assert result == ["document"]


def test_delete_document_basic():
    """Test delete_document() creates proper DeleteDocument structure."""
    query = WOQLQuery().delete_document("Person/Alice")

    H.assert_query_type(query, "DeleteDocument")
    H.assert_has_key(query, "identifier")
    assert query._contains_update is True


def test_delete_document_with_variable():
    """Test delete_document() with variable."""
    query = WOQLQuery().delete_document("v:ID")

    H.assert_query_type(query, "DeleteDocument")
    H.assert_is_variable(query._query["identifier"], "ID")


def test_delete_document_args_introspection():
    """Test delete_document() returns args list when called with 'args'."""
    result = WOQLQuery().delete_document("args")

    assert result == ["document"]


def test_read_document_basic():
    """Test read_document() creates proper ReadDocument structure."""
    query = WOQLQuery().read_document("Person/Alice", "v:Doc")

    H.assert_query_type(query, "ReadDocument")
    H.assert_has_key(query, "identifier")
    H.assert_has_key(query, "document")


def test_read_document_with_variable_iri():
    """Test read_document() with variable IRI."""
    query = WOQLQuery().read_document("v:ID", "v:Doc")

    H.assert_query_type(query, "ReadDocument")
    H.assert_is_variable(query._query["identifier"], "ID")
    H.assert_is_variable(query._query["document"], "Doc")


def test_read_document_args_introspection():
    """Test read_document() returns args list when called with 'args'."""
    result = WOQLQuery().read_document("args", None)

    assert result == ["document"]


# Substring Test


def test_substr_basic():
    """Test substr() creates proper Substring structure."""
    query = WOQLQuery().substr("test string", 4, "v:Substr", before=0, after=6)

    H.assert_query_type(query, "Substring")
    H.assert_has_key(query, "string")
    H.assert_has_key(query, "before")
    H.assert_has_key(query, "length")
    H.assert_has_key(query, "after")
    H.assert_has_key(query, "substring")


def test_substr_with_variables():
    """Test substr() with variable inputs."""
    query = WOQLQuery().substr("v:String", "v:Length", "v:Substring")

    H.assert_query_type(query, "Substring")


def test_substr_invalid_string():
    """Test substr() raises ValueError for invalid string."""
    try:
        WOQLQuery().substr(None, 5, "v:Sub")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "string" in str(e).lower()


def test_substr_args_introspection():
    """Test substr() returns args list when called with 'args'."""
    result = WOQLQuery().substr("args", None, None)

    assert isinstance(result, list)
    assert "string" in result
    assert "substring" in result


# Once Test


def test_once_basic():
    """Test once() creates proper Once structure."""
    query = WOQLQuery().once()

    H.assert_query_type(query, "Once")


def test_once_with_subquery():
    """Test once() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().once(subquery)

    H.assert_query_type(query, "Once")
    assert query._query["query"]["@type"] == "Triple"


def test_once_args_introspection():
    """Test once() returns args list when called with 'args'."""
    result = WOQLQuery().once("args")

    assert result == ["query"]


# woql_not Test


def test_woql_not_basic():
    """Test woql_not() creates proper Not structure."""
    query = WOQLQuery().woql_not()

    H.assert_not_structure(query)


def test_woql_not_with_subquery():
    """Test woql_not() with subquery."""
    subquery = WOQLQuery().triple("v:X", "v:Y", "v:Z")

    query = WOQLQuery().woql_not(subquery)

    H.assert_not_structure(query)
    assert query._query["query"]["@type"] == "Triple"


def test_woql_not_args_introspection():
    """Test woql_not() returns args list when called with 'args'."""
    result = WOQLQuery().woql_not("args")

    assert result == ["query"]


# Chaining Tests


def test_chaining_limit_and_order():
    """Test chaining limit() with order_by()."""
    query = WOQLQuery().triple("v:X", "rdf:type", "Person")
    query.limit(10)
    query.order_by("v:X")

    # Should create nested structure with And
    H.assert_and_structure(query)


def test_chaining_start_and_limit():
    """Test chaining start() and limit()."""
    query = WOQLQuery().triple("v:X", "rdf:type", "Person")
    query.start(20)
    query.limit(10)

    H.assert_and_structure(query)


def test_pagination_pattern():
    """Test typical pagination pattern."""
    query = WOQLQuery().triple("v:X", "rdf:type", "Person")
    query.order_by("v:X")
    query.start(0)
    query.limit(10)

    # Should have complex nested structure
    H.assert_and_structure(query)


# Update Operations Chaining


def test_insert_then_read():
    """Test chaining insert_document() and read_document()."""
    query = WOQLQuery().insert_document({"@type": "Person"}, "v:ID")
    query.read_document("v:ID", "v:Doc")

    H.assert_and_structure(query)
    assert query._contains_update is True


def test_update_document_marks_as_update():
    """Test that update_document() marks query as containing update."""
    query = WOQLQuery()
    assert query._contains_update is False

    query.update_document({"@id": "test"})

    assert query._contains_update is True


def test_delete_document_marks_as_update():
    """Test that delete_document() marks query as containing update."""
    query = WOQLQuery()
    assert query._contains_update is False

    query.delete_document("test")

    assert query._contains_update is True
