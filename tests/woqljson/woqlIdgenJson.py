WoqlIdgen = {
    "@type": "woql:IDGenerator",
    "woql:base": {"@type": "woql:Node", "woql:node": "doc:Station"},
    "woql:key_list": {
        "@type": "woql:Array",
        "woql:array_element": [
            {
                "@type": "woql:ArrayElement",
                "woql:variable_name": {"@value": "Start_ID", "@type": "xsd:string"},
                "woql:index": {"@type": "xsd:nonNegativeInteger`", "@value": 0},
            },
            {
                "@type": "woql:ArrayElement",
                "woql:variable_name": {"@value": "End_ID", "@type": "xsd:string"},
                "woql:index": {"@type": "xsd:nonNegativeInteger`", "@value": 1},
            },
        ],
    },
    "woql:uri": {
        "@type": "woql:Variable",
        "woql:variable_name": {"@value": "Start_Station_URL", "@type": "xsd:string"},
    },
}
