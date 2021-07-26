WOQL_IDGEN_JSON = {
    "@type": "LexicalKey",
    "base": {
        "@type": "DataValue",
        "data": {"@type": "xsd:string", "@value": "Station"},
    },
    "key_list": {"@type": "DataValue", "variable": "Start_ID"},
    "uri": {
        "@type": "NodeValue",
        "variable": "Start_Station_URL",
    },
}

WOQL_UNIQUE_JSON = {
    "@type": "HashKey",
    "base": {
        "@type": "DataValue",
        "data": {"@type": "xsd:string", "@value": "Station"},
    },
    "key_list": {
        "@type": "DataValue",
        "variable": "Start_ID",
    },
    "uri": {
        "@type": "NodeValue",
        "variable": "Start_Station_URL",
    },
}

WOQL_RANDOM_IDGEN_JSON = {
    "@type": "RandomKey",
    "base": {
        "@type": "DataValue",
        "data": {"@type": "xsd:string", "@value": "Station"},
    },
    "key_list": {
        "@type": "DataValue",
        "variable": "Start_ID",
    },
    "uri": {
        "@type": "NodeValue",
        "variable": "Start_Station_URL",
    },
}
