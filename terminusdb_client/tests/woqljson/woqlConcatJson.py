WOQL_CONCAT_JSON = {
    "@type": "Concatenate",
    "list": {"@type" : "DataValue",
             "list" : [
                 {"@type": "DataValue", "variable": "Duration"},
                 {
                     "@type": "DataValue",
                     "data": {"@type": "xsd:string", "@value": " yo "},
                 },
                 {"@type": "DataValue", "variable": "Duration_Cast"},
             ]},
    "result": {"@type": "DataValue", "variable": "x"},
}
