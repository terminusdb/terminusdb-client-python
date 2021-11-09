from terminusdb_client.woqlquery.woql_core import _get_clause_and_remainder, _tokenize


def test_get_clause_and_remainder():
    result = _get_clause_and_remainder("((capability_userstory|userstory_gap){1,2})")
    assert result == ["capability_userstory|userstory_gap", "{1,2}"]


def test_tokenize():
    result = _tokenize("((capability_userstory|userstory_gap){1,2})")
    assert result == ["capability_userstory|userstory_gap", "{1,2}"]
