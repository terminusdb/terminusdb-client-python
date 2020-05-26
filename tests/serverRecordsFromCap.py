serverRecordsFromCap={
    "@id": "doc:server",
    "@type": "terminus:Server",
    "rdfs:comment": {
        "@language": "en",
        "@value": "The current Database Server itself"
    },
    "rdfs:label": {
        "@language": "en",
        "@value": "The DB server"
    },
    "terminus:allow_origin": {
        "@type": "xsd:string",
        "@value": "*"
    },
    "terminus:resource_includes": [
        {
            "@id": "doc:Database%5fadmin%7CTEST",
            "@type": "terminus:Database"
        },
        {
            "@id": "doc:Database%5fadmin%7Cbike",
            "@type": "terminus:Database"
        },
        {
            "@id": "doc:Database%5fadmin%7Ctesting123",
            "@type": "terminus:Database"
        },
        {
            "@id": "doc:Database%5ffalse%7Cadfadsf",
            "@type": "terminus:Database"
        },
        {
            "@id": "doc:terminus",
            "@type": "terminus:Database"
        }
    ],
    "terminus:resource_name": {
        "@type": "xsd:string",
        "@value": "http://195.201.12.87:6380"
    },
    "terminus:authority": [
        "terminus:class_frame",
        "terminus:create_database",
        "terminus:create_document",
        "terminus:delete_database",
        "terminus:delete_document",
        "terminus:get_document",
        "terminus:get_schema",
        "terminus:read_access",
        "terminus:update_document",
        "terminus:update_schema",
        "terminus:write_access"
    ]
}
