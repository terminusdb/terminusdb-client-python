connect_response = {
    "@context": {
        "doc": "terminus:///terminus/document/",
        "layer": "http://terminusdb.com/schema/layer#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "ref": "http://terminusdb.com/schema/ref#",
        "repo": "http://terminusdb.com/schema/repository#",
        "terminus": "http://terminusdb.com/schema/terminus#",
        "vio": "http://terminusdb.com/schema/vio#",
        "woql": "http://terminusdb.com/schema/woql#",
        "xdd": "http://terminusdb.com/schema/xdd#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    },
    "@id": "doc:admin",
    "@type": "terminus:User",
    "rdfs:comment": {
        "@language": "en",
        "@value": "This is the server super user account",
    },
    "rdfs:label": {"@language": "en", "@value": "Server Admin User"},
    "terminus:agent_key_hash": {
        "@type": "xsd:string",
        "@value": "$pbkdf2-sha512$t=32768$ISbyCYB0Z2r/00THgkjVTQ$Pua1CJndFkVjOrug6AivfnvU5Q/v3+6Xs+Tb3ybhqf77rlXXlDjE9FkCpXS+f1m0l8+CtkNIkb++Lm+YYcPrig",
    },
    "terminus:agent_name": {"@type": "xsd:string", "@value": "admin"},
    "terminus:authority": {
        "@id": "doc:access_all_areas",
        "@type": "terminus:ServerCapability",
        "rdfs:comment": {"@language": "en", "@value": "Access all server functions"},
        "rdfs:label": {"@language": "en", "@value": "All Capabilities"},
        "terminus:access": {
            "@id": "doc:server_access",
            "@type": "terminus:Access",
            "terminus:action": [
                {"@id": "terminus:class_frame", "@type": "terminus:DBAction"},
                {"@id": "terminus:create_database", "@type": "terminus:DBAction"},
                {"@id": "terminus:create_document", "@type": "terminus:DBAction"},
                {"@id": "terminus:delete_database", "@type": "terminus:DBAction"},
                {"@id": "terminus:delete_document", "@type": "terminus:DBAction"},
                {"@id": "terminus:get_document", "@type": "terminus:DBAction"},
                {"@id": "terminus:get_schema", "@type": "terminus:DBAction"},
                {"@id": "terminus:read_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:update_document", "@type": "terminus:DBAction"},
                {"@id": "terminus:update_schema", "@type": "terminus:DBAction"},
                {"@id": "terminus:write_access", "@type": "terminus:DBAction"},
            ],
            "terminus:authority_scope": [
                {
                    "@id": "doc:Database%5fadmin%7CTEST",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "TEST"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "TEST"},
                        {"@language": "en", "@value": "admin|TEST"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|TEST",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cbike",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "bike desc"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|bike"},
                        {"@language": "en", "@value": "bike test"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|bike",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Ctesting123",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "thsi is a"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|testing123"},
                        {"@language": "en", "@value": "this is a test"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|testing123",
                    },
                },
                {
                    "@id": "doc:Database%5ffalse%7Cadfadsf",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "asdf"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "asdf"},
                        {"@language": "en", "@value": "false|adfadsf"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "false|adfadsf",
                    },
                },
                {
                    "@id": "doc:terminus",
                    "@type": "terminus:Database",
                    "rdfs:comment": {
                        "@language": "en",
                        "@value": "The master database contains the meta-data about databases, users and roles",
                    },
                    "rdfs:label": {"@language": "en", "@value": "Master Database"},
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "terminus",
                    },
                },
                {
                    "@id": "doc:server",
                    "@type": "terminus:Server",
                    "rdfs:comment": {
                        "@language": "en",
                        "@value": "The current Database Server itself",
                    },
                    "rdfs:label": {"@language": "en", "@value": "The DB server"},
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:resource_includes": [
                        {
                            "@id": "doc:Database%5fadmin%7CTEST",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cbike",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Ctesting123",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5ffalse%7Cadfadsf",
                            "@type": "terminus:Database",
                        },
                        {"@id": "doc:terminus", "@type": "terminus:Database"},
                    ],
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "http://195.201.12.87:6380",
                    },
                },
            ],
        },
    },
}
