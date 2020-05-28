WoqlDoctype = {
    "@type": "woql:And",
    "woql:query_list": [
        {
            "@type": "woql:QueryListElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
            "woql:query": {
                "@type": "woql:AddQuad",
                "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
                "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
            },
        },
        {
            "@type": "woql:QueryListElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
            "woql:query": {
                "@type": "woql:AddQuad",
                "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                "woql:predicate": {
                    "@type": "woql:Node",
                    "woql:node": "rdfs:subClassOf",
                },
                "woql:object": {"@type": "woql:Node", "woql:node": "terminus:Document"},
                "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
            },
        },
    ],
}
