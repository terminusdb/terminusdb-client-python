"""Tests for WOQLQuery utility methods."""
from terminusdb_client.woqlquery.woql_query import WOQLQuery


def test_to_dict():
    """Test to_dict returns copy of query."""
    query = WOQLQuery({"@type": "Triple", "subject": "v:X"})

    result = query.to_dict()

    assert result["@type"] == "Triple"
    assert result["subject"] == "v:X"
    # Should be a copy, not the same object
    assert result is not query._query


def test_from_dict():
    """Test from_dict sets query from dict."""
    query = WOQLQuery()
    dictdata = {"@type": "And", "and": []}

    result = query.from_dict(dictdata)

    assert result is query  # Returns self
    assert query._query["@type"] == "And"


def test_find_last_subject_with_subject():
    """Test _find_last_subject finds subject in simple query."""
    query = WOQLQuery()
    json_obj = {"@type": "Triple", "subject": "v:X", "predicate": "v:P"}

    result = query._find_last_subject(json_obj)

    assert result == json_obj


def test_find_last_subject_in_and():
    """Test _find_last_subject finds subject in And clause."""
    query = WOQLQuery()
    triple = {"@type": "Triple", "subject": "v:Y"}
    json_obj = {
        "@type": "And",
        "and": [
            {"@type": "Other"},
            triple
        ]
    }

    result = query._find_last_subject(json_obj)

    assert result == triple


def test_find_last_subject_in_or():
    """Test _find_last_subject finds subject in Or clause."""
    query = WOQLQuery()
    triple = {"@type": "Triple", "subject": "v:Z"}
    json_obj = {
        "@type": "Or",
        "or": [
            {"@type": "Other"},
            triple
        ]
    }

    result = query._find_last_subject(json_obj)

    assert result == triple


def test_find_last_subject_in_nested_query():
    """Test _find_last_subject finds subject in nested query."""
    query = WOQLQuery()
    triple = {"@type": "Triple", "subject": "v:A"}
    json_obj = {
        "@type": "Select",
        "query": triple
    }

    result = query._find_last_subject(json_obj)

    assert result == triple


def test_find_last_subject_not_found():
    """Test _find_last_subject returns False when no subject found."""
    query = WOQLQuery()
    json_obj = {"@type": "Other", "data": "test"}

    result = query._find_last_subject(json_obj)

    assert result is False


def test_find_last_subject_reverse_order():
    """Test _find_last_subject searches in reverse order."""
    query = WOQLQuery()
    first = {"@type": "Triple", "subject": "v:First"}
    last = {"@type": "Triple", "subject": "v:Last"}
    json_obj = {
        "@type": "And",
        "and": [first, last]
    }

    result = query._find_last_subject(json_obj)

    # Should find the last one
    assert result == last


def test_find_last_property_with_object_property():
    """Test _find_last_property finds owl:ObjectProperty."""
    query = WOQLQuery()
    json_obj = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdf:type",
        "object": "owl:ObjectProperty"
    }

    result = query._find_last_property(json_obj)

    assert result == json_obj


def test_find_last_property_with_datatype_property():
    """Test _find_last_property finds owl:DatatypeProperty."""
    query = WOQLQuery()
    json_obj = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdf:type",
        "object": "owl:DatatypeProperty"
    }

    result = query._find_last_property(json_obj)

    assert result == json_obj


def test_find_last_property_with_domain():
    """Test _find_last_property finds rdfs:domain predicate."""
    query = WOQLQuery()
    json_obj = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdfs:domain",
        "object": "v:Y"
    }

    result = query._find_last_property(json_obj)

    assert result == json_obj


def test_find_last_property_with_range():
    """Test _find_last_property finds rdfs:range predicate."""
    query = WOQLQuery()
    json_obj = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdfs:range",
        "object": "xsd:string"
    }

    result = query._find_last_property(json_obj)

    assert result == json_obj


def test_find_last_property_in_and():
    """Test _find_last_property finds property in And clause."""
    query = WOQLQuery()
    prop_triple = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdfs:domain",
        "object": "v:Y"
    }
    json_obj = {
        "@type": "And",
        "and": [
            {"@type": "Other"},
            prop_triple
        ]
    }

    result = query._find_last_property(json_obj)

    assert result == prop_triple


