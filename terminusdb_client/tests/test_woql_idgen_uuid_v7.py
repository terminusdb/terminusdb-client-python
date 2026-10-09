"""Unit tests for idgen_uuid_v7 WOQL method"""

from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestIdgenUuidV7:
    """Test idgen_uuid_v7 WOQL method"""

    def test_idgen_uuid_v7_basic(self):
        """Test basic idgen_uuid_v7 functionality"""
        woql = WOQLQuery().idgen_uuid_v7("Person/", "v:PersonID")
        result = woql.to_dict()

        assert result["@type"] == "UuidV7"
        assert result["base"]["@type"] == "DataValue"
        assert result["base"]["data"]["@type"] == "xsd:string"
        assert result["base"]["data"]["@value"] == "Person/"
        assert result["uri"]["@type"] == "NodeValue"
        assert result["uri"]["variable"] == "PersonID"

    def test_idgen_uuid_v7_with_prefix(self):
        """Test idgen_uuid_v7 with different prefix formats"""
        woql = WOQLQuery().idgen_uuid_v7("http://example.org/Person/", "v:ID")
        result = woql.to_dict()

        assert result["base"]["data"]["@value"] == "http://example.org/Person/"
        assert result["uri"]["variable"] == "ID"

    def test_idgen_uuid_v7_chaining(self):
        """Test idgen_uuid_v7 can be chained with other operations"""
        woql = (
            WOQLQuery()
            .triple("v:Person", "rdf:type", "@schema:Person")
            .idgen_uuid_v7("Person/", "v:PersonID")
        )

        result = woql.to_dict()
        assert result["@type"] == "And"
        assert len(result["and"]) == 2
        assert result["and"][0]["@type"] == "Triple"
        assert result["and"][1]["@type"] == "UuidV7"

    def test_idgen_uuid_v7_multiple_calls(self):
        """Test multiple idgen_uuid_v7 calls in same query"""
        woql = (
            WOQLQuery()
            .idgen_uuid_v7("Person/", "v:PersonID")
            .idgen_uuid_v7("Order/", "v:OrderID")
        )

        result = woql.to_dict()
        assert result["@type"] == "And"
        assert result["and"][0]["@type"] == "UuidV7"
        assert result["and"][0]["base"]["data"]["@value"] == "Person/"
        assert result["and"][1]["@type"] == "UuidV7"
        assert result["and"][1]["base"]["data"]["@value"] == "Order/"

    def test_idgen_uuid_v7_args_parameter(self):
        """Test idgen_uuid_v7 args parameter returns parameter list"""
        result = WOQLQuery().idgen_uuid_v7("args", "v:ID")

        assert result == ["base", "uri"]

    def test_idgen_uuid_v7_empty_prefix(self):
        """Test idgen_uuid_v7 with empty prefix"""
        woql = WOQLQuery().idgen_uuid_v7("", "v:ID")
        result = woql.to_dict()

        assert result["@type"] == "UuidV7"
        assert result["base"]["data"]["@value"] == ""

    def test_idgen_uuid_v7_variable_output(self):
        """Test idgen_uuid_v7 output variable format"""
        woql = WOQLQuery().idgen_uuid_v7("Test/", "v:MyVar")
        result = woql.to_dict()

        assert result["uri"]["variable"] == "MyVar"

    def test_idgen_uuid_v7_in_query_chain(self):
        """Test idgen_uuid_v7 in complex query chain"""
        woql = (
            WOQLQuery()
            .triple("v:Person", "rdf:type", "@schema:Person")
            .idgen_uuid_v7("Person/", "v:PersonID")
            .triple("v:PersonID", "@schema:name", "v:Name")
        )

        result = woql.to_dict()
        assert result["@type"] == "And"
        # WOQLQuery chains create nested And structures
        # Verify UuidV7 is present in the chain
        has_uuid_v7 = False

        def check_for_uuid_v7(obj):
            nonlocal has_uuid_v7
            if isinstance(obj, dict):
                if obj.get("@type") == "UuidV7":
                    has_uuid_v7 = True
                for value in obj.values():
                    check_for_uuid_v7(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_for_uuid_v7(item)

        check_for_uuid_v7(result)
        assert has_uuid_v7, "UuidV7 should be present in query chain"

    def test_idgen_uuid_v7_matches_expected_json(self):
        """Test idgen_uuid_v7 produces expected WOQL JSON structure"""
        from terminusdb_client.tests.woqljson.woqlIdgenJson import (
            WOQL_UUID_V7_KEY_JSON,
        )

        woql = WOQLQuery().idgen_uuid_v7("Person/", "v:Person_ID")
        result = woql.to_dict()

        assert result == WOQL_UUID_V7_KEY_JSON

    def test_idgen_uuid_v7_with_special_characters_in_prefix(self):
        """Test idgen_uuid_v7 handles special characters in prefix"""
        woql = WOQLQuery().idgen_uuid_v7("Test/2024-11/", "v:ID")
        result = woql.to_dict()

        assert result["base"]["data"]["@value"] == "Test/2024-11/"

    def test_idgen_uuid_v7_preserves_cursor_state(self):
        """Test idgen_uuid_v7 returns self for method chaining"""
        woql = WOQLQuery()
        result = woql.idgen_uuid_v7("Test/", "v:ID")

        assert result is woql  # Should return same object for chaining
