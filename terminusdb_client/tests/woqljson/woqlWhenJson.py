WOQL_WHEN_JSON = {
    "@type": "When",
    "query": {"@type": "True"},
    "consequent": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "id"},
        "predicate": {"@type": "NodeValue", "node": "rdf:type"},
        "object": {"@type": "Value", "node": "owl:Class"},
        "graph": "schema",
    },
}
