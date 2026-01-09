"""Tests for woql_core.py"""

import pytest

from terminusdb_client.woqlquery.woql_core import (
    _split_at,
    _path_tokens_to_json,
    _path_or_parser,
    _group,
    _phrase_parser,
    _path_tokenize,
    _copy_dict,
)


class TestSplitAt:
    """Test _split_at function"""
    
    def test_split_at_basic(self):
        """Test basic splitting at operator"""
        tokens = ["a", ",", "b", ",", "c"]
        result = _split_at(",", tokens)
        assert result == [["a"], ["b"], ["c"]]
    
    def test_split_at_with_parentheses(self):
        """Test splitting respects parentheses"""
        tokens = ["a", "(", "b", ",", "c", ")", ",", "d"]
        result = _split_at(",", tokens)
        assert result == [["a", "(", "b", ",", "c", ")"], ["d"]]
    
    def test_split_at_with_braces(self):
        """Test splitting respects braces"""
        tokens = ["a", "{", "b", ",", "c", "}", ",", "d"]
        result = _split_at(",", tokens)
        assert result == [["a", "{", "b", ",", "c", "}"], ["d"]]
    
    def test_split_at_nested(self):
        """Test splitting with nested structures"""
        tokens = ["a", "(", "b", "{", "c", "}", ")", ",", "d"]
        result = _split_at(",", tokens)
        assert result == [["a", "(", "b", "{", "c", "}", ")"], ["d"]]
    
    def test_split_at_unbalanced_parentheses(self):
        """Test error on unbalanced parentheses"""
        tokens = ["a", "(", "b", ")", ")"]
        with pytest.raises(SyntaxError) as exc_info:
            _split_at(",", tokens)
        assert "Unbalanced parenthesis" in str(exc_info.value)
    
    def test_split_at_unbalanced_braces(self):
        """Test error on unbalanced braces"""
        tokens = ["a", "{", "b", "}", "}"]
        with pytest.raises(SyntaxError) as exc_info:
            _split_at(",", tokens)
        assert "Unbalanced parenthesis" in str(exc_info.value)
    
    def test_split_at_no_operator(self):
        """Test when operator not found"""
        tokens = ["a", "b", "c"]
        result = _split_at(",", tokens)
        assert result == [["a", "b", "c"]]
    
    def test_split_at_empty(self):
        """Test empty token list"""
        tokens = []
        result = _split_at(",", tokens)
        assert result == [[]]


class TestPathTokensToJson:
    """Test _path_tokens_to_json function"""
    
    def test_single_sequence(self):
        """Test single sequence returns directly"""
        tokens = ["a", "b", "c"]
        result = _path_tokens_to_json(tokens)
        assert result == {"@type": "PathPredicate", "predicate": "c"}
    
    def test_multiple_sequences(self):
        """Test multiple sequences create PathSequence"""
        tokens = ["a", ",", "b", ",", "c"]
        result = _path_tokens_to_json(tokens)
        assert result["@type"] == "PathSequence"
        assert len(result["sequence"]) == 3
    
    def test_complex_sequence(self):
        """Test complex sequence with groups"""
        tokens = ["a", "(", "b", "|", "c", ")", ",", "d"]
        result = _path_tokens_to_json(tokens)
        assert result["@type"] == "PathSequence"


class TestPathOrParser:
    """Test _path_or_parser function"""
    
    def test_single_phrase(self):
        """Test single phrase returns directly"""
        tokens = ["a", "b", "c"]
        result = _path_or_parser(tokens)
        assert result == {"@type": "PathPredicate", "predicate": "c"}
    
    def test_multiple_phrases(self):
        """Test multiple phrases create PathOr"""
        tokens = ["a", "|", "b", "|", "c"]
        result = _path_or_parser(tokens)
        assert result["@type"] == "PathOr"
        assert len(result["or"]) == 3
    
    def test_complex_or(self):
        """Test complex or with groups"""
        tokens = ["a", "(", "b", ",", "c", ")", "|", "d"]
        result = _path_or_parser(tokens)
        assert result["@type"] == "PathOr"


