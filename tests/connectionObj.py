snapCapabilitiesObj={
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
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@id": "doc:admin",
  "@type": "terminus:User",
  "rdfs:comment": {
    "@language": "en",
    "@value": "This is the server super user account"
  },
  "rdfs:label": {
    "@language": "en",
    "@value": "Server Admin User"
  },
  "terminus:agent_key_hash": {
    "@type": "xsd:string",
    "@value": "$pbkdf2-sha512$t=32768$ISbyCYB0Z2r/00THgkjVTQ$Pua1CJndFkVjOrug6AivfnvU5Q/v3+6Xs+Tb3ybhqf77rlXXlDjE9FkCpXS+f1m0l8+CtkNIkb++Lm+YYcPrig"
  },
  "terminus:agent_name": {
    "@type": "xsd:string",
    "@value": "admin"
  },
  "doc:Database%5fadmin%7CTEST": {
    "@id": "doc:Database%5fadmin%7CTEST",
    "@type": "terminus:Database",
    "rdfs:comment": {
      "@language": "en",
      "@value": "TEST"
    },
    "rdfs:label": [
      {
        "@language": "en",
        "@value": "TEST"
      },
      {
        "@language": "en",
        "@value": "admin|TEST"
      }
    ],
    "terminus:allow_origin": {
      "@type": "xsd:string",
      "@value": "*"
    },
    "terminus:database_state": {
      "@id": "terminus:finalized",
      "@type": "terminus:DatabaseState"
    },
    "terminus:resource_name": {
      "@type": "xsd:string",
      "@value": "admin|TEST"
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
  },
  "doc:Database%5fadmin%7Cbike": {
    "@id": "doc:Database%5fadmin%7Cbike",
    "@type": "terminus:Database",
    "rdfs:comment": {
      "@language": "en",
      "@value": "bike desc"
    },
    "rdfs:label": [
      {
        "@language": "en",
        "@value": "admin|bike"
      },
      {
        "@language": "en",
        "@value": "bike test"
      }
    ],
    "terminus:allow_origin": {
      "@type": "xsd:string",
      "@value": "*"
    },
    "terminus:database_state": {
      "@id": "terminus:finalized",
      "@type": "terminus:DatabaseState"
    },
    "terminus:resource_name": {
      "@type": "xsd:string",
      "@value": "admin|bike"
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
  },
  "doc:Database%5fadmin%7Ctesting123": {
    "@id": "doc:Database%5fadmin%7Ctesting123",
    "@type": "terminus:Database",
    "rdfs:comment": {
      "@language": "en",
      "@value": "thsi is a"
    },
    "rdfs:label": [
      {
        "@language": "en",
        "@value": "admin|testing123"
      },
      {
        "@language": "en",
        "@value": "this is a test"
      }
    ],
    "terminus:allow_origin": {
      "@type": "xsd:string",
      "@value": "*"
    },
    "terminus:database_state": {
      "@id": "terminus:finalized",
      "@type": "terminus:DatabaseState"
    },
    "terminus:resource_name": {
      "@type": "xsd:string",
      "@value": "admin|testing123"
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
  },
  "doc:Database%5ffalse%7Cadfadsf": {
    "@id": "doc:Database%5ffalse%7Cadfadsf",
    "@type": "terminus:Database",
    "rdfs:comment": {
      "@language": "en",
      "@value": "asdf"
    },
    "rdfs:label": [
      {
        "@language": "en",
        "@value": "asdf"
      },
      {
        "@language": "en",
        "@value": "false|adfadsf"
      }
    ],
    "terminus:allow_origin": {
      "@type": "xsd:string",
      "@value": "*"
    },
    "terminus:database_state": {
      "@id": "terminus:finalized",
      "@type": "terminus:DatabaseState"
    },
    "terminus:resource_name": {
      "@type": "xsd:string",
      "@value": "false|adfadsf"
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
  },
  "doc:terminus": {
    "@id": "doc:terminus",
    "@type": "terminus:Database",
    "rdfs:comment": {
      "@language": "en",
      "@value": "The master database contains the meta-data about databases, users and roles"
    },
    "rdfs:label": {
      "@language": "en",
      "@value": "Master Database"
    },
    "terminus:allow_origin": {
      "@type": "xsd:string",
      "@value": "*"
    },
    "terminus:resource_name": {
      "@type": "xsd:string",
      "@value": "terminus"
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
  },
  "doc:server": {
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
}
