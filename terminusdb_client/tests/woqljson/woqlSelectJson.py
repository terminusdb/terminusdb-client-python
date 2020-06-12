WoqlSelect = {
    "jsonObj": {
        "@type": "woql:Select",
        "woql:variable_list": [
            {
                "@type": "woql:VariableListElement",
                "woql:variable_name": {"@value": "V1", "@type": "xsd:string"},
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
            }
        ],
        "woql:query": {
            "@type": "woql:Triple",
            "woql:subject": {"@type": "woql:Node", "woql:node": "doc:a"},
            "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:b"},
            "woql:object": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "c"},
            },
        },
    },
    "jsonObjMulti": {
        "@type": "woql:Select",
        "woql:variable_list": [
            {
                "@type": "woql:VariableListElement",
                "woql:variable_name": {"@value": "V1", "@type": "xsd:string"},
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
            },
            {
                "@type": "woql:VariableListElement",
                "woql:variable_name": {"@value": "V2", "@type": "xsd:string"},
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
            },
        ],
        "woql:query": {
            "@type": "woql:Triple",
            "woql:subject": {"@type": "woql:Node", "woql:node": "doc:a"},
            "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:b"},
            "woql:object": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "c"},
            },
        },
    },
}
