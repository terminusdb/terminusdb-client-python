WOQL_STAR = {
    "@type": "Triple",
    "object": {
        "@type": "Value",
        "variable": "Object",
    },
    "predicate": {"@type": "NodeValue", "variable": "Predicate"},
    "subject": {"@type": "NodeValue", "variable": "Subject"},
}

WOQL_JSON = {
    "quadJson": {
        "@type": "Triple",
        "subject": {"@type": "NodeValue", "node": "a"},
        "predicate": {"@type": "NodeValue", "node": "b"},
        "object": {
            "@type": "Value",
            "node": "c",
        },
        "graph": "d",
    },
    "tripleJson": {
        "@type": "Triple",
        "subject": {"@type": "NodeValue", "node": "a"},
        "predicate": {"@type": "NodeValue", "node": "b"},
        "object": {
            "@type": "Value",
            "node": "c",
        },
    },
    "getJson": {
        "@type": "Get",
        "columns": [
            {
                "@type": "Column",
                "indicator": {"@type": "Indicator", "name": "M"},
                "variable": "a",
                "type": "p",
            }
        ],
        "resource": "Target",
    },
    "memberJson": {
        "@type": "Member",
        "member": {"@type": "Value", "variable": "member"},
        "list": {"@type": "Value", "variable": "list_obj"},
    },
    "groupbyJson": {
        "@type": "GroupBy",
        "group_by": ["A", "B"],
        "template": ["C"],
        "grouped": {"@type": "Value", "variable": "New"},
        "query": {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "variable": "A"},
            "predicate": {"@type": "NodeValue", "variable": "B"},
            "object": {"@type": "Value", "variable": "C"},
        },
    },
    "addClassJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "id"},
        "predicate": {"@type": "NodeValue", "node": "rdf:type"},
        "object": {"@type": "Value", "node": "owl:Class"},
        "graph": "schema",
    },
    "subsumptionJson": {
        "@type": "Subsumption",
        "parent": {"@type": "NodeValue", "node": "ClassA"},
        "child": {"@type": "NodeValue", "node": "ClassB"},
    },
    "orderbyJson": {
        "@type": "OrderBy",
        "query": WOQL_STAR,
        "ordering": [
            {"@type": "OrderTemplate", "order": "asc", "variable": "A"},
            {"@type": "OrderTemplate", "order": "asc", "variable": "B"},
            {"@type": "OrderTemplate", "order": "asc", "variable": "C"},
        ],
    },
    "isAJson": {
        "@type": "IsA",
        "element": {"@type": "NodeValue", "node": "instance"},
        "type": {"@type": "NodeValue", "node": "Class"},
    },
    "deleteTripleJson": {
        "@type": "DeleteTriple",
        "subject": {"@type": "NodeValue", "node": "a"},
        "predicate": {"@type": "NodeValue", "node": "b"},
        "object": {
            "@type": "Value",
            "node": "c",
        },
    },
    "deleteQuadJson": {
        "@type": "DeleteTriple",
        "subject": {"@type": "NodeValue", "node": "a"},
        "predicate": {"@type": "NodeValue", "node": "b"},
        "object": {
            "@type": "Value",
            "node": "c",
        },
        "graph": "d",
    },
    "addTripleJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "a"},
        "predicate": {"@type": "NodeValue", "node": "b"},
        "object": {
            "@type": "Value",
            "node": "c",
        },
    },
    "addQuadJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "a"},
        "predicate": {"@type": "NodeValue", "node": "b"},
        "object": {
            "@type": "Value",
            "node": "c",
        },
        "graph": "d",
    },
    "addPropertyJson": {
        "@type": "And",
        "and": [
            {
                "@type": "AddTriple",
                "subject": {
                    "@type": "NodeValue",
                    "node": "some_property",
                },
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {
                    "@type": "Value",
                    "node": "owl:DataValueProperty",
                },
                "graph": "schema",
            },
            {
                "@type": "AddTriple",
                "subject": {
                    "@type": "NodeValue",
                    "node": "some_property",
                },
                "predicate": {"@type": "NodeValue", "node": "rdfs:range"},
                "object": {"@type": "Value", "node": "xsd:string"},
                "graph": "schema",
            },
        ],
    },
    "deletePropertyJson": {
        "@type": "And",
        "and": [
            {
                "@type": "DeleteTriple",
                "subject": {
                    "@type": "NodeValue",
                    "node": "some_property",
                },
                "predicate": {"@type": "NodeValue", "variable": "All"},
                "object": {"@type": "Value", "variable": "Al2"},
                "graph": "string",
            },
            {
                "@type": "DeleteTriple",
                "subject": {"@type": "Value", "variable": "Al3"},
                "predicate": {"@type": "Value", "variable": "Al4"},
                "object": {
                    "@type": "Value",
                    "node": "some_property",
                },
                "graph": "string",
            },
        ],
    },
    "graphMethodJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "x"},
        "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
        "object": {
            "@type": "Value",
            "data": {
                "@value": "my label",
                "@type": "xsd:string",
                "@language": "en",
            },
        },
        "graph": "schema",
    },
    "labelMethodJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "x"},
        "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
        "object": {
            "@type": "Value",
            "data": {
                "@value": "my label",
                "@type": "xsd:string",
                "@language": "en",
            },
        },
        "graph": "schema",
    },
    "labelMethodJson2": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "x"},
        "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
        "object": {"@type": "Value", "variable": "label"},
        "graph": "schema",
    },
    "addClassDescJson": {
        "@type": "And",
        "and": [
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "NewClass"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "node": "owl:Class"},
                "graph": "schema",
            },
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "NewClass"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:comment",
                },
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "A new class object.",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
        ],
    },
    "addNodePropJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "x"},
        "predicate": {"@type": "NodeValue", "node": "myprop"},
        "object": {
            "@type": "DataValue",
            "data": {"@type": "xsd:string", "@value": "value"},
        },
    },
    "nodeParentJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "x"},
        "predicate": {"@type": "NodeValue", "node": "rdfs:subClassOf"},
        "object": {"@type": "Value", "node": "classParentName"},
        "graph": "schema",
    },
    "nodeAbstractJson": {
        "@type": "AddTriple",
        "subject": {"@type": "NodeValue", "node": "x"},
        "predicate": {"@type": "NodeValue", "node": "terminus:tag"},
        "object": {"@type": "Value", "node": "terminus:abstract"},
        "graph": "schema",
    },
}
