WOQL_MATH_JSON = {
    "divJson": {
        "@type": "woql:Div",
        "woql:first": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2"},
        },
        "woql:second": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "1"},
        },
    },
    "minusJson": {
        "@type": "woql:Minus",
        "woql:first": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2"},
        },
        "woql:second": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "1"},
        },
    },
    "evalJson": {
        "@type": "woql:Eval",
        "woql:expression": "1+2",
        "woql:result": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:string", "@value": "b"},
        },
    },
    "plusJson": {
        "@type": "woql:Plus",
        "woql:first": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2"},
        },
        "woql:second": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "1"},
        },
    },
    "timesJson": {
        "@type": "woql:Times",
        "woql:first": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2"},
        },
        "woql:second": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "1"},
        },
    },
    "divideJson": {
        "@type": "woql:Divide",
        "woql:first": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2"},
        },
        "woql:second": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "1"},
        },
    },
    "expJson": {
        "@type": "woql:Exp",
        "woql:first": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2"},
        },
        "woql:second": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "1"},
        },
    },
    "floorJson": {
        "@type": "woql:Floor",
        "woql:argument": {
            "@type": "woql:Datatype",
            "woql:datatype": {"@type": "xsd:decimal", "@value": "2.5"},
        },
    },
}
