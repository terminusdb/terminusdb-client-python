WOQL_JOIN_SPLIT_JSON = {
    "joinJson": {
        "@type": "Join",
        "list": {"@type": "DataValue",
                 "list": [
                     {"@type": "DataValue", "variable": "A_obj"},
                     {"@type": "DataValue", "variable": "B_obj"},
                 ]},
        "separator": {
            "@type": "DataValue",
            "data": {"@type": "xsd:string", "@value": ", "},
        },
        "result": {
            "@type": "DataValue",
            "variable": "output",
        },
    },
    "splitJson": {
        "@type": "Split",
        "string": {
            "@type": "DataValue",
            "data": {"@type": "xsd:string", "@value": "A, B, C"},
        },
        "pattern": {
            "@type": "DataValue",
            "data": {"@type": "xsd:string", "@value": ", "},
        },
        "list": {
            "@type": "DataValue",
            "variable": "list_obj",
        },
    },
}
