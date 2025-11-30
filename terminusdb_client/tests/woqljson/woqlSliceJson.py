"""Expected JSON output for WOQL slice operator tests"""

WOQL_SLICE_JSON = {
    "basicSlice": {
        "@type": "Slice",
        "list": {
            "@type": "DataValue",
            "list": [
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "a"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "b"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "c"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "d"}},
            ],
        },
        "result": {"@type": "DataValue", "variable": "Result"},
        "start": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 1}},
        "end": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 3}},
    },
    "negativeIndices": {
        "@type": "Slice",
        "list": {
            "@type": "DataValue",
            "list": [
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "a"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "b"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "c"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "d"}},
            ],
        },
        "result": {"@type": "DataValue", "variable": "Result"},
        "start": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": -2}},
        "end": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": -1}},
    },
    "withoutEnd": {
        "@type": "Slice",
        "list": {
            "@type": "DataValue",
            "list": [
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "a"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "b"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "c"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "d"}},
            ],
        },
        "result": {"@type": "DataValue", "variable": "Result"},
        "start": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 1}},
        # Note: no 'end' property when end is omitted
    },
    "variableList": {
        "@type": "Slice",
        "list": {"@type": "DataValue", "variable": "MyList"},
        "result": {"@type": "DataValue", "variable": "Result"},
        "start": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 0}},
        "end": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 2}},
    },
    "variableIndices": {
        "@type": "Slice",
        "list": {
            "@type": "DataValue",
            "list": [
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "x"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "y"}},
                {"@type": "DataValue", "data": {"@type": "xsd:string", "@value": "z"}},
            ],
        },
        "result": {"@type": "DataValue", "variable": "Result"},
        "start": {"@type": "DataValue", "variable": "Start"},
        "end": {"@type": "DataValue", "variable": "End"},
    },
    "emptyList": {
        "@type": "Slice",
        "list": {"@type": "DataValue", "list": []},
        "result": {"@type": "DataValue", "variable": "Result"},
        "start": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 0}},
        "end": {"@type": "DataValue", "data": {"@type": "xsd:integer", "@value": 1}},
    },
}
