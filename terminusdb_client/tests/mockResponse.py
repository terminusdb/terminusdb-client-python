from terminusdb_client.woqlclient.api_endpoint_const import APIEndpointConst

from .connectCapabilitiesResponse import ConnectResponse
from .getSchemaTurtleResponse import RESPONSE


def mocked_requests(*args, **kwargs):
    class MockResponse:
        def json(self):
            if self._json_data is None:
                raise ValueError("EXCEPTION NO JSON OBJECT")
            return self._json_data

        @property
        def status_code(self):
            return self._status_code

        @property
        def url(self):
            return self._url

        @property
        def text(self):
            return self._text

        def __init__(self, url, status, action_type):

            # set status code and content
            self._json_data = None
            self._text = None
            self._status_code = status
            self._content = "cont"
            self._url = url
            # add json data if provided

            if action_type == APIEndpointConst.CONNECT:
                self._json_data = ConnectResponse

            elif action_type == APIEndpointConst.GET_TRIPLES:
                self._text = RESPONSE

            # elif action_type == APIEndpointConst.WOQL_SELECT:
            #   with open("tests/getAllClassQueryResponse.json") as json_file:
            #      json_data = json.load(json_file)
            #     self._json_data = json_data
            #    json_file.close()

            elif (
                action_type == APIEndpointConst.CREATE_DATABASE
                or action_type == APIEndpointConst.DELETE_DATABASE
                or action_type == APIEndpointConst.UPDATE_TRIPLES
                or action_type == APIEndpointConst.BRANCH
                or action_type == APIEndpointConst.CREATE_GRAPH
            ):
                self._json_data = {"terminus:status": "terminus:success"}

    if (
        args[0]
        == "http://localhost:6363/branch/admin/myDBName/local/branch/my_new_branch"
    ):
        return MockResponse(args[0], 200, APIEndpointConst.BRANCH)

    elif (
        args[0]
        == "http://localhost:6363/graph/admin/myDBName/local/branch/main/instance/mygraph"
    ):
        return MockResponse(args[0], 200, APIEndpointConst.CREATE_GRAPH)

    elif (
        args[0]
        == "http://localhost:6363/triples/admin/myDBName/local/branch/main/instance/mygraph"
    ):
        return MockResponse(args[0], 200, APIEndpointConst.GET_TRIPLES)

    elif args[0] == "http://localhost:6363/db/admin/myFirstTerminusDB":
        return MockResponse(args[0], 200, APIEndpointConst.DELETE_DATABASE)

    return MockResponse(args[0], 200, APIEndpointConst.CONNECT)
