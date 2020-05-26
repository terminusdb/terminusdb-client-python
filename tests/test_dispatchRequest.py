import unittest.mock as mock

# import sys
import requests
from mockResponse import mocked_requests
from woqlclient import DispatchRequest, DocumentTemplate, const


def sendDispatchRequest(url, actionType, key, payload={}):
    return DispatchRequest.sendRequestByAction(url, actionType, key, payload)


@mock.patch("requests.get", side_effect=mocked_requests)
def test_connectCall(mocked_requests):
    # Assert requests.get calls
    # assert (1 == 2) == True
    json_data = sendDispatchRequest("http://localhost:6363/", const.CONNECT, "mykey")

    requests.get.assert_called_once_with(
        "http://localhost:6363/", headers={"Authorization": "Basic Om15a2V5"}
    )


@mock.patch("requests.post", side_effect=mocked_requests)
def test_createDataBase(mocked_requests):
    fullUrl = "http://localhost:6363/myFirstTerminusDB"

    payload = DocumentTemplate.createDBTemplate(
        "http://localhost:6363/",
        "myFirstTerminusDB",
        "my first terminusDB",
        comment="test terminusDB",
    )
    sendDispatchRequest(fullUrl, const.CREATE_DATABASE, "mykey", payload)
    # requests.post.assert_called_once_with('http://localhost:6363/myFirstTerminusDB', headers={'Authorization': 'Basic Om15a2V5', 'content-type': 'application/json'}, json={'@context': {'rdfs': 'http://www.w3.org/2000/01/rdf-schema#', 'terminus': 'http://terminusdb.com/schema/terminus#', '_': 'http://localhost:6363/myFirstTerminusDB/'}, 'terminus:document': {'@type': 'terminus:Database', 'rdfs:label': {'@language': 'en', '@value': 'my first terminusDB'}, 'rdfs:comment': {'@language': 'en', '@value': 'test terminusDB'}, 'terminus:allow_origin': {'@type': 'xsd:string', '@value': '*'}, '@id': 'http://localhost:6363/myFirstTerminusDB'}, '@type': 'terminus:APIUpdate'})


@mock.patch("requests.get", side_effect=mocked_requests)
def test_getSchema(mocked_requests):
    payload = {"terminus:encoding": "terminus:turtle"}
    string_data = sendDispatchRequest(
        "http://localhost:6363/myFirstTerminusDB/schema",
        const.CONNECT,
        "mykey",
        payload,
    )
    requests.get.assert_called_once_with(
        "http://localhost:6363/myFirstTerminusDB/schema?terminus%3Aencoding=terminus%3Aturtle",
        headers={"Authorization": "Basic Om15a2V5"},
    )


