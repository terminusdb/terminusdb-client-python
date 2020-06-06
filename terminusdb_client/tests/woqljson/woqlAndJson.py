WOQL_AND_JSON = {
    "@type": "woql:And",
    "woql:query_list": [
        {
            "@type": "woql:QueryListElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
            "woql:query": {
                "@type": "woql:Triple",
                "woql:subject": {"@type": "woql:Node", "woql:node": "doc:a"},
                "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:b"},
                "woql:object": {
                    "@type": "woql:Datatype",
                    "woql:datatype": {"@type": "xsd:string", "@value": "c"},
                },
            },
        },
        {
            "@type": "woql:QueryListElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
            "woql:query": {
                "@type": "woql:Triple",
                "woql:subject": {"@type": "woql:Node", "woql:node": "doc:1"},
                "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:2"},
                "woql:object": {
                    "@type": "woql:Datatype",
                    "woql:datatype": {"@type": "xsd:string", "@value": "3"},
                },
            },
        },
    ],
}
