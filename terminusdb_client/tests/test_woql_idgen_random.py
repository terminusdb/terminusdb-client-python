"""Unit tests for idgen_random WOQL method"""
from terminusdb_client.woqlquery.woql_query import WOQLQuery


class TestIdgenRandom:
    """Test idgen_random WOQL method"""

    def test_idgen_random_basic(self):
        """Test basic idgen_random functionality"""
        woql = WOQLQuery().idgen_random("Person/", "v:PersonID")
        result = woql.to_dict()

        assert result["@type"] == "RandomKey"
        assert result["base"]["@type"] == "DataValue"
        assert result["base"]["data"]["@type"] == "xsd:string"
        assert result["base"]["data"]["@value"] == "Person/"
        assert result["uri"]["@type"] == "NodeValue"
        assert result["uri"]["variable"] == "PersonID"

    def test_idgen_random_with_prefix(self):
        """Test idgen_random with different prefix formats"""
        woql = WOQLQuery().idgen_random("http://example.org/Person/", "v:ID")
        result = woql.to_dict()

        assert result["base"]["data"]["@value"] == "http://example.org/Person/"
        assert result["uri"]["variable"] == "ID"

    def test_idgen_random_chaining(self):
        """Test idgen_random can be chained with other operations"""
        woql = (WOQLQuery()
                .triple("v:Person", "rdf:type", "@schema:Person")
                .idgen_random("Person/", "v:PersonID"))

        result = woql.to_dict()
        assert result["@type"] == "And"
        assert len(result["and"]) == 2
        assert result["and"][0]["@type"] == "Triple"
        assert result["and"][1]["@type"] == "RandomKey"

    def test_idgen_random_multiple_calls(self):
        """Test multiple idgen_random calls in same query"""
        woql = (WOQLQuery()
                .idgen_random("Person/", "v:PersonID")
                .idgen_random("Order/", "v:OrderID"))

        result = woql.to_dict()
        assert result["@type"] == "And"
        assert result["and"][0]["@type"] == "RandomKey"
        assert result["and"][0]["base"]["data"]["@value"] == "Person/"
        assert result["and"][1]["@type"] == "RandomKey"
        assert result["and"][1]["base"]["data"]["@value"] == "Order/"

    def test_idgen_random_args_parameter(self):
        """Test idgen_random args parameter returns parameter list"""
        result = WOQLQuery().idgen_random("args", "v:ID")

        assert result == ["base", "uri"]

    def test_idgen_random_empty_prefix(self):
        """Test idgen_random with empty prefix"""
        woql = WOQLQuery().idgen_random("", "v:ID")
        result = woql.to_dict()

        assert result["@type"] == "RandomKey"
        assert result["base"]["data"]["@value"] == ""

    def test_idgen_random_variable_output(self):
        """Test idgen_random output variable format"""
        woql = WOQLQuery().idgen_random("Test/", "v:MyVar")
        result = woql.to_dict()

        assert result["uri"]["variable"] == "MyVar"

    def test_idgen_random_in_query_chain(self):
        """Test idgen_random in complex query chain"""
        woql = (WOQLQuery()
                .triple("v:Person", "rdf:type", "@schema:Person")
                .idgen_random("Person/", "v:PersonID")
                .triple("v:PersonID", "@schema:name", "v:Name"))

        result = woql.to_dict()
        assert result["@type"] == "And"
        # WOQLQuery chains create nested And structures
        # Verify RandomKey is present in the chain
        has_random_key = False

        def check_for_random_key(obj):
            nonlocal has_random_key
            if isinstance(obj, dict):
                if obj.get("@type") == "RandomKey":
                    has_random_key = True
                for value in obj.values():
                    check_for_random_key(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_for_random_key(item)

        check_for_random_key(result)
        assert has_random_key, "RandomKey should be present in query chain"

    def test_idgen_random_matches_expected_json(self):
        """Test idgen_random produces expected WOQL JSON structure"""
        from terminusdb_client.tests.woqljson.woqlIdgenJson import WOQL_RANDOM_KEY_JSON

        woql = WOQLQuery().idgen_random("Person/", "v:Person_ID")
        result = woql.to_dict()

        assert result == WOQL_RANDOM_KEY_JSON

    def test_idgen_random_with_special_characters_in_prefix(self):
        """Test idgen_random handles special characters in prefix"""
        woql = WOQLQuery().idgen_random("Test/2024-11/", "v:ID")
        result = woql.to_dict()

        assert result["base"]["data"]["@value"] == "Test/2024-11/"

    def test_idgen_random_preserves_cursor_state(self):
        """Test idgen_random returns self for method chaining"""
        woql = WOQLQuery()
        result = woql.idgen_random("Test/", "v:ID")

        assert result is woql  # Should return same object for chaining
