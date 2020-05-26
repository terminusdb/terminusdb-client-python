from woqlclient import IDParser

# import sys
# sys.path.append('woqlclient')


def test_parseServerURL():
    servURL = "http://localhost:6363/"
    idParser = IDParser()
    assert idParser.parse_server_url(servURL) == servURL


def test_parseDBID():
    dbName = "myFirstTerminusDB"
    idParser = IDParser()
    assert idParser.parse_dbid(dbName) == dbName


def test_validURL():
    fullURL = "http://localhost:6363/myFirstTerminusDB"
    idParser = IDParser()
    assert idParser._valid_url(fullURL) == True

    fullURL = "localhost&899900/myFirstTerminusDB"
    assert idParser._valid_url(fullURL) == False


def test_validIDString():
    idString = "myFirstTerminusDB"
    idParser = IDParser()
    assert idParser._valid_id_string(idString) == True
    idString = "my First:"
    assert idParser._valid_id_string(idString) == False
