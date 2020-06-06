WOQL_JOIN_SPLIT_JSON = {
    "joinJson": {
        "@type": "woql:Join",
        "woql:join_list": {
            "@type": "woql:Array",
            "woql:array_element": [
                {
                    "@type": "woql:ArrayElement",
                    "woql:variable_name": {"@value": "A_obj", "@type": "xsd:string"},
                    "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                },
                {
                    "@type": "woql:ArrayElement",
                    "woql:variable_name": {"@value": "B_obj", "@type": "xsd:string"},
                    "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                },
            ],
        },
        "woql:join_separator": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:string", "@value": ", "},
        },
        "woql:join": {
            "@type": "woql:Variable",
            "woql:variable_name": {"@value": "output", "@type": "xsd:string"},
        },
    },
    "splitJson": {
        "@type": "woql:Split",
        "woql:split_string": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:string", "@value": "A, B, C"},
        },
        "woql:split_pattern": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:string", "@value": ", "},
        },
        "woql:split_list": {
            "@type": "woql:Variable",
            "woql:variable_name": {"@value": "list_obj", "@type": "xsd:string"},
        },
    },
}
