WoqlSelect = {
    "jsonObj": {
        "@type": "Select",
        "variables": ["V1"],
        "query": {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "a"},
            "predicate": {"@type": "NodeValue", "node": "b"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "c"},
            },
        },
    },
    "jsonObjMulti": {
        "@type": "Select",
        "variable_list": ["V1", "V2"],
        "query": {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "a"},
            "predicate": {"@type": "NodeValue", "node": "b"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "c"},
            },
        },
    },
}