def test_find_last_property_in_or():
    """Test _find_last_property finds property in Or clause."""
    query = WOQLQuery()
    prop_triple = {
        "@type": "Triple",
        "subject": "v:X",
        "object": "owl:ObjectProperty"
    }
    json_obj = {
        "@type": "Or",
        "or": [
            {"@type": "Other"},
            prop_triple
        ]
    }

    result = query._find_last_property(json_obj)

    assert result == prop_triple


def test_find_last_property_in_nested_query():
    """Test _find_last_property finds property in nested query."""
    query = WOQLQuery()
    prop_triple = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdfs:range",
        "object": "v:Y"
    }
    json_obj = {
        "@type": "Select",
        "query": prop_triple
    }

    result = query._find_last_property(json_obj)

    assert result == prop_triple


def test_find_last_property_not_found():
    """Test _find_last_property returns False when no property found."""
    query = WOQLQuery()
    json_obj = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "someOther:predicate",
        "object": "v:Y"
    }

    result = query._find_last_property(json_obj)

    assert result is False


def test_is_property_triple_object_property():
    """Test _is_property_triple with owl:ObjectProperty."""
    query = WOQLQuery()

    result = query._is_property_triple("rdf:type", "owl:ObjectProperty")

    assert result is True


def test_is_property_triple_datatype_property():
    """Test _is_property_triple with owl:DatatypeProperty."""
    query = WOQLQuery()

    result = query._is_property_triple("rdf:type", "owl:DatatypeProperty")

    assert result is True


def test_is_property_triple_domain():
    """Test _is_property_triple with rdfs:domain predicate."""
    query = WOQLQuery()

    result = query._is_property_triple("rdfs:domain", "v:Something")

    assert result is True


def test_is_property_triple_range():
    """Test _is_property_triple with rdfs:range predicate."""
    query = WOQLQuery()

    result = query._is_property_triple("rdfs:range", "xsd:string")

    assert result is True


def test_is_property_triple_false():
    """Test _is_property_triple returns False for non-property triple."""
    query = WOQLQuery()

    result = query._is_property_triple("rdf:type", "owl:Class")

    assert result is False


def test_is_property_triple_with_dict_pred():
    """Test _is_property_triple with dict predicate."""
    query = WOQLQuery()
    pred = {"@type": "NodeValue", "node": "rdfs:domain"}

    result = query._is_property_triple(pred, "v:X")

    assert result is True


def test_is_property_triple_with_dict_obj():
    """Test _is_property_triple with dict object."""
    query = WOQLQuery()
    obj = {"@type": "NodeValue", "node": "owl:ObjectProperty"}

    result = query._is_property_triple("rdf:type", obj)

    assert result is True


def test_is_property_triple_with_both_dicts():
    """Test _is_property_triple with both dict pred and obj."""
    query = WOQLQuery()
    pred = {"@type": "NodeValue", "node": "rdfs:range"}
    obj = {"@type": "NodeValue", "node": "xsd:string"}

    result = query._is_property_triple(pred, obj)

    assert result is True


def test_is_property_triple_with_dict_no_node():
    """Test _is_property_triple with dict without node."""
    query = WOQLQuery()
    pred = {"@type": "NodeValue", "variable": "P"}
    obj = {"@type": "NodeValue", "variable": "O"}

    result = query._is_property_triple(pred, obj)

    # Neither has 'node', so extracts None
    assert result is False


def test_find_last_subject_deeply_nested():
    """Test _find_last_subject with deep nesting."""
    query = WOQLQuery()
    triple = {"@type": "Triple", "subject": "v:Deep"}
    json_obj = {
        "@type": "And",
        "and": [
            {
                "@type": "Or",
                "or": [
                    {"@type": "Select", "query": triple}
                ]
            }
        ]
    }

    result = query._find_last_subject(json_obj)

    assert result == triple


def test_find_last_property_deeply_nested():
    """Test _find_last_property with deep nesting."""
    query = WOQLQuery()
    triple = {
        "@type": "Triple",
        "subject": "v:X",
        "predicate": "rdfs:domain",
        "object": "v:Y"
    }
    json_obj = {
        "@type": "And",
        "and": [
            {
                "@type": "Or",
                "or": [
                    {"@type": "Select", "query": triple}
                ]
            }
        ]
    }

    result = query._find_last_property(json_obj)

    assert result == triple
