WOQL_IDGEN_JSON = {
    "@type": "woql:IDGenerator",
    "woql:base": {"@type": "woql:Node", "woql:node": "doc:Station"},
    "woql:key_list": {
        "@type": "woql:Array",
        "woql:array_element": [
            {
                "@type": "woql:ArrayElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1 - 1},
                "woql:variable_name": {"@type": "xsd:string", "@value": "Start_ID"},
            }
        ],
    },
    "woql:uri": {
        "@type": "woql:Variable",
        "woql:variable_name": {"@type": "xsd:string", "@value": "Start_Station_URL"},
    },
}
