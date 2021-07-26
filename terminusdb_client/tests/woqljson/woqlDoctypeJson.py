WoqlDoctype = {
    "@type": "And",
    "and": [
        {
            "@type": "AddTriple",
            "subject": {"@type": "NodeValue", "node": "Station"},
            "predicate": {"@type": "NodeValue", "node": "rdf:type"},
            "object": {"@type": "Value", "node": "owl:Class"},
            "graph": "schema",
        },
        {
            "@type": "AddTriple",
            "subject": {"@type": "NodeValue", "node": "Station"},
            "predicate": {
                "@type": "NodeValue",
                "node": "rdfs:subClassOf",
            },
            "object": {"@type": "Value", "node": "terminus:Document"},
            "graph": "schema",
        },
    ],
}
