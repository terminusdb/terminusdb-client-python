# from terminusdb_client.woqlclient.api_endpoint_const import APIEndpointConst
#
# from .connectCapabilitiesResponse import ConnectResponse
# from .getSchemaTurtleResponse import RESPONSE

#
# def mocked_requests(*args, **kwargs):
#     class MockResponse:
#         def json(self):
#             if self._json_data is None:
#                 raise ValueError("EXCEPTION NO JSON OBJECT")
#             return self._json_data
#
#         @property
#         def status_code(self):
#             return self._status_code
#
#         @property
#         def url(self):
#             return self._url
#
#         @property
#         def text(self):
#             return self._text
#
#         def __init__(self, url, status, action_type):
#
#             # set status code and content
#             self._json_data = None
#             self._text = None
#             self._status_code = status
#             self._content = "cont"
#             self._url = url
#             # add json data if provided
#
#             if action_type == APIEndpointConst.CONNECT:
#                 self._json_data = ConnectResponse
#
#             elif action_type == APIEndpointConst.GET_TRIPLES:
#                 self._text = RESPONSE
#
#             # elif action_type == APIEndpointConst.WOQL_SELECT:
#             #   with open("tests/getAllClassQueryResponse.json") as json_file:
#             #      json_data = json.load(json_file)
#             #     self._json_data = json_data
#             #    json_file.close()
#
#             elif (
#                 action_type == APIEndpointConst.CREATE_DATABASE
#                 or action_type == APIEndpointConst.DELETE_DATABASE
#                 or action_type == APIEndpointConst.UPDATE_TRIPLES
#                 or action_type == APIEndpointConst.BRANCH
#                 or action_type == APIEndpointConst.CREATE_GRAPH
#             ):
#                 self._json_data = {"terminus:status": "terminus:success"}
#
#     if (
#         args[0]
#         == "http://localhost:6363/branch/admin/myDBName/local/branch/my_new_branch"
#     ):
#         return MockResponse(args[0], 200, APIEndpointConst.BRANCH)
#
#     elif (
#         args[0]
#         == "http://localhost:6363/graph/admin/myDBName/local/branch/main/instance/mygraph"
#     ):
#         return MockResponse(args[0], 200, APIEndpointConst.CREATE_GRAPH)
#
#     elif (
#         args[0]
#         == "http://localhost:6363/triples/admin/myDBName/local/branch/main/instance/mygraph"
#     ):
#         return MockResponse(args[0], 200, APIEndpointConst.GET_TRIPLES)
#
#     elif args[0] == "http://localhost:6363/db/admin/myFirstTerminusDB":
#         return MockResponse(args[0], 200, APIEndpointConst.DELETE_DATABASE)
#
#     return MockResponse(args[0], 200, APIEndpointConst.CONNECT)


MOCK_CAPABILITIES = {
    "@context": {
        "api": "http://terminusdb.com/schema/api#",
        "doc": "terminusdb:///system/data/",
        "layer": "http://terminusdb.com/schema/layer#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "ref": "http://terminusdb.com/schema/ref#",
        "repo": "http://terminusdb.com/schema/repository#",
        "system": "http://terminusdb.com/schema/system#",
        "terminus": "http://terminusdb.com/schema/system#",
        "vio": "http://terminusdb.com/schema/vio#",
        "woql": "http://terminusdb.com/schema/woql#",
        "xdd": "http://terminusdb.com/schema/xdd#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    },
    "@id": "doc:admin",
    "@type": "system:User",
    "rdfs:comment": {
        "@language": "en",
        "@value": "This is the server super user account",
    },
    "rdfs:label": {"@language": "en", "@value": "Server Admin User"},
    "system:agent_name": {"@type": "xsd:string", "@value": "admin"},
    "system:role": {
        "@id": "doc:admin_role",
        "@type": "system:Role",
        "rdfs:comment": {
            "@language": "en",
            "@value": "Role providing admin capabilities",
        },
        "rdfs:label": {"@language": "en", "@value": "Admin Role"},
        "system:capability": {
            "@id": "doc:server_access",
            "@type": "system:Capability",
            "rdfs:comment": {"@language": "en", "@value": "Server wide access Object"},
            "rdfs:label": {"@language": "en", "@value": "server access capability"},
            "system:action": [
                {"@id": "system:branch", "@type": "system:DBAction"},
                {"@id": "system:class_frame", "@type": "system:DBAction"},
                {"@id": "system:clone", "@type": "system:DBAction"},
                {"@id": "system:commit_read_access", "@type": "system:DBAction"},
                {"@id": "system:commit_write_access", "@type": "system:DBAction"},
                {"@id": "system:create_database", "@type": "system:DBAction"},
                {"@id": "system:delete_database", "@type": "system:DBAction"},
                {"@id": "system:fetch", "@type": "system:DBAction"},
                {"@id": "system:inference_read_access", "@type": "system:DBAction"},
                {"@id": "system:inference_write_access", "@type": "system:DBAction"},
                {"@id": "system:instance_read_access", "@type": "system:DBAction"},
                {"@id": "system:instance_write_access", "@type": "system:DBAction"},
                {"@id": "system:manage_capabilities", "@type": "system:DBAction"},
                {"@id": "system:meta_read_access", "@type": "system:DBAction"},
                {"@id": "system:meta_write_access", "@type": "system:DBAction"},
                {"@id": "system:push", "@type": "system:DBAction"},
                {"@id": "system:rebase", "@type": "system:DBAction"},
                {"@id": "system:schema_read_access", "@type": "system:DBAction"},
                {"@id": "system:schema_write_access", "@type": "system:DBAction"},
            ],
            "system:capability_scope": [
                {
                    "@id": "doc:admin_organization",
                    "@type": "system:Organization",
                    "rdfs:comment": {"@language": "en", "@value": "Admin organization"},
                    "rdfs:label": {"@language": "en", "@value": "admin organization"},
                    "system:organization_database": {
                        "@id": "doc:system",
                        "@type": "system:SystemDatabase",
                    },
                    "system:organization_name": {
                        "@type": "xsd:string",
                        "@value": "admin",
                    },
                    "system:resource_includes": {
                        "@id": "doc:system",
                        "@type": "system:SystemDatabase",
                    },
                    "system:resource_name": {"@type": "xsd:string", "@value": "admin"},
                },
                {
                    "@id": "doc:system",
                    "@type": "system:SystemDatabase",
                    "rdfs:comment": {
                        "@language": "en",
                        "@value": "The system database contains the meta-data about databases, users and roles",
                    },
                    "rdfs:label": {"@language": "en", "@value": "System Database"},
                    "system:resource_name": {
                        "@type": "xsd:string",
                        "@value": "_system",
                    },
                },
            ],
        },
    },
    "system:user_key_hash": "",
}
