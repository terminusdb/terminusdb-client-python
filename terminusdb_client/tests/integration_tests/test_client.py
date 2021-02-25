import pytest

from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.woql_query import WOQLQuery


def test_rollback(docker_url):
    client = WOQLClient(docker_url)
    client.connect()
    client.create_database("test_rollback")
    init_commit = client._get_current_commit()
    WOQLQuery().doctype("Station").execute(client)
    assert client._commit_made == 1
    first_commit = client._get_current_commit()
    assert first_commit != init_commit
    client.rollback()
    assert client._commit_made == 0
    assert client._get_current_commit() == init_commit

    WOQLQuery().doctype("Station").execute(client)
    WOQLQuery().doctype("Journey").execute(client)
    assert client._commit_made == 2
    second_commit = client._get_current_commit()
    assert second_commit != init_commit
    client.rollback(2)
    assert client._commit_made == 0
    assert client._get_current_commit() == init_commit

    WOQLQuery().doctype("Station").execute(client)
    assert client._commit_made == 1
    with pytest.raises(ValueError):
        client.rollback(2)
