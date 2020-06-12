WOQL_CONCAT_JSON = {
    "@type": "woql:Concatenate",
    "woql:concat_list": {
        "@type": "woql:Array",
        "woql:array_element": [
            {
                "@type": "woql:ArrayElement",
                "woql:variable_name": {"@value": "Duration", "@type": "xsd:string"},
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
            },
            {
                "@type": "woql:ArrayElement",
                "woql:datatype": {"@type": "xsd:string", "@value": " yo "},
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
            },
            {
                "@type": "woql:ArrayElement",
                "woql:variable_name": {
                    "@value": "Duration_Cast",
                    "@type": "xsd:string",
                },
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
            },
        ],
    },
    "woql:concatenated": {
        "@type": "woql:Variable",
        "woql:variable_name": {"@type": "xsd:string", "@value": "x"},
    },
}
