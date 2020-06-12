ConnectResponse = {
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
        "@value": "$pbkdf2-sha512$t=32768$b7+2Xn5XkuluDASL34WSlg$eORRJ0QzUGa5ET5BRFOd06NmX7hIvU6cWp86zLdMB0Sgu6YMhR2XT3ayL1cDaBs+5EhOPqAKp2BitYvqIsVldA",
    },
    "terminus:agent_name": {"@type": "xsd:string", "@value": "admin"},
    "terminus:authority": {
        "@id": "doc:access_all_areas",
        "@type": "terminus:Capability",
        "rdfs:comment": {"@language": "en", "@value": "Access all server functions"},
        "rdfs:label": {"@language": "en", "@value": "All Capabilities"},
        "terminus:access": {
            "@id": "doc:server_access",
            "@type": "terminus:Access",
            "terminus:action": [
                {"@id": "terminus:branch", "@type": "terminus:DBAction"},
                {"@id": "terminus:class_frame", "@type": "terminus:DBAction"},
                {"@id": "terminus:clone", "@type": "terminus:DBAction"},
                {"@id": "terminus:commit_read_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:commit_write_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:create_database", "@type": "terminus:DBAction"},
                {"@id": "terminus:delete_database", "@type": "terminus:DBAction"},
                {"@id": "terminus:fetch", "@type": "terminus:DBAction"},
                {"@id": "terminus:inference_read_access", "@type": "terminus:DBAction"},
                {
                    "@id": "terminus:inference_write_access",
                    "@type": "terminus:DBAction",
                },
                {"@id": "terminus:instance_read_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:instance_write_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:manage", "@type": "terminus:DBAction"},
                {"@id": "terminus:meta_read_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:meta_write_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:push", "@type": "terminus:DBAction"},
                {"@id": "terminus:rebase", "@type": "terminus:DBAction"},
                {"@id": "terminus:schema_read_access", "@type": "terminus:DBAction"},
                {"@id": "terminus:schema_write_access", "@type": "terminus:DBAction"},
            ],
            "terminus:authority_scope": [
                {
                    "@id": "doc:Database%5fadmin%7C5534534",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "345345"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "3453"},
                        {"@language": "en", "@value": "admin|5534534"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|5534534",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Caaaaaa",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "dasdasdds"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|aaaaaa"},
                        {"@language": "en", "@value": "dadsds"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|aaaaaa",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cadsasasddsa",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "asdsadsda"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|adsasasddsa"},
                        {"@language": "en", "@value": "asdasdasd"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|adsasasddsa",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cblah",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "adfadf"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|blah"},
                        {"@language": "en", "@value": "better freaking work"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|blah",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cdaassd",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "asdasdsd"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|daassd"},
                        {"@language": "en", "@value": "asdsd"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|daassd",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cdassadds",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "asdsdsad"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|dassadds"},
                        {"@language": "en", "@value": "asdasdds"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|dassadds",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cddd",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "ddds"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|ddd"},
                        {"@language": "en", "@value": "ddd"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|ddd",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cffff",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "fffff"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|ffff"},
                        {"@language": "en", "@value": "fff"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|ffff",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cfffffff",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "fff"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|fffffff"},
                        {"@language": "en", "@value": "fffasdfasdf"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|fffffff",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Cggggggggg",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "gg"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|ggggggggg"},
                        {"@language": "en", "@value": "gg"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|ggggggggg",
                    },
                },
                {
                    "@id": "doc:Database%5fadmin%7Ctwretwert",
                    "@type": "terminus:Database",
                    "rdfs:comment": {"@language": "en", "@value": "adfadf"},
                    "rdfs:label": [
                        {"@language": "en", "@value": "admin|twretwert"},
                        {"@language": "en", "@value": "dgsdfgsg"},
                    ],
                    "terminus:allow_origin": {"@type": "xsd:string", "@value": "*"},
                    "terminus:database_state": {
                        "@id": "terminus:finalized",
                        "@type": "terminus:DatabaseState",
                    },
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "admin|twretwert",
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
                            "@id": "doc:Database%5fadmin%7C5534534",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Caaaaaa",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cadsasasddsa",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cblah",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cdaassd",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cdassadds",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cddd",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cffff",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cfffffff",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Cggggggggg",
                            "@type": "terminus:Database",
                        },
                        {
                            "@id": "doc:Database%5fadmin%7Ctwretwert",
                            "@type": "terminus:Database",
                        },
                        {"@id": "doc:terminus", "@type": "terminus:Database"},
                    ],
                    "terminus:resource_name": {
                        "@type": "xsd:string",
                        "@value": "http://localhost:6363",
                    },
                },
            ],
        },
    },
}
