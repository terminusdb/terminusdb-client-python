from terminusdb_client.woqlquery.woql_core import _path_tokenize


def test_tokenize():
    result = _path_tokenize("((capability_userstory|userstory_gap){1,2})")
    assert result == [
        "(",
        "(",
        "capability_userstory",
        "|",
        "userstory_gap",
        ")",
        "{",
        "1",
        ",",
        "2",
        "}",
        ")",
    ]
