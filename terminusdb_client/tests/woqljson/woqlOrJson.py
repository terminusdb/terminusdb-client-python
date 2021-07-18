WOQL_OR_JSON = {
    "@type": "Or",
    "or": [
        {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "doc:a"},
            "predicate": {"@type": "NodeValue", "node": "scm:b"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "c"},
            },
        },
        {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "doc:1"},
            "predicate": {"@type": "NodeValue", "node": "scm:2"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "3"},
            },
        },
    ],
}
