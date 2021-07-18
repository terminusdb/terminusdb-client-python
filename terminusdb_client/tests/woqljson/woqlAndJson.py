WOQL_AND_JSON = {
    "@type": "And",
    "and": [
        {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "a"},
            "predicate": {"@type": "NodeValue", "node": "b"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "c"},
            },
        },
        {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "1"},
            "predicate": {"@type": "NodeValue", "node": "2"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "3"},
            },
        },
    ],
}
