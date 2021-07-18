WoqlStar = {
    "@type": "Limit",
    "limit": 10,
    "query": {
        "@type": "Triple",
        "subject": {
            "@type": "NodeValue",
            "variable": "Subject",
        },
        "predicate": {
            "@type": "NodeValue",
            "variable_name": "Predicate",
        },
        "object": {
            "@type": "Value",
            "variable_name": "Object",
        },
    },
}