@mock.patch("requests.get", side_effect=mocked_requests)
def test_woqlSelect(mocked_requests):
    payload = {
        "terminus:query": '{"@context":{"s":"http://localhost:6363/myFirstTerminusDB/schema#","dg":"http://localhost:6363/myFirstTerminusDB/schema","doc":"http://localhost:6363/myFirstTerminusDB/document/","db":"http://localhost:6363/myFirstTerminusDB/","g":"http://localhost:6363/","rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#","xsd":"http://www.w3.org/2001/XMLSchema#","owl":"http://www.w3.org/2002/07/owl#","tcs":"http://terminusdb.com/schema/tcs#","tbs":"http://terminusdb.com/schema/tbs#","xdd":"http://terminusdb.com/schema/xdd#","terminus":"http://terminusdb.com/schema/terminus#","vio":"http://terminusdb.com/schema/vio#","docs":"http://terminusdb.com/schema/documentation#","scm":"http://localhost:6363/myFirstTerminusDB/schema#"},"from":["http://localhost:6363/myFirstTerminusDB",{"limit":[20,{"start":[0,{"and":[{"quad":["v:Element","rdf:type","owl:Class","db:schema"]},{"opt":[{"quad":["v:Element","rdfs:label","v:Label","db:schema"]}]},{"opt":[{"quad":["v:Element","rdfs:comment","v:Comment","db:schema"]}]},{"opt":[{"quad":["v:Element","tcs:tag","v:Abstract","db:schema"]}]}]}]}]}]}'
    }
    fullUrl = "http://localhost:6363/myFirstTerminusDB/woql"
    sendDispatchRequest(fullUrl, const.WOQL_SELECT, "mykey", payload)
    requests.get.assert_called_once_with(
        "http://localhost:6363/myFirstTerminusDB/woql?terminus%3Aquery=%7B%22%40context%22%3A%7B%22s%22%3A%22http%3A%2F%2Flocalhost%3A6363%2FmyFirstTerminusDB%2Fschema%23%22%2C%22dg%22%3A%22http%3A%2F%2Flocalhost%3A6363%2FmyFirstTerminusDB%2Fschema%22%2C%22doc%22%3A%22http%3A%2F%2Flocalhost%3A6363%2FmyFirstTerminusDB%2Fdocument%2F%22%2C%22db%22%3A%22http%3A%2F%2Flocalhost%3A6363%2FmyFirstTerminusDB%2F%22%2C%22g%22%3A%22http%3A%2F%2Flocalhost%3A6363%2F%22%2C%22rdf%22%3A%22http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%22%2C%22rdfs%22%3A%22http%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%22%2C%22xsd%22%3A%22http%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%22%2C%22owl%22%3A%22http%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%22%2C%22tcs%22%3A%22http%3A%2F%2Fterminusdb.com%2Fschema%2Ftcs%23%22%2C%22tbs%22%3A%22http%3A%2F%2Fterminusdb.com%2Fschema%2Ftbs%23%22%2C%22xdd%22%3A%22http%3A%2F%2Fterminusdb.com%2Fschema%2Fxdd%23%22%2C%22terminus%22%3A%22http%3A%2F%2Fterminusdb.com%2Fschema%2Fterminus%23%22%2C%22vio%22%3A%22http%3A%2F%2Fterminusdb.com%2Fschema%2Fvio%23%22%2C%22docs%22%3A%22http%3A%2F%2Fterminusdb.com%2Fschema%2Fdocumentation%23%22%2C%22scm%22%3A%22http%3A%2F%2Flocalhost%3A6363%2FmyFirstTerminusDB%2Fschema%23%22%7D%2C%22from%22%3A%5B%22http%3A%2F%2Flocalhost%3A6363%2FmyFirstTerminusDB%22%2C%7B%22limit%22%3A%5B20%2C%7B%22start%22%3A%5B0%2C%7B%22and%22%3A%5B%7B%22quad%22%3A%5B%22v%3AElement%22%2C%22rdf%3Atype%22%2C%22owl%3AClass%22%2C%22db%3Aschema%22%5D%7D%2C%7B%22opt%22%3A%5B%7B%22quad%22%3A%5B%22v%3AElement%22%2C%22rdfs%3Alabel%22%2C%22v%3ALabel%22%2C%22db%3Aschema%22%5D%7D%5D%7D%2C%7B%22opt%22%3A%5B%7B%22quad%22%3A%5B%22v%3AElement%22%2C%22rdfs%3Acomment%22%2C%22v%3AComment%22%2C%22db%3Aschema%22%5D%7D%5D%7D%2C%7B%22opt%22%3A%5B%7B%22quad%22%3A%5B%22v%3AElement%22%2C%22tcs%3Atag%22%2C%22v%3AAbstract%22%2C%22db%3Aschema%22%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D",
        headers={"Authorization": "Basic Om15a2V5"},
    )


@mock.patch("requests.delete", side_effect=mocked_requests)
def test_deleteDatabase(mocked_requests):
    fullUrl = "http://localhost:6363/myFirstTerminusDB"
    sendDispatchRequest(fullUrl, const.DELETE_DATABASE, "mykey")
    requests.delete.assert_called_once_with(
        "http://localhost:6363/myFirstTerminusDB",
        headers={"Authorization": "Basic Om15a2V5"},
    )
    # print("call_args_list", requests.delete.call_args_list)
