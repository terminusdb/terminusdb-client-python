import sys

from terminusdb_client.woqlclient.id_parser import IDParser

sys.path.append("woqlclient")


def test_parse_server_url():
    server_url = "http://localhost:6363/"
    id_parser = IDParser()
    assert id_parser.parse_server_url(server_url) == server_url


def test_parse_dbid():
    db_name = "myFirstTerminusDB"
    id_parser = IDParser()
    assert id_parser.parse_dbid(db_name) == db_name


def test_valid_url():
    full_url = "http://localhost:6363/myFirstTerminusDB"
    id_parser = IDParser()
    assert id_parser._valid_url(full_url)

    full_url = "localhost&899900/myFirstTerminusDB"
    assert not id_parser._valid_url(full_url)


def test_valid_id_string():
    id_string = "myFirstTerminusDB"
    id_parser = IDParser()
    assert id_parser._valid_id_string(id_string)
    id_string = "my First:"
    assert not id_parser._valid_id_string(id_string)
