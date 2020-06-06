WOQL_DELETE_JSON = {
    "@type": "woql:And",
    "woql:query_list": [
        {
            "@type": "woql:QueryListElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
            "woql:query": {
                "@type": "woql:DeleteQuad",
                "woql:subject": {"@type": "woql:Node", "woql:node": "scm:id"},
                "woql:predicate": {
                    "@type": "woql:Variable",
                    "woql:variable_name": {"@value": "Outgoing", "@type": "xsd:string"},
                },
                "woql:object": {
                    "@type": "woql:Variable",
                    "woql:variable_name": {"@value": "Value", "@type": "xsd:string"},
                },
                "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
            },
        },
        {
            "@type": "woql:QueryListElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
            "woql:query": {
                "@type": "woql:Optional",
                "woql:query": {
                    "@type": "woql:DeleteQuad",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Other",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Incoming",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:id"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        },
    ],
}
