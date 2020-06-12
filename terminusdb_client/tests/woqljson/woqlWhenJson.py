WOQL_WHEN_JSON = {
    "@type": "woql:When",
    "woql:query": {"@type": "woql:True"},
    "woql:consequent": {
        "@type": "woql:AddQuad",
        "woql:subject": {"@type": "woql:Node", "woql:node": "scm:id"},
        "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
        "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
        "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
    },
}
