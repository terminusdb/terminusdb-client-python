WoqlExtra = {
    "chainAndJson": {
        "@type": "And",
        "and": [
            {
                "@type": "Triple",
                "subject": {"@type": "NodeValue", "variable": "A"},
                "predicate": {"@type": "NodeValue", "variable": "B"},
                "object": {"@type": "Value", "variable": "C"},
            },
            {
                "@type": "Triple",
                "subject": {"@type": "NodeValue", "variable": "D"},
                "predicate": {"@type": "NodeValue", "variable": "E"},
                "object": {"@type": "Value", "variable": "F"},
            },
        ],
    },
    "usingJson": {
        "@type": "Using",
        "collection": "userName/dbName/local/commit/commitID",
        "query": {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "variable": "A"},
            "predicate": {"@type": "NodeValue", "variable": "B"},
            "object": {"@type": "Value", "variable": "C"},
        },
    },
    "multiUsingJson": {
        "@type": "And",
        "and": [
            {
                "@type": "Using",
                "collection": "admin/dbName/local/commit/commitID_1",
                "query": {
                    "@type": "Triple",
                    "subject": {"@type": "NodeValue", "variable": "A"},
                    "predicate": {"@type": "NodeValue", "variable": "B"},
                    "object": {"@type": "Value", "variable": "C"},
                },
            },
            {
                "@type": "Using",
                "collection": "admin/dbName/local/commit/commitID_2",
                "query": {
                    "@type": "Not",
                    "query": {
                        "@type": "Triple",
                        "subject": {"@type": "NodeValue", "variable": "A"},
                        "predicate": {"@type": "NodeValue", "variable": "B"},
                        "object": {"@type": "Value", "variable": "C"},
                    },
                },
            },
        ],
    },
}
