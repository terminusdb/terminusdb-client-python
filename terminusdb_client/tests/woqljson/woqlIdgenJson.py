WoqlIdgen = {
    "@type": "woql:IDGenerator",
    "woql:base": {
        "@type": "woql:Datatype",
        "woql:datatype": {"@type": "xsd:string", "@value": "doc:Station"},
    },
    "woql:key_list": {
        "@type": "woql:Array",
        "woql:array_element": {
            "@type": "woql:ArrayElement",
            "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
        },
        "woql:variable_name": {"@type": "xsd:string", "@value": "Start_ID"},
    },
    "woql:uri": {
        "@type": "woql:Variable",
        "woql:variable_name": {"@type": "xsd:string", "@value": "End_ID"},
    },
}