class TestGroup:
    """Test _group function"""
    
    def test_simple_group(self):
        """Test simple group extraction"""
        tokens = ["a", "(", "b", "c", ")", "d"]
        result = _group(tokens)
        assert result == ["a", "(", "b", "c", ")"]
        assert tokens == ["d"]
    
    def test_nested_group(self):
        """Test nested group extraction"""
        tokens = ["a", "(", "b", "(", "c", ")", ")", "d"]
        result = _group(tokens)
        assert result == ["a", "(", "b", "(", "c", ")", ")"]
        assert tokens == ["d"]
    
    def test_group_at_end(self):
        """Test group at end of tokens"""
        tokens = ["a", "(", "b", "c", ")"]
        result = _group(tokens)
        assert result == ["a", "(", "b", "c"]
        assert tokens == [")"]


class TestPhraseParser:
    """Test _phrase_parser function"""
    
    def test_simple_predicate(self):
        """Test simple predicate"""
        tokens = ["parentOf"]
        result = _phrase_parser(tokens)
        assert result == {"@type": "PathPredicate", "predicate": "parentOf"}
    
    def test_inverse_path(self):
        """Test inverse path with < >"""
        tokens = ["<", "parentOf", ">"]
        result = _phrase_parser(tokens)
        assert result == {"@type": "InversePathPredicate", "predicate": "parentOf"}
    
    def test_path_predicate(self):
        """Test path predicate"""
        tokens = ["."]
        result = _phrase_parser(tokens)
        assert result == {"@type": "PathPredicate"}
    
    def test_path_star(self):
        """Test path star"""
        tokens = ["parentOf", "*"]
        result = _phrase_parser(tokens)
        assert result == {"@type": "PathStar", "star": {"@type": "PathPredicate", "predicate": "parentOf"}}
    
    def test_path_plus(self):
        """Test path plus"""
        tokens = ["parentOf", "+"]
        result = _phrase_parser(tokens)
        assert result == {"@type": "PathPlus", "plus": {"@type": "PathPredicate", "predicate": "parentOf"}}
    
    def test_path_times(self):
        """Test path times with {n,m}"""
        tokens = ["parentOf", "{", "1", ",", "3", "}"]
        result = _phrase_parser(tokens)
        assert result == {
            "@type": "PathTimes",
            "from": 1,
            "to": 3,
            "times": {"@type": "PathPredicate", "predicate": "parentOf"}
        }
    
    def test_path_times_error_no_comma(self):
        """Test error when no comma in path times"""
        tokens = ["parentOf", "{", "1", "3", "}"]
        with pytest.raises(ValueError) as exc_info:
            _phrase_parser(tokens)
        assert "incorrect separation" in str(exc_info.value)
    
    def test_path_times_error_no_brace(self):
        """Test error when no closing brace"""
        tokens = ["parentOf", "{", "1", ",", "3", ")"]
        with pytest.raises(ValueError) as exc_info:
            _phrase_parser(tokens)
        assert "no matching brace" in str(exc_info.value)
    
    def test_grouped_phrase(self):
        """Test phrase with group"""
        tokens = ["(", "a", "|", "b", ")"]
        result = _phrase_parser(tokens)
        assert result["@type"] == "PathOr"
    
    def test_complex_phrase(self):
        """Test complex phrase combination"""
        tokens = ["parentOf", "*", "(", "knows", "|", "likes", ")", "+"]
        result = _phrase_parser(tokens)
        assert result["@type"] == "PathPlus"


class TestPathTokenize:
    """Test _path_tokenize function"""
    
    def test_simple_tokenize(self):
        """Test simple tokenization"""
        pat = "parentOf"
        result = _path_tokenize(pat)
        assert result == ["parentOf"]
    
    def test_tokenize_with_operators(self):
        """Test tokenization with operators"""
        pat = "parentOf.knows"
        result = _path_tokenize(pat)
        assert "." in result
        assert "parentOf" in result
        assert "knows" in result
    
    def test_tokenize_with_groups(self):
        """Test tokenization with groups"""
        pat = "(parentOf|knows)"
        result = _path_tokenize(pat)
        assert "(" in result
        assert ")" in result
        assert "|" in result
    
    def test_tokenize_complex(self):
        """Test complex pattern tokenization"""
        pat = "parentOf*{1,3}"
        result = _path_tokenize(pat)
        assert "parentOf" in result
        assert "*" in result
        assert "{" in result
        assert "}" in result
    
    def test_tokenize_with_special_chars(self):
        """Test tokenization with special characters"""
        pat = "friend_of:@test"
        result = _path_tokenize(pat)
        assert "friend_of:@test" in result
    
    def test_tokenize_with_quotes(self):
        """Test tokenization with quoted strings"""
        pat = "prop:'test value'"
        result = _path_tokenize(pat)
        assert "prop:'test" in result
        assert "value'" in result


