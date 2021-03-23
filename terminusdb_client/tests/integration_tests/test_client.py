import csv
import filecmp
import os

import pytest

from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.woql_query import WOQLQuery


def test_happy_path(docker_url):
    # create client
    client = WOQLClient(docker_url)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.create_database("test_happy_path", prefixes={"doc": "foo://"})
    init_commit = client._get_current_commit()
    assert client._db == "test_happy_path"
    assert "test_happy_path" in client.list_databases()
    assert client._context.get("doc") == "foo://"
    # test adding doctype
    WOQLQuery().doctype("Station").execute(client)
    assert client._commit_made == 1
    first_commit = client._get_current_commit()
    assert first_commit != init_commit
    # test rollback
    client.rollback()
    assert client._commit_made == 0  # back to squre 1
    assert client._get_current_commit() == init_commit
    # test rollback twice
    WOQLQuery().doctype("Station").execute(client)
    WOQLQuery().doctype("Journey").execute(client)
    assert client._commit_made == 2
    second_commit = client._get_current_commit()
    assert second_commit != init_commit
    client.rollback(2)
    assert client._commit_made == 0  # back to squre 1
    assert client._get_current_commit() == init_commit
    # test rollback too much
    WOQLQuery().doctype("Station").execute(client)
    assert client._commit_made == 1
    with pytest.raises(ValueError):
        client.rollback(2)
    client.delete_database("test_happy_path", "admin")
    assert client._db is None
    assert "test_happy_path" not in client.list_databases()


def _generate_csv():
    file_path = "employee_file.csv"
    with open(file_path, mode="w") as employee_file:
        employee_writer = csv.writer(
            employee_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        employee_writer.writerow(["John Smith", "Accounting", "November"])
        employee_writer.writerow(["Erica Meyers", "IT", "March"])
    return file_path


def _file_clean_up(filename):
    if os.path.exists(filename):
        os.remove(filename)


def test_csv_handeling(docker_url):
    client = WOQLClient(docker_url)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.create_database("test_csv")
    client._get_current_commit()
    assert client._db == "test_csv"
    assert "test_csv" in client.list_databases()
    csv_file_path = _generate_csv()  # create testing csv
    try:
        client.insert_csv(csv_file_path)
        client.get_csv(csv_file_path, csv_output_name="new_" + csv_file_path)
        assert filecmp.cmp(csv_file_path, "new_" + csv_file_path)
    finally:
        _file_clean_up(csv_file_path)
        _file_clean_up("new_" + csv_file_path)


def test_create_graph(docker_url):
    client = WOQLClient(docker_url)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.create_database("test_graph")
    client.create_graph("instance", "test-one-more-graph", "create test graph")
    client.delete_graph("instance", "test-one-more-graph", "delete test graph")
