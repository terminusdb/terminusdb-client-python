WOQL_DELETE_JSON = {
    "@type": "And",
    "and": [
        {
            "@type": "DeleteTriple",
            "subject": {"@type": "NodeValue", "node": "id"},
            "predicate": {"@type": "NodeValue", "variable": "Outgoing"},
            "object": {"@type": "Value", "variable": "Value"},
            "graph": "schema",
        },
        {
            "@type": "Optional",
            "query": {
                "@type": "DeleteTriple",
                "subject": {"@type": "NodeValue", "variable": "Other"},
                "predicate": {"@type": "NodeValue", "variable": "Incoming"},
                "object": {"@type": "Value", "node": "id"},
                "graph": "schema",
            },
        },
    ],
}
