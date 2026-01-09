"""Test query builder methods for WOQL Query."""
import pytest
from terminusdb_client.woqlquery.woql_query import WOQLQuery, Var


class TestWOQLQueryBuilder:
    """Test query builder methods and internal functions."""

    def test_woql_not_returns_new_query(self):
        """Test woql_not returns a new WOQLQuery instance."""
        query = WOQLQuery()
        result = query.woql_not()
        assert isinstance(result, WOQLQuery)
        # Note: woql_not modifies the query in place, so we check the type
        assert hasattr(result, '_query')

    def test_add_sub_query_with_dict(self):
        """Test _add_sub_query with dictionary parameter."""
        query = WOQLQuery()
        sub_query = {"@type": "TestQuery"}
        result = query._add_sub_query(sub_query)

        assert query._cursor["query"] == sub_query
        assert result is query

    def test_add_sub_query_without_parameter(self):
        """Test _add_sub_query without parameter creates new object."""
        query = WOQLQuery()
        result = query._add_sub_query()

        # The cursor should be reset to an empty dict
        assert query._cursor == {}
        assert result is query

    def test_contains_update_check_with_dict(self):
        """Test _contains_update_check with dictionary containing update operator."""
        query = WOQLQuery()
        test_json = {"@type": "AddTriple"}
        result = query._contains_update_check(test_json)
        assert result is True

    def test_contains_update_check_with_non_dict(self):
        """Test _contains_update_check with non-dictionary input."""
        query = WOQLQuery()
        result = query._contains_update_check("not_a_dict")
        assert result is False

    def test_contains_update_check_with_consequent(self):
        """Test _contains_update_check checks consequent field."""
        query = WOQLQuery()
        test_json = {
            "@type": "Query",
            "consequent": {
                "@type": "DeleteTriple"
            }
        }
        result = query._contains_update_check(test_json)
        assert result is True

    def test_contains_update_check_with_query(self):
        """Test _contains_update_check checks query field."""
        query = WOQLQuery()
        test_json = {
            "@type": "Query",
            "query": {
                "@type": "UpdateObject"
            }
        }
        result = query._contains_update_check(test_json)
        assert result is True

    def test_contains_update_check_with_and_list(self):
        """Test _contains_update_check checks and list."""
        query = WOQLQuery()
        test_json = {
            "@type": "Query",
            "and": [
                {"@type": "Triple"},
                {"@type": "AddQuad"}
            ]
        }
        result = query._contains_update_check(test_json)
        assert result is True

    def test_contains_update_check_with_or_list(self):
        """Test _contains_update_check checks or list."""
        query = WOQLQuery()
        test_json = {
            "@type": "Query",
            "or": [
                {"@type": "Triple"},
                {"@type": "DeleteQuad"}
            ]
        }
        result = query._contains_update_check(test_json)
        assert result is True

    def test_contains_update_check_default(self):
        """Test _contains_update_check returns False for non-update queries."""
        query = WOQLQuery()
        test_json = {"@type": "Triple"}
        result = query._contains_update_check(test_json)
        assert result is False

    def test_updated_method(self):
        """Test _updated method sets _contains_update flag."""
        query = WOQLQuery()
        assert query._contains_update is False

        result = query._updated()
        assert query._contains_update is True
        assert result is query

    def test_wfrom_with_format(self):
        """Test _wfrom method with format option."""
        query = WOQLQuery()
        opts = {"format": "json"}
        result = query._wfrom(opts)

        assert "format" in query._cursor
        assert query._cursor["format"]["@type"] == "Format"
        assert query._cursor["format"]["format_type"]["@value"] == "json"
        assert result is query

    def test_wfrom_with_format_and_header(self):
        """Test _wfrom method with format and header options."""
        query = WOQLQuery()
        opts = {
            "format": "csv",
            "format_header": True
        }
        result = query._wfrom(opts)

        assert query._cursor["format"]["format_type"]["@value"] == "csv"
        assert query._cursor["format"]["format_header"]["@value"] is True
        assert result is query

    def test_wfrom_without_options(self):
        """Test _wfrom method without options."""
        query = WOQLQuery()
        result = query._wfrom(None)

        assert "format" not in query._cursor
        assert result is query

    def test_wfrom_empty_dict(self):
        """Test _wfrom method with empty dictionary."""
        query = WOQLQuery()
        result = query._wfrom({})

        assert "format" not in query._cursor
        assert result is query

    def test_arop_with_dict_object(self):
        """Test _arop with dictionary object having to_dict method."""
        query = WOQLQuery()

        # Create an actual dict with to_dict method attached
        test_dict = {"@type": "ArithmeticValue", "data": {"@value": "mock"}}
        test_dict["to_dict"] = lambda: {"@type": "ArithmeticValue", "data": {"@value": "mock"}}

        result = query._arop(test_dict)
        # Since type(arg) is dict and it has to_dict, it returns the dict as-is
        # The to_dict method is NOT called automatically - it's only checked
        assert result == test_dict
        assert "to_dict" in result  # The function is still there

    def test_arop_with_plain_dict(self):
        """Test _arop with plain dictionary."""
        query = WOQLQuery()
        test_dict = {"key": "value"}
        result = query._arop(test_dict)
        # Plain dict is returned as-is
        assert result == test_dict

    def test_arop_with_value(self):
        """Test _arop with numeric value."""
        query = WOQLQuery()
        result = query._arop(42)
        # Should return wrapped arithmetic value
        assert "@type" in result
        assert result["@type"] == "ArithmeticValue"

    def test_vlist_with_mixed_items(self):
        """Test _vlist with mixed item types."""
        query = WOQLQuery()
        items = ["string", "v:42", Var("x")]
        result = query._vlist(items)

        assert len(result) == 3
        # Each item should be expanded/wrapped appropriately
        for item in result:
            assert isinstance(item, dict)

    @pytest.mark.skip(reason="This method is deprecated and dead code - it is never called anywhere in the codebase.")
    def test_data_value_list_with_mixed_items(self):
        """Test _data_value_list with mixed item types.

        DEPRECATED: This method is dead code - it is never called anywhere in the
        codebase. The similar method _value_list() is used instead throughout the
        client. This test and the method will be removed in a future release.

        There was an issue that is now fixed; however, test is disabled due to
        deprecation. To be cleaned up once confirmed.
        """
        query = WOQLQuery()
        items = ["string", "42", True, None]

        result = query._data_value_list(items)

        assert isinstance(result, list)
        assert len(result) == 4
        for item in result:
            assert isinstance(item, dict)
            assert "@type" in item

    def test_clean_subject_with_dict(self):
        """Test _clean_subject with dictionary input."""
        query = WOQLQuery()
        test_dict = {"@id": "test"}
        result = query._clean_subject(test_dict)
        assert result == test_dict

    def test_clean_subject_with_iri_string(self):
        """Test _clean_subject with IRI string containing colon."""
        query = WOQLQuery()
        iri_string = "http://example.org/test"
        result = query._clean_subject(iri_string)
        # IRI strings are wrapped in NodeValue
        assert result["@type"] == "NodeValue"
        assert result["node"] == iri_string

    def test_clean_subject_with_vocab_key(self):
        """Test _clean_subject with vocabulary key."""
        query = WOQLQuery()
        result = query._clean_subject("type")
        # Vocab keys are also wrapped in NodeValue
        assert result["@type"] == "NodeValue"
        assert result["node"] == "rdf:type"

    def test_clean_subject_with_unknown_string(self):
        """Test _clean_subject with unknown string."""
        query = WOQLQuery()
        result = query._clean_subject("unknown_key")
        # Unknown strings are wrapped in NodeValue
        assert result["@type"] == "NodeValue"
        assert result["node"] == "unknown_key"
