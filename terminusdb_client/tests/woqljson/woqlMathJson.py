WOQL_MATH_JSON = {
    "divJson": {
        "@type": "Div",
        "left": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 2},
        },
        "right": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
    },
    "minusJson": {
        "@type": "Minus",
        "left": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
        "right": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
    },
    "evalJson": {
        "@type": "Eval",
        "expression": {
            "@type": "Plus",
            "left": {
                "@type": "ArithmeticValue",
                "data": {"@type": "xsd:decimal", "@value": 1},
            },
            "right": {
                "@type": "ArithmeticValue",
                "data": {"@type": "xsd:decimal", "@value": 2},
            },
        },
        "result": {
            "@type": "ArithmeticValue",
            "variable": "x",
        },
    },
    "plusJson": {
        "@type": "Plus",
        "left": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 2},
        },
        "right": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
    },
    "timesJson": {
        "@type": "Times",
        "left": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 2},
        },
        "right": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
    },
    "divideJson": {
        "@type": "Divide",
        "left": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 2},
        },
        "right": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
    },
    "expJson": {
        "@type": "Exp",
        "left": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 2},
        },
        "right": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 1},
        },
    },
    "floorJson": {
        "@type": "Floor",
        "argument": {
            "@type": "ArithmeticValue",
            "data": {"@type": "xsd:decimal", "@value": 2.5},
        },
    },
}