class TestCopyDict:
    """Test _copy_dict function"""
    
    def test_copy_simple_dict(self):
        """Test copying simple dictionary"""
        orig = {"a": 1, "b": 2}
        result = _copy_dict(orig)
        assert result == orig
    
    def test_copy_list(self):
        """Test copying list returns as-is"""
        orig = [1, 2, 3]
        result = _copy_dict(orig)
        assert result is orig
    
    def test_copy_with_rollup_and_empty(self):
        """Test rollup with empty And"""
        orig = {"@type": "And", "and": []}
        result = _copy_dict(orig, rollup=True)
        assert result == {}
    
    def test_copy_with_rollup_and_single(self):
        """Test rollup with single item in And"""
        orig = {"@type": "And", "and": [{"@type": "Test", "value": 1}]}
        result = _copy_dict(orig, rollup=True)
        assert result == {"@type": "Test", "value": 1}
    
    def test_copy_with_rollup_or_empty(self):
        """Test rollup with empty Or"""
        orig = {"@type": "Or", "or": []}
        result = _copy_dict(orig, rollup=True)
        assert result == {}
    
    def test_copy_with_rollup_or_single(self):
        """Test rollup with single item in Or"""
        orig = {"@type": "Or", "or": [{"@type": "Test", "value": 1}]}
        result = _copy_dict(orig, rollup=True)
        assert result == {"@type": "Test", "value": 1}
    
    def test_copy_with_query_tuple(self):
        """Test copying with query as tuple"""
        class MockQuery:
            def to_dict(self):
                return {"@type": "Query", "select": "x"}
        
        orig = {"@type": "Test", "query": (MockQuery(),)}
        result = _copy_dict(orig, rollup=True)
        assert result["query"] == {"@type": "Query", "select": "x"}
    
    def test_copy_with_no_type_query(self):
        """Test copying with query having no @type"""
        orig = {"@type": "Test", "query": {"select": "x"}}
        result = _copy_dict(orig, rollup=True)
        assert result == {}
    
    def test_copy_with_consequent_no_type(self):
        """Test copying with consequent having no @type"""
        orig = {"@type": "Test", "consequent": {"select": "x"}}
        result = _copy_dict(orig, rollup=True)
        assert result == {}
    
    def test_copy_with_list_of_dicts(self):
        """Test copying list with dictionaries"""
        orig = {"items": [{"@type": "Item", "value": 1}, {"@type": "Item", "value": 2}]}
        result = _copy_dict(orig)
        assert len(result["items"]) == 2
        assert result["items"][0]["value"] == 1
    
    def test_copy_with_nested_dict(self):
        """Test copying nested dictionary"""
        orig = {"nested": {"@type": "Nested", "value": 1}}
        result = _copy_dict(orig)
        assert result["nested"]["value"] == 1
    
    def test_copy_with_to_dict_object(self):
        """Test copying object with to_dict method"""
        class MockObj:
            def to_dict(self):
                return {"converted": True}
        
        orig = {"obj": MockObj()}
        result = _copy_dict(orig)
        assert result["obj"] == {"converted": True}
    
    def test_copy_empty_dict(self):
        """Test copying empty dictionary"""
        orig = {}
        result = _copy_dict(orig)
        assert result == {}
    
    def test_copy_with_empty_list_in_dict(self):
        """Test copying dictionary with empty list"""
        orig = {"items": []}
        result = _copy_dict(orig)
        assert result == {"items": []}
    
    def test_copy_with_list_of_non_dicts(self):
        """Test copying list with non-dict items"""
        orig = {"items": [1, "string", True]}
        result = _copy_dict(orig)
        assert result == {"items": [1, "string", True]}
